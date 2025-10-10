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

    # Handle missing DATABASE_URL
    if not db_url or db_url.strip() == "":
        # Default to SQLite for development/testing
        db_url = "sqlite:///./daily_briefing.db"
        print(f"⚠️ DATABASE_URL not set, using default SQLite: {db_url}")

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

# Defer engine creation to avoid import errors at module level
async_engine = None

def get_async_engine():
    """Get or create the async engine."""
    global async_engine
    if async_engine is None:
        try:
            async_engine = create_async_engine(
                get_async_database_url(),
                echo=settings.DEBUG,
                future=True,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=300     # Recycle connections every 5 minutes
            )
        except Exception as e:
            print(f"⚠️ Failed to create async engine: {e}")
            # Fallback to SQLite
            async_engine = create_async_engine(
                "sqlite+aiosqlite:///./daily_briefing.db",
                echo=settings.DEBUG,
                future=True
            )
    return async_engine

# Create async session factory (deferred)
AsyncSessionLocal = None

def get_async_session_factory():
    """Get or create the async session factory."""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        AsyncSessionLocal = async_sessionmaker(
            get_async_engine(),
            class_=AsyncSession,
            expire_on_commit=False
        )
    return AsyncSessionLocal

# Create sync engine for scheduler and other sync operations
def get_sync_database_url():
    """Get the appropriate sync database URL for the environment."""
    db_url = settings.DATABASE_URL

    # Handle missing DATABASE_URL
    if not db_url or db_url.strip() == "":
        # Default to SQLite for development/testing
        db_url = "sqlite:///./daily_briefing.db"
        print(f"⚠️ DATABASE_URL not set, using default SQLite: {db_url}")

    # Handle PostgreSQL for production (Render)
    if db_url.startswith("postgres://"):
        return db_url.replace("postgres://", "postgresql://")

    # Default case (SQLite and PostgreSQL)
    return db_url

# Defer sync engine creation to avoid import errors at module level
sync_engine = None

def get_sync_engine():
    """Get or create the sync engine."""
    global sync_engine
    if sync_engine is None:
        try:
            sync_engine = create_engine(
                get_sync_database_url(),
                echo=settings.DEBUG,
                future=True,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=300     # Recycle connections every 5 minutes
            )
        except Exception as e:
            print(f"⚠️ Failed to create sync engine: {e}")
            # Fallback to SQLite
            sync_engine = create_engine(
                "sqlite:///./daily_briefing.db",
                echo=settings.DEBUG,
                future=True
            )
    return sync_engine

# Create sync session factory (deferred)
SessionLocal = None

def get_sync_session_factory():
    """Get or create the sync session factory."""
    global SessionLocal
    if SessionLocal is None:
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_sync_engine()
        )
    return SessionLocal

async def create_tables():
    """Create database tables."""
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def create_tables_sync():
    """Create database tables synchronously."""
    engine = get_sync_engine()
    Base.metadata.create_all(bind=engine)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get async database session."""
    session_factory = get_async_session_factory()
    async with session_factory() as session:
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
