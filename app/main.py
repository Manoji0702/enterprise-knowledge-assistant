from fastapi import FastAPI

app = FastAPI(
    title="Enterprise Knowledge Assistant",
    description="Internal AI-powered knowledge assistant",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "enterprise-knowledge-assistant"
    }
