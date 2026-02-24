from fastapi import FastAPI

from app.api.architect import router as architect_router
from app.api.ml import router as ml_router  # <-- REQUIRED

app = FastAPI(title="AI Architecture Designer ML")

app.include_router(architect_router)
app.include_router(ml_router)  # <-- REQUIRED


@app.get("/")
def root():
    return {"service": "ai-arch-designer-ml", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/version")
def version():
    return {"version": "0.1.0"}
