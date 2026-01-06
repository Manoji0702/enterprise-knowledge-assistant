from fastapi import APIRouter
from pydantic import BaseModel

from app.services.retriever import retrieve_similar_chunks
from app.services.llm import generate_answer

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    question: str

@router.post("")
def chat(request: ChatRequest):
    chunks = retrieve_similar_chunks(request.question)

    if not chunks:
        return {
            "question": request.question,
            "answer": "Information not available in the knowledge base.",
            "sources": []
        }

    answer = generate_answer(
        question=request.question,
        context_chunks=chunks
    )

    sources = list({chunk["filename"] for chunk in chunks})

    return {
        "question": request.question,
        "answer": answer,
        "sources": sources
    }
