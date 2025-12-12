"""
Taxini Database package.

This package is intentionally minimal and exists to establish the repository structure.
Do not implement database logic in this file. Instead, add concrete modules under this package
as the backend evolves.

Recommended layout for `taxini.db` (create files/directories when needed):

- session.py
  - Centralize database bootstrap:
    - Create engines (async/sync) for SQLAlchemy 2.x
    - Configure session factories
    - Expose FastAPI dependencies (e.g., `get_session()`) without importing from API layers
  - Read configuration from environment (e.g., `TAXINI_DATABASE_URL`)
  - Keep connection lifecycle management here (connect/close hooks), not in routers

- migrations/
  - Alembic migrations live here
  - Wire Alembic's `env.py` to your SQLAlchemy metadata (typically from `taxini.models`)
  - Use revision scripts to evolve schema safely across environments

- repositories/ (optional)
  - Encapsulate DB access patterns for specific aggregates (e.g., rides, users)
  - Keep them framework-agnostic (no FastAPI/HTTP literals)

- utils.py (optional)
  - Shared DB helpers (pagination, transactional helpers, raw SQL utilities, etc.)

- seed.py / fixtures/ (optional)
  - Seed or fixture data for local development and integration testing

Cross-package conventions (structure only; implemented later):
- taxini.models
  - Domain models (e.g., SQLAlchemy Declarative mappings)
- taxini.schemas
  - Pydantic models for request/response payloads (API contracts)
- taxini.services
  - Business use-cases that orchestrate repositories and models
- taxini.workers
  - Background jobs and task runners (e.g., Celery/RQ/Arq/etc.)

Environment & configuration (suggested, not enforced here):
- TAXINI_DATABASE_URL
  - Example (PostgreSQL): postgresql+psycopg://user:pass@host:5432/taxini
  - Example (SQLite dev): sqlite+aiosqlite:///./.data/taxini.db

Notes:
- Keep `taxini.db` free of API or HTTP concerns; it should be usable by CLI tools, workers, and tests.
- Prefer async drivers for FastAPI (e.g., `postgresql+asyncpg`, `sqlite+aiosqlite`) when running async code.
"""

# Explicitly export nothing at the package root. Concrete modules will be added as the codebase grows.
__all__: list[str] = []
