from fastapi import APIRouter
import os
import shutil

from app.services.extractor import extract_text
from app.services.chunker import chunk_text
from app.services.embeddings import embed_texts
from app.services.vector_store import VectorStore

SEED_DIR = "app/knowledge/seed"
RAW_DIR = "app/knowledge/raw"
VECTOR_DIR = "app/knowledge/vector_store"

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])

@router.post("/reindex")
def reindex_knowledge():
    # 🔥 Reset vector store
    if os.path.exists(VECTOR_DIR):
        shutil.rmtree(VECTOR_DIR)
    os.makedirs(VECTOR_DIR, exist_ok=True)

    store = VectorStore()
    indexed = 0

    def index_dir(path):
        nonlocal indexed
        for file in os.listdir(path):
            fp = os.path.join(path, file)
            if not os.path.isfile(fp):
                continue

            text = extract_text(fp)
            if not text.strip():
                continue

            chunks = chunk_text(text)
            embeddings = embed_texts(chunks)
            metadata = [{"source": file} for _ in chunks]

            store.add(embeddings, metadata)
            indexed += 1

    index_dir(SEED_DIR)
    index_dir(RAW_DIR)

    return {
        "status": "reindexed",
        "documents_indexed": indexed
    }
