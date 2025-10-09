"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_database
from app.routes.briefing import router as briefing_router
from app.services.scheduler import start_background_scheduler, stop_background_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Daily Briefing application...")
    
    # Validate settings
    if not settings.validate_settings():
        logger.error("Invalid configuration. Please check your environment variables.")
        raise HTTPException(status_code=500, detail="Invalid configuration")
    
    # Initialize database
    await init_database()

    # Start scheduler
    await start_background_scheduler()

    logger.info("Application startup complete!")

    yield

    # Shutdown
    logger.info("Shutting down Daily Briefing application...")
    await stop_background_scheduler()

# Create FastAPI app
app = FastAPI(
    title="Daily Briefing API",
    description="Automated daily news briefings using ChatGPT-4o-mini",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(briefing_router, prefix="/api/v1", tags=["briefing"])

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Daily Briefing API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.APP_HOST}:{settings.APP_PORT}")
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
