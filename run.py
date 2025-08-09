import os
from dotenv import load_dotenv
from core.faq_loader import load_all_faqs
from core.index_builder import build_index
from core.gemini_responder import polish_response_with_context

# Load environment variables
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "utils/faq-voice-keys.json"

def main():
    print("📘 Loading FAQs and building index...")
    faqs = load_all_faqs("data")
    index = build_index(faqs)

    print("🤖 Ask me anything about DreamStream!")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        # Run RAG pipeline
        rag_response = index.query(user_input).response

        # Polished answer from Gemini
        polished = polish_response_with_context(user_input, rag_response)
        print(f"Bot: {polished}\n")

if __name__ == "__main__":
    main()
