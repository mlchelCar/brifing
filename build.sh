#!/bin/bash

# Build script for Render deployment
# Handles dependency installation with fallback options for Python 3.13 compatibility

set -e  # Exit on any error

echo "🚀 Starting MorningBrief build process..."
echo "🐍 Python version: $(python --version)"

# Upgrade pip first
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install greenlet first (critical for SQLAlchemy async)
echo "📦 Installing greenlet (critical for async operations)..."
pip install greenlet==3.1.1

# Try Python 3.13 specific requirements first
echo "📦 Trying Python 3.13 compatible requirements..."
if pip install -r requirements-py313.txt; then
    echo "✅ Successfully installed from requirements-py313.txt"
    # Ensure greenlet is installed even if requirements succeeded
    pip install greenlet==3.1.1
    echo "🎉 Build completed successfully!"
    exit 0
fi

echo "⚠️ Python 3.13 requirements failed, trying individual installation..."

# Install packages individually with Python 3.13 compatible versions
echo "📦 Installing packages with Python 3.13 compatibility..."

# Install greenlet first (critical for SQLAlchemy async)
pip install greenlet==3.1.1

# Core packages first
pip install fastapi==0.104.1
pip install "uvicorn[standard]==0.24.0"
pip install streamlit==1.28.1
pip install openai==1.3.5
pip install requests==2.31.0
pip install python-dotenv==1.0.0
pip install apscheduler==3.10.4
pip install sqlalchemy==2.0.35
pip install aiosqlite==0.19.0

# Install asyncpg with Python 3.13 compatible version
echo "📦 Installing asyncpg with Python 3.13 compatibility..."
if pip install --only-binary=all asyncpg==0.30.0; then
    echo "✅ Successfully installed asyncpg 0.30.0"
elif pip install --only-binary=all asyncpg==0.29.0; then
    echo "✅ Successfully installed asyncpg 0.29.0"
elif pip install --only-binary=all asyncpg==0.28.0; then
    echo "✅ Successfully installed asyncpg 0.28.0"
else
    echo "⚠️ All asyncpg versions failed, trying alternative PostgreSQL driver..."
    # Try psycopg with async support as fallback
    if pip install "psycopg[asyncio]==3.1.18"; then
        echo "✅ Successfully installed psycopg with async support"
    else
        echo "📦 Using psycopg2-binary only (sync operations)"
    fi
fi

# Install psycopg2-binary with Python 3.13 compatibility
echo "📦 Installing psycopg2-binary..."
if pip install --only-binary=all psycopg2-binary==2.9.10; then
    echo "✅ Successfully installed psycopg2-binary 2.9.10"
elif pip install --only-binary=all psycopg2-binary==2.9.9; then
    echo "✅ Successfully installed psycopg2-binary 2.9.9"
else
    echo "⚠️ psycopg2-binary failed, trying psycopg3 as alternative..."
    pip install "psycopg[binary]==3.1.18"
fi

# Install pydantic with compatible version
echo "📦 Installing pydantic..."
if pip install --only-binary=all pydantic==2.8.2; then
    echo "✅ Successfully installed pydantic 2.8.2"
elif pip install --only-binary=all pydantic==2.4.2; then
    echo "✅ Successfully installed pydantic 2.4.2"
else
    pip install pydantic==2.3.0
    echo "✅ Successfully installed pydantic 2.3.0"
fi

# Install remaining packages
pip install httpx==0.25.2
pip install python-multipart==0.0.6
pip install python-telegram-bot==20.7

echo "🎉 Build completed successfully!"
