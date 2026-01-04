import faiss
import os
import pickle
import numpy as np

INDEX_PATH = "app/knowledge/vector_store/index.faiss"
META_PATH = "app/knowledge/vector_store/meta.pkl"

os.makedirs("app/knowledge/vector_store", exist_ok=True)

class VectorStore:
    def __init__(self, dim=1536):
        if os.path.exists(INDEX_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            with open(META_PATH, "rb") as f:
                self.metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(dim)
            self.metadata = []

    def add(self, embeddings, metadatas):
        vectors = np.array(embeddings).astype("float32")
        self.index.add(vectors)
        self.metadata.extend(metadatas)
        faiss.write_index(self.index, INDEX_PATH)
        with open(META_PATH, "wb") as f:
            pickle.dump(self.metadata, f)
