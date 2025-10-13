"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car

Licensed under the MIT License. See LICENSE file for details.

Landing page redirect to main FastAPI application.
"""

import os
import sys

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    print("🚀 Starting MorningBrief application...")
    print("📍 This script redirects to the main FastAPI application.")
    print("🔄 Use: uvicorn app.main:app --host 0.0.0.0 --port $PORT")
    
    # Import and run the main application
    import uvicorn
    from app.main import app
    
    port = int(os.environ.get("PORT", 8000))
    print(f"🌐 Starting server on port {port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
