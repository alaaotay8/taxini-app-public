"""
Taxini Models package.

This package is intentionally left without concrete implementations. It exists to
document and enforce the structure and conventions for domain models as the project evolves.

Guiding principles:
- Separation of concerns:
  - Keep persistence-layer definitions (ORM mappings) here.
  - Keep business rules and orchestration in `taxini.services`.
  - Keep API request/response shapes in `taxini.schemas`.
- SQLAlchemy 2.x style:
  - Prefer type-annotated, Declarative mappings (SQLAlchemy 2.0 style).
  - Centralize the Declarative Base and engine/session config under `taxini.db`.
- Portability and clarity:
  - Favor database-agnostic types where reasonable.
  - Use explicit constraints, indexes, and naming conventions (Alembic-friendly).
  - Prefer UUID (string) or BIGINT identifiers; be consistent across models.
- Observability and maintainability:
  - Include `created_at` and `updated_at` columns (server-side defaults).
  - Provide readable `__repr__` implementations on entities.

Suggested layout (create files when needed):
- taxini/models/
  - mixins.py          -> shared mixins (TimestampMixin, SoftDeleteMixin, etc.)
  - enums.py           -> domain enums (e.g., roles, ride statuses)
  - user.py            -> User entity (rider/driver/admin flags)
  - ride.py            -> Ride entity (lifecycle, pricing, coordinates)
  - vehicle.py         -> Vehicle entity (for drivers)
  - payment.py         -> Payment/transaction entities (if applicable)
  - __init__.py        -> (this file) aggregate exports if needed

Design notes:
- Keep this package free of FastAPI constructs or HTTP concerns.
- Avoid importing from higher layers (e.g., API or services) to prevent circular deps.
- If you introduce repository abstractions, consider placing them under `taxini.db.repositories`
  (and keep them framework/transport agnostic).

Example skeleton (for future reference; do not uncomment directly here):

    # mixins.py
    # from datetime import datetime
    # from sqlalchemy import DateTime, func
    # from sqlalchemy.orm import Mapped, mapped_column
    #
    # class TimestampMixin:
    #     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    #     updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # user.py
    # from enum import Enum
    # from sqlalchemy import String
    # from sqlalchemy.orm import Mapped, mapped_column
    # from taxini.db.session import Base  # central Declarative Base (to be created in taxini.db)
    # from .mixins import TimestampMixin
    #
    # class UserRole(str, Enum):
    #     rider = "rider"
    #     driver = "driver"
    #     admin = "admin"
    #
    # class User(TimestampMixin, Base):
    #     __tablename__ = "users"
    #     id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID string
    #     full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    #     email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    #     role: Mapped[UserRole]

    # ride.py
    # from enum import Enum
    # from sqlalchemy import Float, ForeignKey, String
    # from sqlalchemy.orm import Mapped, mapped_column, relationship
    # from taxini.db.session import Base
    # from .mixins import TimestampMixin
    #
    # class RideStatus(str, Enum):
    #     requested = "requested"
    #     accepted = "accepted"
    #     in_progress = "in_progress"
    #     completed = "completed"
    #     canceled = "canceled"
    #
    # class Ride(TimestampMixin, Base):
    #     __tablename__ = "rides"
    #     id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID string
    #     rider_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    #     driver_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), index=True)
    #     status: Mapped[RideStatus]
    #     origin_lat: Mapped[float] = mapped_column(Float, nullable=False)
    #     origin_lng: Mapped[float] = mapped_column(Float, nullable=False)
    #     dest_lat: Mapped[float] = mapped_column(Float, nullable=False)
    #     dest_lng: Mapped[float] = mapped_column(Float, nullable=False)
    #     rider = relationship("User", foreign_keys=[rider_id])
    #     driver = relationship("User", foreign_keys=[driver_id])

Exports:
- Keep `__all__` minimal; re-export only stable, commonly used symbols when the models are implemented.
"""

# Import models to ensure they're registered with SQLModel
from .location import Location, LocationBase, LocationUpdate, LocationResponse
from .ticket import Ticket, TicketBase, TicketUpdate, TicketStatus, TicketPriority
from .settings import Settings, SettingsBase, SettingsUpdate, SettingKeys, DEFAULT_SETTINGS
from .trip import Trip, TripBase
from .user import User, Driver, Rider, Admin

# Intentionally export nothing at the package root for now.
__all__: list[str] = []
