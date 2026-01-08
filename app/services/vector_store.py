import faiss
import os
import pickle
import numpy as np

VECTOR_DIR = "app/knowledge/vector_store"
INDEX_PATH = os.path.join(VECTOR_DIR, "index.faiss")
META_PATH = os.path.join(VECTOR_DIR, "meta.pkl")

os.makedirs(VECTOR_DIR, exist_ok=True)


class VectorStore:
    def __init__(self, dim: int = 1536):
        self.dim = dim

        if self.exists():
            self.index = faiss.read_index(INDEX_PATH)
            with open(META_PATH, "rb") as f:
                self.metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(dim)
            self.metadata = []

    def exists(self) -> bool:
        return os.path.exists(INDEX_PATH) and os.path.exists(META_PATH)

    # -----------------------------
    # ➕ Add vectors
    # -----------------------------
    def add(self, embeddings, metadatas):
        if not embeddings:
            return

        vectors = np.array(embeddings, dtype="float32")

        # Safety check
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)

        self.index.add(vectors)
        self.metadata.extend(metadatas)
        self.persist()

    # -----------------------------
    # 💾 Persist index + metadata
    # -----------------------------
    def persist(self):
        faiss.write_index(self.index, INDEX_PATH)
        with open(META_PATH, "wb") as f:
            pickle.dump(self.metadata, f)

    # -----------------------------
    # 🔍 Search (USED BY CHAT)
    # -----------------------------
    def search(self, query_embedding, top_k: int = 5):
        if self.index.ntotal == 0:
            return []

        query = np.array(query_embedding, dtype="float32").reshape(1, -1)
        distances, indices = self.index.search(query, top_k)

        results = []
        for idx in indices[0]:
            if idx < len(self.metadata):
                results.append(self.metadata[idx])

        return results

    # -----------------------------
    # 🧹 HARD RESET (USED BY ADMIN)
    # -----------------------------
    def clear(self):
        self.index = faiss.IndexFlatL2(self.dim)
        self.metadata = []

        if os.path.exists(INDEX_PATH):
            os.remove(INDEX_PATH)

        if os.path.exists(META_PATH):
            os.remove(META_PATH)

        print("🧹 Vector store cleared")
