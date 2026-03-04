"""FastAPI main application for UniThrive.

This is the entry point for the UniThrive backend API.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.routers import (
    auth, checkins, dashboard, ai_assistant, wellbeing_rings,
    mental_ring, psychological_ring, physical_ring
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Data directory: {settings.data_dir}")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="UniThrive - AI-powered student wellbeing platform with 3-Ring tracking",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(checkins.router, prefix="/api/checkins", tags=["Check-ins"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(ai_assistant.router, prefix="/api/ai", tags=["AI Assistants"])
app.include_router(wellbeing_rings.router, prefix="/api/rings", tags=["Wellbeing Rings"])

# Ring submodules
app.include_router(mental_ring.router, prefix="/api/mental-ring", tags=["Mental Ring"])
app.include_router(psychological_ring.router, prefix="/api/psychological-ring", tags=["Psychological Ring"])
app.include_router(physical_ring.router, prefix="/api/physical-ring", tags=["Physical Ring"])


@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs_url": "/docs",
        "endpoints": {
            "auth": "/api/auth",
            "checkins": "/api/checkins",
            "dashboard": "/api/dashboard",
            "ai": "/api/ai",
            "rings": "/api/rings",
            "mental_ring": "/api/mental-ring",
            "psychological_ring": "/api/psychological-ring",
            "physical_ring": "/api/physical-ring"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.app_name}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
