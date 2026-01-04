from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
import shutil
import os

from app.services.extractor import extract_text
from app.services.chunker import chunk_text
from app.services.embeddings import embed_texts
from app.services.vector_store import VectorStore

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])

RAW_DIR = "app/knowledge/raw"
PROCESSED_DIR = "app/knowledge/processed"

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".txt", ".md", ".pdf", ".docx"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Generate document ID
    doc_id = str(uuid.uuid4())

    # Save raw file
    raw_path = os.path.join(RAW_DIR, f"{doc_id}_{file.filename}")
    with open(raw_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text
    text = extract_text(raw_path)
    if not text.strip():
        raise HTTPException(status_code=400, detail="No readable text found")

    # Save processed text
    processed_path = os.path.join(PROCESSED_DIR, f"{doc_id}.txt")
    with open(processed_path, "w", encoding="utf-8") as f:
        f.write(text)

    # 🔥 CHUNK + EMBED + INDEX
    chunks = chunk_text(text)
    embeddings = embed_texts(chunks)

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

    return {
        "document_id": doc_id,
        "filename": file.filename,
        "chunks_indexed": len(chunks),
        "status": "uploaded_and_indexed"
    }
