import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

models = genai.list_models()

for model in models:
    print(f"Name: {model.name}")
    print(f"  Description: {model.description}")
    print(f"  Supported generation methods: {model.supported_generation_methods}")
    print()