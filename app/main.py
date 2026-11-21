from fastapi import FastAPI

from app import models  # noqa: F401
from app.config import settings
from app.database import Base

app = FastAPI(
    title="Electronic Dean's Office API (Hardened)",
    version="0.2.0",
)


@app.get("/")
def root():
    return {"message": "Electronic Dean's Office API", "environment": settings.ENVIRONMENT}


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "SQLite",
        "tables": len(Base.metadata.tables),
    }
