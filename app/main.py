from fastapi import FastAPI

from app import models  # noqa: F401
from app.auth.router import router as auth_router
from app.config import settings
from app.database import Base
from app.routes.admin import router as admin_router
from app.routes.students import router as students_router
from app.routes.teachers import router as teachers_router

app = FastAPI(
    title="Electronic Dean's Office API (Hardened)",
    version="0.4.0",
)

app.include_router(auth_router)
app.include_router(students_router)
app.include_router(teachers_router)
app.include_router(admin_router)


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
