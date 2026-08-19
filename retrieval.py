"""
Milestone 5 - Retrieval

Given a question, embed it using the same sentence-transformers model,
then query ChromaDB for the most relevant chunks from the document.
"""

from vector_store import chroma_client, model


def retrieve_relevant_chunks(document_id: str, question: str, top_k: int = 5) -> list[str]:
    """
    Find the top_k most semantically similar chunks to the question.

    Returns a list of chunk strings (most relevant first).
    """
    collection = chroma_client.get_collection(name=document_id)

    # Embed the question using the same model used for chunks
    question_embedding = model.encode([question]).tolist()

    # Query ChromaDB for the closest matches
    results = collection.query(
        query_embeddings=question_embedding,
        n_results=top_k,
    )

    # results["documents"] is a list-of-lists (one per query); we have one query
    return results["documents"][0]
