import numpy as np
from app.services.vector_store import VectorStore
from app.services.embeddings import embed_texts

def retrieve_similar_chunks(question, top_k=3):
    store = VectorStore()
    embeddings = embed_texts([question])

    D, I = store.index.search(np.array(embeddings).astype("float32"), top_k)

    results = []
    for idx in I[0]:
        if idx < len(store.metadata):
            results.append(store.metadata[idx])

    return results

