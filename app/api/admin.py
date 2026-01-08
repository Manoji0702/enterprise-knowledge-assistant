from fastapi import APIRouter, HTTPException
from app.services.vector_store import VectorStore
from app.services.extractor import extract_text
from app.services.chunker import chunk_text
from app.services.embeddings import embed_texts
import os

router = APIRouter(prefix="/admin", tags=["Admin"])

SEED_DIR = "app/knowledge/seed"
ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}


@router.post("/reindex")
def reindex_knowledge():
    if not os.path.exists(SEED_DIR):
        raise HTTPException(status_code=400, detail="Seed directory not found")

    store = VectorStore()
    store.clear()

    documents_indexed = 0
    chunks_indexed = 0

    for filename in os.listdir(SEED_DIR):
        path = os.path.join(SEED_DIR, filename)

        if not os.path.isfile(path):
            continue

        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            continue

        try:
            text = extract_text(path)
            if not text.strip():
                continue

            chunks = chunk_text(text)
            embeddings = embed_texts(chunks)

            metadata = [
                {"source": filename, "text": chunk}
                for chunk in chunks
            ]

            store.add(embeddings, metadata)

            documents_indexed += 1
            chunks_indexed += len(chunks)

            print(f"✅ Indexed {filename} ({len(chunks)} chunks)")

        except Exception as e:
            print(f"❌ Failed to index {filename}: {e}")

    return {
        "status": "reindexed",
        "documents_indexed": documents_indexed,
        "chunks_indexed": chunks_indexed
    }
