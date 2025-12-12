"""
API security middleware and utilities.
"""

import logging
import secrets
import hmac
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
from src.core.settings import settings

logger = logging.getLogger(__name__)


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce API key authentication on all requests.

    This middleware intercepts all incoming requests and validates the presence
    and correctness of the X-API-Key header. If the API key is missing or invalid,
    it returns a 401 Unauthorized response.
    """

    def __init__(self, app, exclude_paths: Optional[list] = None):
        """
        Initialize the API key middleware.

        Args:
            app: FastAPI application instance
            exclude_paths: List of path prefixes to exclude from API key validation
                          (e.g., ["/health", "/docs", "/redoc", "/openapi.json"])
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"]

    async def dispatch(self, request: Request, call_next):
        """
        Process each request and validate API key.

        Args:
            request: Incoming FastAPI request
            call_next: Next middleware/request handler in the chain

        Returns:
            Response from the next handler or 401 error response
        """
        # Skip API key validation for CORS preflight OPTIONS requests
        if request.method == "OPTIONS":
            return await call_next(request)

        # Skip API key validation for excluded paths
        for path in self.exclude_paths:
            if request.url.path.startswith(path):
                return await call_next(request)

        # Extract API key from X-API-Key header
        api_key = request.headers.get("x-api-key")

        if not api_key:
            logger.warning(f"Missing X-API-Key header for request: {request.method} {request.url.path}")
            return JSONResponse(
                status_code=401,
                content={"detail": "X-API-Key header is required"}
            )

        # Validate API key against configured key
        if not self._validate_api_key(api_key):
            logger.warning(f"Invalid X-API-Key for request: {request.method} {request.url.path}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid API Key"}
            )

        # API key is valid, proceed with request
        logger.debug(f"Valid API key for request: {request.method} {request.url.path}")
        return await call_next(request)

    def _validate_api_key(self, provided_key: str) -> bool:
        """
        Validate the provided API key against the configured key using constant-time comparison.

        Args:
            provided_key: API key from the request header

        Returns:
            True if the key is valid, False otherwise
        """
        configured_key = settings.api_key
        
        # If no API key is configured, reject all requests
        if not configured_key:
            logger.error("No API key configured in settings")
            return False

        # Use constant-time comparison to prevent timing attacks
        try:
            is_valid = secrets.compare_digest(provided_key, configured_key)
            if not is_valid:
                logger.warning("Invalid API key attempt")
            return is_valid
        except (TypeError, ValueError):
            logger.error("API key comparison error")
            return False


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # Updated CSP to allow Swagger UI CDN and FastAPI resources
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "img-src 'self' data: https://fastapi.tiangolo.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "connect-src 'self' https://cdn.jsdelivr.net"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(self), microphone=(), camera=()"
        
        return response


def validate_api_key_header(api_key: str) -> bool:
    """
    Utility function to validate API key (can be used in dependencies).

    Args:
        api_key: API key to validate

    Returns:
        True if valid, False otherwise
    """
    return APIKeyMiddleware(None)._validate_api_key(api_key)