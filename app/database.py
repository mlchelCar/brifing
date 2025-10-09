"""Database connection and session management."""

import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.models import Base
from app.config import settings

# Create async engine for FastAPI
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://"),
    echo=settings.DEBUG,
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create sync engine for scheduler and other sync operations
sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
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
