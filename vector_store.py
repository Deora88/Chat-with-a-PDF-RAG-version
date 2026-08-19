"""
Milestone 4 - Embeddings + Vector Store

Loads a local sentence-transformers model, generates embeddings for text
chunks, and stores them in a ChromaDB collection keyed by document_id.
"""

import chromadb
from sentence_transformers import SentenceTransformer

# Load the embedding model once (reused across all requests)
MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

# Persistent ChromaDB client — data survives restarts
chroma_client = chromadb.PersistentClient(path="./chroma_db")


def index_chunks(document_id: str, chunks: list[str]) -> dict:
    """
    Embed all chunks and store them in a ChromaDB collection
    named after the document_id.

    Returns a summary dict with document_id and chunk count.
    """
    # One collection per document — isolates each PDF's chunks
    collection = chroma_client.get_or_create_collection(name=document_id)

    # Generate embeddings for all chunks at once (batch is faster)
    embeddings = model.encode(chunks).tolist()

    # ChromaDB needs unique IDs for each entry
    ids = [f"chunk_{i}" for i in range(len(chunks))]

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
    )

    return {"document_id": document_id, "num_chunks": len(chunks)}
