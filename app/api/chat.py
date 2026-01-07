from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.retriever import retrieve_similar_chunks
from app.services.llm import generate_answer

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

@router.post("/chat")
def chat(request: ChatRequest):
    try:
        chunks = retrieve_similar_chunks(request.question)

        if not chunks:
            return {
                "question": request.question,
                "answer": "Information not available in the knowledge base.",
                "sources": []
            }

        answer = generate_answer(request.question, chunks)

        return {
            "question": request.question,
            "answer": answer,
            "sources": list(set(c["source"] for c in chunks))
        }

    except Exception as e:
        # 👇 THIS IS THE KEY
        print("❌ Chat error:", str(e))
        raise HTTPException(status_code=500, detail="Chat processing failed")
