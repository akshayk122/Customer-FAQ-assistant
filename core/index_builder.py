from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.schema import TextNode
from llama_index.core.settings import Settings


def build_index(chunks):
    """
    Builds a vector index from parsed FAQ chunks.
    Each chunk should contain: 'question', 'answer', 'source', and 'doc_id'.
    Falls back to defaults if optional metadata is missing.
    """
    nodes = []

    for i, chunk in enumerate(chunks):
        question = chunk.get("question", f"Untitled Question {i}")
        answer = chunk.get("answer", "No answer provided.")
        source = chunk.get("source", "unknown")
        doc_id = chunk.get("doc_id", f"doc_{i}")

        text = f"{question}\n{answer}"

        node = TextNode(
            text=text,
            metadata={
                "question": question,
                "source": source,
                "doc_id": doc_id
            }
        )
        nodes.append(node)

    # Set embedding model
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    Settings.embed_model = embed_model
    Settings.llm = None  # Disable LLM-based reasoning, just use embedding

    # Build vector index and return query engine
    index = VectorStoreIndex(nodes)
    return index.as_query_engine()