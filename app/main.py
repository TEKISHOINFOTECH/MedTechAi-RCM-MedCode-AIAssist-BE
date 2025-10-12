"""
FastAPI application entry point for MedTechAi RCM Assistant.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from config import settings
from app.core import init_db
from app.routes import medical_codes
from app.routes import usecase1
from app.routes import supabase
from app.routes import orchestrator
from app.routes import rcm_api


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    init_db()
    yield
    # Shutdown
    pass


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered medical code validation for healthcare RCM",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Include routers
app.include_router(medical_codes.router)
app.include_router(usecase1.router)
app.include_router(supabase.router)
app.include_router(orchestrator.router)
app.include_router(rcm_api.router)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "https://medtechai-rcm-backend-i2rh.onrender.com",
        "https://medtechai-rcm-backend.onrender.com",
        "https://medtech-ai-rcm-med-code-ai-assist-u.vercel.app",
        "https://yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
)

if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["yourdomain.com", "*.yourdomain.com", "*.onrender.com", "*.render.com"]
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to MedTechAi RCM Assistant",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs" if settings.debug else None
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment
    }

@app.head("/health")
async def health_check_head():
    """Health check endpoint for HEAD requests."""
    return {"status": "healthy"}

@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle CORS preflight requests."""
    return {"message": "OK"}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    # Placeholder for now - will be implemented with prometheus_client
    return {"message": "Metrics endpoint - to be implemented"}


def main():
    """Main function for CLI execution."""
    import uvicorn
    import os
    
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()
