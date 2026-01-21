from fastapi import FastAPI
from app.api.architect import router as architect_router

app = FastAPI(title="AI Architecture Designer ML")

app.include_router(architect_router)

@app.get("/")
def root():
    return {"service": "ai-arch-designer-ml", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/version")
def version():
    return {"version": "0.1.0"}
