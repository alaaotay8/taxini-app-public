from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from src.api.v1 import router as v1_router
from src.db.session import create_db_and_tables
from src.core.security import APIKeyMiddleware, SecurityHeadersMiddleware
from src.core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    # Temporarily disabled: Tables already exist in Supabase
    # create_db_and_tables()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Taxini Backend", 
    version="0.1.0",
    description="Taxini ride-hailing backend API",
    lifespan=lifespan
)

# Security headers (applied first)
app.add_middleware(SecurityHeadersMiddleware)

# Configure CORS - Allow frontend to make requests (environment-based)
allowed_origins = settings.get_allowed_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,  # Enable HttpOnly cookies
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],  # Explicit methods
    allow_headers=["Authorization", "Content-Type", "X-API-Key", "Cookie"],  # Include Cookie header
    expose_headers=["Set-Cookie"],  # Expose Set-Cookie to frontend
    max_age=600,  # Cache preflight for 10 minutes
)

# Add API key middleware for security
app.add_middleware(APIKeyMiddleware)


@app.get("/")
async def root():
    return {"message": "Hello from Taxini Backend"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Mount API v1 under /api/v1
app.include_router(v1_router, prefix="/api/v1")
