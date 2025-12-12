"""
Database session and engine configuration.
"""

from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator, AsyncGenerator
from contextlib import asynccontextmanager
from src.core.settings import settings


# Create sync engine
def get_database_url() -> str:
    """Get database URL, using Supabase PostgreSQL."""
    db_url = settings.get_database_url()
    if not db_url:
        raise ValueError("TAXINI_SUPABASE_DB_URL must be set in environment variables")
    
    # Force IPv4 for Supabase if using db.*.supabase.co hostname
    if "db." in db_url and ".supabase.co" in db_url:
        # Add hostaddr parameter to force IPv4 resolution
        import socket
        try:
            # Extract hostname from URL
            hostname = db_url.split("@")[1].split(":")[0]
            # Get IPv4 address only
            ipv4_addr = socket.getaddrinfo(hostname, None, socket.AF_INET)[0][4][0]
            # Replace hostname with IP in URL
            db_url = db_url.replace(hostname, ipv4_addr)
        except Exception as e:
            print(f"Warning: Could not resolve IPv4 for {hostname}: {e}")
    
    return db_url


engine = create_engine(
    get_database_url(),
    echo=False,  # Set to True for development debugging
    pool_pre_ping=True,
    pool_recycle=300,
    # Optimized PostgreSQL pooling for better performance
    pool_size=10,  # Increased from 5 for better concurrency
    max_overflow=20,  # Increased from 10 for peak load handling
    pool_timeout=30,  # Timeout for getting connection from pool
    connect_args={
        "connect_timeout": 10,
        # Performance optimizations
        "options": "-c statement_timeout=30000"  # 30s query timeout
    }
)

# Create async engine for async operations
async_engine = create_async_engine(
    get_database_url().replace("postgresql://", "postgresql+asyncpg://"),
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
    # Optimized async PostgreSQL pooling
    pool_size=30,  # Increased from 20 for better async concurrency
    max_overflow=10,  # Allow some overflow for burst traffic
    pool_timeout=30
)

# Session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


def get_session() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager to get database session."""
    async with AsyncSessionLocal() as session:
        yield session


def create_db_and_tables():
    """Create database tables."""
    SQLModel.metadata.create_all(engine)
