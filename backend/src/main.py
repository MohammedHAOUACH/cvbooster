"""
CVBooster - FastAPI Backend Application.
ATS-optimized CV generator API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import get_settings
from .database import init_db
from .routers import auth, upload, scraper, cv_engine, templates, files


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    settings = get_settings()
    print(f"Starting {settings.app_name} in {settings.app_env} mode")
    
    # Initialize SQLite database
    init_db()
    
    yield
    print("Shutting down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="ATS-optimized CV generator API",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS
    origins = [origin.strip() for origin in settings.cors_origins.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(auth.router)
    app.include_router(upload.router)
    app.include_router(scraper.router)
    app.include_router(cv_engine.router)
    app.include_router(templates.router)
    app.include_router(files.router)

    # Health check
    @app.get("/health")
    async def health():
        return {"status": "ok", "app": settings.app_name}

    return app


app = create_app()
