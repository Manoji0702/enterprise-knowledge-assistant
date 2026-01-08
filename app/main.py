import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from prometheus_client import Counter, Histogram, make_asgi_app

from app.api.upload import router as upload_router
from app.api.chat import router as chat_router
from app.api.reindex import router as reindex_router
from app.api.admin import router as admin_router

from app.services.extractor import extract_text
from app.services.chunker import chunk_text
from app.services.embeddings import embed_texts
from app.services.vector_store import VectorStore


# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────
SEED_DIR = "app/knowledge/seed"
VECTOR_DIR = "app/knowledge/vector_store"
VECTOR_INDEX = f"{VECTOR_DIR}/index.faiss"

# ─────────────────────────────────────────────
# Create FastAPI app
# ─────────────────────────────────────────────
app = FastAPI(
    title="Enterprise Knowledge Assistant",
    version="1.0.0"
)


# ─────────────────────────────────────────────
# Metrics endpoint
# ─────────────────────────────────────────────
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# ─────────────────────────────────────────────
# Static Web UI
# ─────────────────────────────────────────────
app.mount("/ui", StaticFiles(directory="web", html=True), name="web")

@app.get("/")
def user_ui():
    return FileResponse("web/user.html")

@app.get("/admin-ui")
def admin_ui():
    return FileResponse("web/admin.html")


# ─────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}


# ─────────────────────────────────────────────
# API Routers
# ─────────────────────────────────────────────
app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(reindex_router)
app.include_router(admin_router)


# ─────────────────────────────────────────────
# Bootstrap knowledge base (ONE TIME)
# ─────────────────────────────────────────────
@app.on_event("startup")
def bootstrap_knowledge_base():
    os.makedirs(SEED_DIR, exist_ok=True)
    os.makedirs(VECTOR_DIR, exist_ok=True)

    if os.path.exists(VECTOR_INDEX):
        print("✅ Vector store already exists. Skipping bootstrap.")
        return

    print("🚀 Bootstrapping knowledge base from seed docs...")
    store = VectorStore()

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
                {"source": filename, "text": chunk}
                for chunk in chunks
            ]

            store.add(embeddings, metadata)
            print(f"✅ Indexed {filename}")

        except Exception as e:
            print(f"❌ Failed to process {filename}: {e}")

    print("🎉 Knowledge base bootstrap complete")
