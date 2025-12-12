"""
Taxini Core package.

This package will house cross-cutting concerns for the application:
- Configuration/settings (environment variables, feature flags, etc.)
- Security (authentication, authorization helpers, password hashing, JWT handling)
- Logging setup (formatters, handlers, structured logging)

Recommended modules for `taxini.core` (to be created when needed):
- settings.py      -> Configuration loading and validation (env/.env, secrets)
- logging.py       -> Logging configuration and helpers
- security.py      -> Security primitives (password hashing, JWT helpers, etc.)
- middleware.py    -> FastAPI/Starlette middlewares and related utilities
- observability.py -> Tracing/metrics/log correlation hooks
- config.py        -> Additional config glue or typed config objects (optional)

Other top-level packages in the repository (placeholders until implemented):
- taxini.db         -> Database engine/session bootstrap, migrations wiring
- taxini.models     -> Domain models (e.g., SQLAlchemy models)
- taxini.schemas    -> Pydantic request/response models (API contracts)
- taxini.services   -> Business logic and use-case orchestration
- taxini.workers    -> Background jobs and task runners

Notes:
- Keep `core` free of domain/business rules; focus on shared infrastructure and
  application scaffolding that other packages depend on.
- Prefer small, composable modules with clear responsibilities.
"""

# This package intentionally exports nothing by default.
__all__: list[str] = []
