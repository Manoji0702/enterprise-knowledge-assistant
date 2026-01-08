from app.services.embeddings import embed_texts
from app.services.vector_store import VectorStore


def retrieve_similar_chunks(query: str, k: int = 5):
    store = VectorStore()

    # 1️⃣ Generate embedding for the query
    embeddings = embed_texts([query])
    if not embeddings:
        return []

    query_embedding = embeddings[0]

    # 2️⃣ Use VectorStore search (SAFE)
    results = store.search(
        query_embedding=query_embedding,
        top_k=k
    )

    return results
