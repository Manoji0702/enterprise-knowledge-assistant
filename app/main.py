import os
from fastapi import FastAPI

from app.services.extractor import extract_text
from app.services.chunker import chunk_text
from app.services.embeddings import embed_texts
from app.services.vector_store import VectorStore

from app.api.upload import router as upload_router
from app.api.chat import router as chat_router
from app.api.reindex import router as reindex_router


SEED_DIR = "app/knowledge/seed"
VECTOR_INDEX = "app/knowledge/vector_store/index.faiss"

# ✅ 1. Create app FIRST
app = FastAPI(
    title="Enterprise Knowledge Assistant",
    version="1.0.0"
)

# ✅ 2. Basic endpoints
@app.get("/health")
def health():
    return {"status": "ok"}

# ✅ 3. Include routers AFTER app exists
app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(reindex_router)

# ✅ 4. Startup bootstrap
@app.on_event("startup")
def bootstrap_knowledge_base():
    if os.path.exists(VECTOR_INDEX):
        print("✅ Vector store already initialized. Skipping bootstrap.")
        return

    print("🚀 Bootstrapping knowledge base from repo docs...")
    store = VectorStore()

    if not os.path.exists(SEED_DIR):
        print(f"⚠️ Seed directory not found: {SEED_DIR}")
        return

    for filename in os.listdir(SEED_DIR):
        file_path = os.path.join(SEED_DIR, filename)
        if not os.path.isfile(file_path):
            continue

        try:
            text = extract_text(file_path)
            if not text.strip():
                continue

            chunks = chunk_text(text)
            embeddings = embed_texts(chunks)
            metadata = [
                {
                    "source": filename,
                    "text": chunk
                }
                for chunk in chunks
            ]

            store.add(embeddings, metadata)
            print(f"✅ Indexed {filename}")

        except Exception as e:
            print(f"❌ Failed to process {filename}: {e}")

    print("🎉 Knowledge base bootstrap complete")
