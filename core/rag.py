

from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.schema import TextNode
from llama_index.core.settings import Settings

# Load your pre-built index once globally (build elsewhere)
from core.index_builder import build_index
from core.faq_loader import load_faqs

# Set embedding model
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.llm = None

faq_chunks = load_faqs("data/")
query_engine = build_index(faq_chunks)

def retrieve_faq_chunks(query, top_k=3):
    """Returns top_k relevant nodes from index"""
    results = query_engine.retrieve(query)
    return results[:top_k]
