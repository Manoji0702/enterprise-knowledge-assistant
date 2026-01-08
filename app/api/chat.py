from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.retriever import retrieve_similar_chunks
from app.services.llm import generate_answer
from time import time
from app.metrics import REQUEST_COUNT, CHAT_LATENCY
import traceback

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

@router.post("/chat")
def chat(request: ChatRequest):
    REQUEST_COUNT.labels(endpoint="/chat").inc()

    with CHAT_LATENCY.time():
        try:
            chunks = retrieve_similar_chunks(request.question)

            if not chunks:
                return {
                    "question": request.question,
                    "answer": "Information not available in the knowledge base.",
                    "sources": []
                }

            context = "\n\n".join(
                c.get("text", "") for c in chunks if c.get("text")
            )

            answer = generate_answer(
                question=request.question,
                context=context
            )

            return {
                "question": request.question,
                "answer": answer,
                "sources": list(set(c.get("source", "unknown") for c in chunks))
            }

        except Exception as e:
            print("❌ Chat error:", e)
            raise HTTPException(status_code=500, detail="Chat processing failed")

    
