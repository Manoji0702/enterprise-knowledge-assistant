from fastapi import FastAPI
from app.api.upload import router as upload_router
from app.api.chat import router as chat_router

app = FastAPI(
    title="Enterprise Knowledge Assistant",
    version="1.0.0"
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(upload_router)
app.include_router(chat_router)
