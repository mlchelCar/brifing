#!/bin/bash

# Build script for Render deployment
# Handles dependency installation with fallback options

set -e  # Exit on any error

echo "🚀 Starting MorningBrief build process..."

# Upgrade pip first
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Try to install from render-optimized requirements first
echo "📦 Installing dependencies from render-optimized requirements..."
if pip install -r requirements-render.txt; then
    echo "✅ Successfully installed from requirements-render.txt"
else
    echo "⚠️ Failed to install from requirements-render.txt, trying fallback..."
    
    # Fallback: Install packages individually with specific versions that work
    echo "📦 Installing packages individually..."
    
    pip install fastapi==0.104.1
    pip install "uvicorn[standard]==0.24.0"
    pip install streamlit==1.28.1
    pip install openai==1.3.5
    pip install requests==2.31.0
    pip install python-dotenv==1.0.0
    pip install apscheduler==3.10.4
    pip install sqlalchemy==2.0.23
    pip install aiosqlite==0.19.0
    
    # Install asyncpg with pre-compiled wheel
    pip install --only-binary=all asyncpg==0.29.0 || pip install asyncpg==0.28.0
    
    # Install psycopg2-binary
    pip install psycopg2-binary==2.9.9
    
    # Install pydantic with compatible version
    pip install --only-binary=all pydantic==2.4.2 || pip install pydantic==2.3.0
    
    pip install httpx==0.25.2
    pip install python-multipart==0.0.6
    pip install python-telegram-bot==20.7
    
    echo "✅ Successfully installed packages individually"
fi

echo "🎉 Build completed successfully!"
