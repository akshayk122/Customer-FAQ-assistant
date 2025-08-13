import io
import os
import time
import wave
import logging
import shutil
from pathlib import Path
from collections import deque

from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Depends, Form
from fastapi.responses import FileResponse, StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from google.cloud import texttospeech
from google.cloud import speech
from google.cloud import secretmanager
from pydantic import BaseModel
from dotenv import load_dotenv

from core.faq_loader import load_all_faqs
from core.index_builder import build_index
from core.gemini_responder import polish_response_with_context

# Set up credentials first for local development
if os.getenv("GAE_ENV", "").startswith("standard") is False:
    # Local development - use local credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "utils/faq-voice-keys.json"
    load_dotenv(".env")  # ✅ add this line to load local .env

def load_secrets_from_secret_manager(secret_id: str, project_id: str):
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        secret_data = response.payload.data.decode("UTF-8")
        load_dotenv(stream=io.StringIO(secret_data))
    except Exception as e:
        print(f"Warning: Could not load secrets from Secret Manager: {e}")
        print("Using local environment variables instead.")

# Only load from Secret Manager in production
if os.getenv("GAE_ENV", "").startswith("standard"):
    load_secrets_from_secret_manager("faq-env-secret", "ai-voice-faq")


# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="AI Voice FAQ Assistant",
    description="Voice assistant using Gemini, Google TTS/STT, and LlamaIndex",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google Cloud clients
tts_client = texttospeech.TextToSpeechClient()
stt_client = speech.SpeechClient()

# Rate limiting
request_counts = {}
MAX_REQUESTS_PER_MINUTE = 5
TIME_WINDOW_SECONDS = 60

async def rate_limit(request: Request):
    ip = request.client.host
    now = time.time()
    timestamps = request_counts.setdefault(ip, deque())
    while timestamps and timestamps[0] < now - TIME_WINDOW_SECONDS:
        timestamps.popleft()
    if len(timestamps) >= MAX_REQUESTS_PER_MINUTE:
        wait = int((timestamps[0] + TIME_WINDOW_SECONDS) - now)
        raise HTTPException(429, f"Rate limit exceeded. Try again in {wait} seconds.")
    timestamps.append(now)

# Load FAQs and build index
faq_data = load_all_faqs("data")
index = build_index(faq_data)

# Core Gemini-enhanced RAG QA function
def get_answer_with_gemini(user_query: str, chat_history: list = None) -> str:
    rag_response = index.query(user_query).response
    return polish_response_with_context(user_query, rag_response, chat_history)

# Audio streaming utility
def stream_audio(audio_bytes):
    buffer = io.BytesIO(audio_bytes)
    while chunk := buffer.read(4096):
        yield chunk

# WAV format utility
def create_wav(raw_audio, sample_rate=24000):
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(raw_audio)
    return buf.getvalue()

# Request schema for text input
class TextRequest(BaseModel):
    text: str
    history: list | None = None

# API: Audio-based question -> answer with TTS
@app.post("/api/ask-audio", dependencies=[Depends(rate_limit)])
async def ask_audio(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(400, "No audio provided")

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        sample_rate_hertz=48000,
        language_code="en-US"
    )
    audio = speech.RecognitionAudio(content=content)
    response = stt_client.recognize(config=config, audio=audio)
    transcript = " ".join([alt.transcript for r in response.results for alt in r.alternatives])

    if not transcript:
        raise HTTPException(400, "No speech detected")

    logger.info(f"Transcribed: {transcript}")
    answer = get_answer_with_gemini(transcript)

    synth_input = texttospeech.SynthesisInput(text=answer)
    voice = texttospeech.VoiceSelectionParams(language_code="en-US", name="en-US-Studio-O")
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16, sample_rate_hertz=24000)
    tts_response = tts_client.synthesize_speech(input=synth_input, voice=voice, audio_config=audio_config)
    wav_data = create_wav(tts_response.audio_content)

    return StreamingResponse(stream_audio(wav_data), media_type="audio/wav")

# API: Text question -> text answer
@app.post("/api/ask-text", dependencies=[Depends(rate_limit)])
async def ask_text(req: TextRequest):
    answer = get_answer_with_gemini(req.text, req.history)
    return {"answer": answer}

# API: Audio -> transcript only
@app.post("/api/ask-text-transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(400, "No audio provided for transcription")

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        sample_rate_hertz=48000,
        language_code="en-US"
    )
    audio = speech.RecognitionAudio(content=content)

    try:
        response = stt_client.recognize(config=config, audio=audio)
        transcript = " ".join([alt.transcript for r in response.results for alt in r.alternatives])
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(500, "Failed to transcribe audio.")

    if not transcript:
        raise HTTPException(400, "No speech detected in audio")

    logger.info(f"Live Transcript: {transcript}")
    return {"transcript": transcript}

# API: Text -> TTS
@app.post("/api/ask-tts")
async def ask_tts(req: TextRequest):
    synth_input = texttospeech.SynthesisInput(text=req.text)
    voice = texttospeech.VoiceSelectionParams(language_code="en-US", name="en-US-Studio-O")
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16, sample_rate_hertz=24000)
    tts_response = tts_client.synthesize_speech(input=synth_input, voice=voice, audio_config=audio_config)
    wav_data = create_wav(tts_response.audio_content)
    return StreamingResponse(io.BytesIO(wav_data), media_type="audio/wav")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "AI Voice FAQ Assistant is running."}

# Dashboard route
@app.get("/dashboard")
async def dashboard():
    return FileResponse("static/dashboard.html")

# File upload route
@app.post("/api/upload-file")
async def upload_file(file: UploadFile = File(...)):
    # Validate file type
    allowed_extensions = {'.docx', '.pdf', '.txt', '.csv', '.json'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(400, f"File type {file_extension} not supported. Allowed: {', '.join(allowed_extensions)}")
    
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Save file to data directory
    file_path = data_dir / file.filename
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Reload FAQs and rebuild index with new file
        global faq_data, index
        faq_data = load_all_faqs("data")
        index = build_index(faq_data)
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "size": file_path.stat().st_size
        }
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(500, "Failed to upload file")

# Get list of uploaded files
@app.get("/api/files")
async def list_files():
    data_dir = Path("data")
    if not data_dir.exists():
        return {"files": []}
    
    files = []
    for file_path in data_dir.iterdir():
        if file_path.is_file():
            files.append({
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime,
                "extension": file_path.suffix.lower()
            })
    
    return {"files": files}

# Delete file route
@app.delete("/api/files/{filename}")
async def delete_file(filename: str):
    data_dir = Path("data")
    file_path = data_dir / filename
    
    if not file_path.exists():
        raise HTTPException(404, "File not found")
    
    try:
        file_path.unlink()
        
        # Reload FAQs and rebuild index after deletion
        global faq_data, index
        faq_data = load_all_faqs("data")
        index = build_index(faq_data)
        
        return {"message": f"File {filename} deleted successfully"}
    except Exception as e:
        logger.error(f"File deletion error: {e}")
        raise HTTPException(500, "Failed to delete file")

# Local dev run
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=True)
