"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car. All rights reserved.

This software is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited.

Main FastAPI application.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
#<<<<<<< fix/landing-page-display
=======
from fastapi.staticfiles import StaticFiles
#>>>>>>> main
from fastapi.responses import FileResponse
from app.config import settings
from app.database import init_database
from app.routes.briefing import router as briefing_router
from app.routes.telegram import router as telegram_router
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
app.include_router(telegram_router, prefix="/telegram", tags=["telegram"])

@app.get("/")
async def root():
    """Serve the landing page."""
    return FileResponse("landing_page.html")

@app.get("/api")
async def api_root():
    """API root endpoint."""
    return {
        "message": "Daily Briefing API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from datetime import datetime
    from app.database import async_engine

    try:
        # Test database connection
        async with async_engine.begin() as conn:
            await conn.execute("SELECT 1")

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0",
            "database": "connected",
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0",
            "database": "disconnected",
            "error": str(e),
            "environment": settings.ENVIRONMENT
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
