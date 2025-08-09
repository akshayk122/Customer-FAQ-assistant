import requests
import json
import os
import dotenv

def polish_response_with_gemini(user_query, rag_response):
    GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
    if not GEMINI_API_KEY:
        raise ValueError("Gemini API key not found.")
    print('GEMINI_API_KEY', GEMINI_API_KEY)
    prompt = f"""
You are an AI assistant for Community Dreams Foundation. A user asked:

Q: {user_query}
A: {rag_response}

Rewrite this in a friendly, helpful tone. Keep it accurate and concise.
"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    print('url', url)
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(url, headers=headers, data=json.dumps(body))
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        print("Gemini Error:", response.text)
        return rag_response
