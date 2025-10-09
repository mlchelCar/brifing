"""Script to run the FastAPI backend server."""

import uvicorn
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.config import settings

if __name__ == "__main__":
    print("🚀 Starting Daily Briefing Backend Server...")
    print(f"   Host: {settings.APP_HOST}")
    print(f"   Port: {settings.APP_PORT}")
    print(f"   Debug: {settings.DEBUG}")
    print(f"   API Documentation: http://{settings.APP_HOST}:{settings.APP_PORT}/docs")
    print("   Press Ctrl+C to stop the server")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
