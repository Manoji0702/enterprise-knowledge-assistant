from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
import shutil
import os

from app.services.extractor import extract_text
from app.services.chunker import chunk_text
from app.services.embeddings import embed_texts
from app.services.vector_store import VectorStore
from app.metrics import UPLOAD_COUNT

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])

RAW_DIR = "app/knowledge/raw"
PROCESSED_DIR = "app/knowledge/processed"

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}"
        )

    doc_id = str(uuid.uuid4())
    raw_path = os.path.join(RAW_DIR, f"{doc_id}_{file.filename}")
    processed_path = os.path.join(PROCESSED_DIR, f"{doc_id}.txt")

    # 1️⃣ Save raw file
    try:
        with open(raw_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # 2️⃣ Extract text
    try:
        text = extract_text(raw_path)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Text extraction failed: {e}"
        )

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="No readable text found in document"
        )

    # 3️⃣ Save processed text
    with open(processed_path, "w", encoding="utf-8") as f:
        f.write(text)

    # 4️⃣ Chunk + embed
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="Document produced no valid chunks"
        )

    embeddings = embed_texts(chunks)

    # 5️⃣ Index into vector store
    store = VectorStore()
    metadata = [
        {
            "document_id": doc_id,
            "filename": file.filename,
            "text": chunk
        }
        for chunk in chunks
    ]

    store.add(embeddings, metadata)

    # ✅ Increment metric ONLY after success
    UPLOAD_COUNT.inc()

    return {
        "status": "uploaded_and_indexed",
        "document_id": doc_id,
        "filename": file.filename,
        "chunks_indexed": len(chunks)
    }
