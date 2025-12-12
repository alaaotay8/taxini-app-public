"""
Taxini Services package.

This package is intentionally left without concrete implementations. It exists to document
and enforce the structure and conventions for the business logic layer (use-case orchestration)
as the project evolves.

Role of services:
- Encapsulate domain use-cases and business rules.
- Keep FastAPI/HTTP handlers thin; routers should delegate to services.
- Avoid transport-specific (HTTP, gRPC, CLI) concerns and frameworks inside services.
- Orchestrate data access via repositories (if introduced) and persist aggregates using the DB layer.
- Provide clear, typed interfaces that are easy to test in isolation.

Layering (suggested):
- taxini.api.* (transport): request/response parsing, auth context extraction, error mapping
  -> calls
- taxini.services.* (use-cases): business rules, state transitions, orchestration
  -> calls
- taxini.db.* (infrastructure): repositories, sessions, migrations, persistence
- taxini.models.* (domain): entities/mappings
- taxini.schemas.* (contracts): API DTOs (request/response shapes)

Recommended layout (create files as needed):
- rides.py          -> Ride lifecycle: request, accept, start, complete, cancel, re-route
- users.py          -> User lifecycle: create, update profile, deactivate/reactivate
- drivers.py        -> Driver onboarding, availability, vehicle management
- auth.py           -> Authentication flows (login, token refresh, logout)
- payments.py       -> Payment intents, captures, refunds (coordinate with PSP)
- pricing.py        -> Price estimation, surge, promotions, fare computation rules
- matching.py       -> Rider-driver matching strategies, batching, dispatch logic
- notifications.py  -> Push/SMS/email orchestration (decouple from transport providers)
- geo.py            -> Geospatial utilities (distance calc, ETA estimation, region checks)
- errors.py         -> Service-level exceptions (e.g., ServiceError, NotFoundError, InvalidStateError)
- utils.py          -> Cross-service helpers that are domain- or use-case-oriented

Guidelines:
- Keep services async where I/O is expected; avoid blocking calls in the event loop.
- Perform input validation close to the boundary (API schemas), enforce invariants in services.
- Make state transitions explicit and validated (e.g., requested -> accepted -> in_progress -> completed).
- Design idempotent operations where appropriate (e.g., payment capture, cancelation).
- Return stable value objects/DTOs (schemas) to the API; do not leak ORM entities over the boundary.
- Keep error taxonomy small and consistent; map service exceptions to HTTP errors at the transport layer.

Testing:
- Unit-test services with in-memory fakes or transaction-scoped DB fixtures.
- Prefer dependency injection for repositories/clients to make services testable.
- Avoid global state; keep services stateless or scope state to explicit contexts.

Observability:
- Add logging around key domain events (created ride, assigned driver, captured payment).
- Consider tracing spans for external calls (DB, payment providers, push gateways).
- Keep logging structured and context-rich (ride_id, user_id, status).

Security:
- Do not perform direct auth/permission checks in services if the transport layer already
  establishes identity/roles; accept an authenticated principal/context where needed.
- Where business rules rely on roles/ownership, verify them explicitly and raise service errors.

This file is intentionally minimal and free of runtime side effects. Concrete implementations
should be added in sibling modules as the product features are built.
"""

# This package intentionally exports nothing by default.
__all__: list[str] = []
