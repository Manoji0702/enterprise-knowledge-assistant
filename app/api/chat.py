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

        # ✅ BUILD CONTEXT STRING HERE
        context = "\n\n".join(c.get("text", "") for c in chunks)

        answer = generate_answer(request.question, context)

        return {
            "question": request.question,
            "answer": answer,
            "sources": list(set(c.get("source", "unknown") for c in chunks))
        }

    except Exception as e:
        print("❌ Chat error:", str(e))
        raise HTTPException(status_code=500, detail="Chat processing failed")
