"""FastAPI entrypoint."""

from fastapi import FastAPI

from app.api.routes import router
from app.config import settings
from app.database import init_db


app = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(router)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Bilibili Goods API is running",
        "health": "/health",
        "api_health": "/api/health",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
