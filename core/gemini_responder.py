import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL = "models/gemini-2.5-flash"
gemini = genai.GenerativeModel(model_name=MODEL)

def polish_response_with_context(user_query: str, rag_answer: str, chat_history: list[str] = None) -> str:
    """
    Enhance a RAG answer using Gemini 2.5 Flash, incorporating conversational context.
    """

    context = "\n".join(
        [f"User: {turn['user']}\nBot: {turn['bot']}" for turn in chat_history]
    ) if chat_history and isinstance(chat_history, list) and all(isinstance(turn, dict) for turn in chat_history) else "No prior conversation history provided."

    prompt = f"""
You are a smart and friendly assistant for DreamStream, a platform created by the Community Dreams Foundation (CDF) to support career growth, learning, and collaboration.

Your job is to:
- Read the user’s question and the raw answer.
- Write a clear, natural-sounding response that focuses on what the user really wants to know.
- Use the chat history only if it helps make your answer more relevant.
- Don’t copy the raw answer directly. Rewrite it in your own words.
- Skip unnecessary details or formalities.
- If the answer isn’t relevant or clear, ask the user for clarification.

--- CHAT HISTORY ---
{context}

--- USER QUESTION ---
{user_query}

--- RAW FAQ ANSWER ---
{rag_answer}

--- YOUR IMPROVED RESPONSE ---
"""

    try:
        response = gemini.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Sorry, I couldn't improve the answer due to an internal issue: {e}"