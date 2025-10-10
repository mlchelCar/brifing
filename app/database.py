"""
MorningBrief - News Briefing Application
Copyright (c) 2025 Michel Car. All rights reserved.

This software is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited.

Database connection and session management.
"""

import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.models import Base, NewsArticle, TelegramUser
from app.config import settings

# Create async engine for FastAPI
def get_async_database_url():
    """Get the appropriate async database URL for the environment."""
    db_url = settings.DATABASE_URL

    # Handle SQLite for development
    if db_url.startswith("sqlite://"):
        return db_url.replace("sqlite://", "sqlite+aiosqlite://")

    # Handle PostgreSQL for production (Render)
    elif db_url.startswith("postgres://"):
        # Try asyncpg first, fallback to psycopg2 if asyncpg not available
        try:
            import asyncpg
            return db_url.replace("postgres://", "postgresql+asyncpg://")
        except ImportError:
            # Fallback to psycopg2 async (requires psycopg[asyncio])
            return db_url.replace("postgres://", "postgresql+psycopg://")

    # Handle PostgreSQL with asyncpg
    elif db_url.startswith("postgresql://"):
        try:
            import asyncpg
            return db_url.replace("postgresql://", "postgresql+asyncpg://")
        except ImportError:
            # Fallback to psycopg2 async
            return db_url.replace("postgresql://", "postgresql+psycopg://")

    # Default case
    return db_url

async_engine = create_async_engine(
    get_async_database_url(),
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300     # Recycle connections every 5 minutes
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create sync engine for scheduler and other sync operations
def get_sync_database_url():
    """Get the appropriate sync database URL for the environment."""
    db_url = settings.DATABASE_URL

    # Handle PostgreSQL for production (Render)
    if db_url.startswith("postgres://"):
        return db_url.replace("postgres://", "postgresql://")

    # Default case (SQLite and PostgreSQL)
    return db_url

sync_engine = create_engine(
    get_sync_database_url(),
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300     # Recycle connections every 5 minutes
)

# Create sync session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

async def create_tables():
    """Create database tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def create_tables_sync():
    """Create database tables synchronously."""
    Base.metadata.create_all(bind=sync_engine)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def get_sync_session():
    """Get synchronous database session."""
    session = SessionLocal()
    try:
        return session
    finally:
        session.close()

async def init_database():
    """Initialize the database."""
    await create_tables()
    print("Database initialized successfully!")

def init_database_sync():
    """Initialize the database synchronously."""
    create_tables_sync()
    print("Database initialized successfully!")
