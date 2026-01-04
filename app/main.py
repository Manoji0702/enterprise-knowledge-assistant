from fastapi import FastAPI
from app.api.upload import router as upload_router

app = FastAPI(
    title="Enterprise Knowledge Assistant",
    description="Internal AI-powered knowledge assistant",
    version="1.0.0"
)

@app.get("/health")
def health():
    return {"status": "ok"}

# 🔴 THIS LINE IS CRITICAL
app.include_router(upload_router)
