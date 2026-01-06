import numpy as np
from app.services.vector_store import VectorStore
from app.services.embeddings import embed_texts

def retrieve_similar_chunks(query: str, top_k: int = 3):
    store = VectorStore()

    # If no vectors indexed yet
    if store.index.ntotal == 0 or not store.metadata:
        return []

    query_embedding = embed_texts([query])[0]
    query_vector = np.array([query_embedding]).astype("float32")

    distances, indices = store.index.search(query_vector, top_k)

    results = []
    meta_len = len(store.metadata)

    for idx in indices[0]:
        # 🔥 CRITICAL GUARD
        if 0 <= idx < meta_len:
            results.append(store.metadata[idx])

    return results
