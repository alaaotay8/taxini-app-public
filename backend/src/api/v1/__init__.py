"""
API v1 package placeholder.

This module documents where the versioned (v1) API routers will live.
Keep this file minimal and free of side effects; actual routers should be
implemented in sibling modules within this package (e.g., rides.py, users.py, auth.py).

Suggested layout for v1:
- rides.py   -> APIRouter for ride endpoints (e.g., /api/v1/rides)
- users.py   -> APIRouter for user endpoints (e.g., /api/v1/users)
- auth.py    -> APIRouter for authentication endpoints (e.g., /api/v1/auth)
- payments.py, drivers.py, etc., as the domain grows.

Conventions:
- Each module should expose a top-level `router: fastapi.APIRouter`.
- Mounting is handled by the application setup (e.g., include all v1 routers under `/api/v1`).
- Keep handlers thin; delegate business logic to services in `taxini.services`.

No runtime logic is intentionally included here.
"""

from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .locations import router as locations_router
from .drivers import router as drivers_router
from .riders import router as riders_router
from .admin import router as admin_router
from .tickets import router as tickets_router
from .admin_tickets import router as admin_tickets_router

# Main v1 router
router = APIRouter()
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(locations_router)
router.include_router(drivers_router)
router.include_router(riders_router)
router.include_router(admin_router)
router.include_router(tickets_router)
router.include_router(admin_tickets_router)

__all__ = ["router"]
