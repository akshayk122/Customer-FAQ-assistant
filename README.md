# 🧠 AI Voice FAQ Assistant – Community Dreams Foundation (CDF)

This project is a **voice and chat-based FAQ assistant** built to support teams, volunteers, and newcomers at CDF. It uses advanced AI tools to **read documents, understand common questions, and respond like a helpful human assistant** — all through your browser.

It’s built using the latest technologies from **Google’s AI (Gemini Pro)** and **open-source tools** like FastAPI, LlamaIndex, and HuggingFace embeddings.

Whether you’re a **developer**, a **non-technical team member**, or a **project lead**, this assistant is designed so **anyone can use it**.

---

## ✅ What It Can Do

- 🎤 Understand your spoken questions (mic supported!)
- 💬 Let you type questions instead of speaking
- 📁 Automatically scan `.docx`, `.pdf`, `.txt`, `.csv`, and `.json` FAQ documents
- 🔍 Find the best answer using vector search (semantic similarity)
- 🗣 Speak the answer back using natural-sounding voice
- ✨ Make the response more human-like using Gemini AI (Google)

---

## 🧱 How It Works (Simple Explanation)

```text
Step 1: You ask a question using mic or by typing it
Step 2: The system finds the best-matching content from your documents
Step 3: Gemini AI rewrites that answer to sound natural and friendly
Step 4: You see the response and hear it read out loud if you want
```

This method is called **RAG** – Retrieval-Augmented Generation.

---

## 📁 Folder Structure (Explained for Everyone)

```bash
ai-voice-faq-assistant/
├── api/
│   └── main.py               # 🔥 The main FastAPI server – THIS is what runs the app
├── run.py                   # 🧪 Testing script (for devs only, not needed for regular use)
├── requirements.txt         # List of tools Python will install
├── .env.example             # Template for adding your private keys
├── .env                     # Your actual keys (will be hidden from Git)
├── core/                    # 💡 All the logic for reading files and understanding questions
│   ├── faq_loader.py
│   ├── file_parser.py
│   ├── index_builder.py
│   ├── rag.py
│   └── gemini_responder.py
├── utils/
│   └── faq-voice-keys.json  # 🔐 Google cloud credentials (you download this)
├── static/
│   ├── index.html           # Your chat window
│   └── script.js            # Makes the mic and chat box work
└── data/
    └── DreamStream FAQ.docx # 📄 Your FAQ files go here
```

---

## 🚀 Getting Started (For Everyone)

This section helps both **non-technical and technical** members get it running.

### 1. Install Python (Once)

Go to https://www.python.org/downloads/ and install **Python 3.10 or newer**.

### 2. Download This Project

Ask your team lead for the GitHub link or run this in your terminal:

```bash
git clone https://github.com/your-org/ai-voice-faq-assistant.git
cd ai-voice-faq-assistant
```

### 3. Set Up Python Environment

```bash
python -m venv venv
source venv/bin/activate          # On Windows use: venv\Scripts\activate
```

### 4. Install All Dependencies

```bash
pip install -r requirements.txt
```

### 5. Add Your API Keys

1. Copy the template:

```bash
cp .env.example .env
```

2. Edit the `.env` file and add your **Google Gemini API key**:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

3. Also download your **Google service account key (JSON)** and place it in:

```
utils/faq-voice-keys.json
```

This is needed for voice-to-text and text-to-voice features.

---

## 🗃️ Add Your FAQ Files

You don’t need to code anything.

1. Open the `data/` folder.
2. Drag and drop any `.docx`, `.pdf`, `.csv`, `.txt`, or `.json` file.
3. The assistant will automatically read them the next time you run it.

---

## ▶️ Run the Assistant (Production)

```bash
uvicorn api.main:app --reload
```

Now open your browser and go to:

```
http://localhost:8000
```

- Click the 🎤 mic to ask your question.
- Or type in the input box.
- You'll see and hear the assistant's response.

---

## 🧪 Run for Testing (Developers Only)

For CLI-based testing (no frontend), run:

```bash
python run.py
```

---

## 🧠 API Endpoints (For Developers)

| Method | Endpoint                | Description                          |
|--------|-------------------------|--------------------------------------|
| POST   | `/api/ask-text`         | Ask a question via text              |
| POST   | `/api/ask-audio`        | Ask a question via audio             |
| POST   | `/api/ask-tts`          | Convert text to speech               |
| POST   | `/api/ask-text-transcribe` | Just get a transcript from audio |
| GET    | `/health`               | Check if backend is running          |

---

## 👩‍💻 Team Workflow (For Developers)

```bash
# Create a new feature branch
git checkout -b feature/my-task-name

# Make changes and commit
git add .
git commit -m "Add feature: improve response formatting"

# Push and open pull request
git push origin feature/my-task-name
```

---

## 🛠️ Requirements

- Python 3.10+
- Google API Key (for Gemini)
- Google Cloud Service Account (for TTS/STT)
- Web browser with microphone access

---

## 🔐 Security & Best Practices

- `.env` and key files are ignored in Git and must be set up manually
- Voice input is rate-limited to prevent abuse
- No user data is stored or shared

---
