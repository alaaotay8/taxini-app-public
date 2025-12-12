"""
Taxini Schemas package.

This package is intentionally left without concrete implementations. It exists to
document and enforce the structure and conventions for API request/response models
(Pydantic schemas) as the project evolves.

Guiding principles:
- Separation of concerns:
  - Keep transport-facing contracts (HTTP request/response payloads) here.
  - Keep domain entities and persistence concerns in `taxini.models`.
  - Keep orchestration and business rules in `taxini.services`.
- Versioned APIs:
  - Schemas should reflect stable, versioned API contracts exposed under `taxini.api.v1`.
  - Prefer explicit input/output models (e.g., `UserCreate`, `UserOut`) rather than reusing
    ORM entities or internal DTOs.
- Pydantic v2:
  - Use `BaseModel` with `model_config = ConfigDict(from_attributes=True)` for ORM compatibility
    when needed (e.g., translating SQLAlchemy rows to API shapes).
  - Favor strict field typing where possible (e.g., `EmailStr`, constrained `str`/`int`).
  - Provide field-level and model-level validators for domain-specific constraints
    (e.g., E.164 phone numbers, latitude/longitude ranges).

Suggested layout (create files when needed):
- taxini/schemas/
  - common.py        -> Shared building blocks (IDs, timestamps, pagination, money, enums if API-specific)
  - user.py          -> User-related input/output schemas (e.g., UserCreate, UserUpdate, UserOut)
  - ride.py          -> Ride-related input/output schemas (e.g., RideCreate, RideUpdate, RideOut)
  - auth.py          -> Auth flows (e.g., TokenRequest, TokenResponse, Refresh)
  - pagination.py    -> Standardized pagination request/response models
  - errors.py        -> Problem Details / error envelope schemas
  - filters.py       -> Query/filter inputs for listing endpoints (e.g., status filters, date ranges)
  - __init__.py      -> (this file) optional stable re-exports when contracts settle

Conventions:
- Avoid importing from `taxini.models` to prevent API contracts from depending on persistence details.
  If you must mirror domain enums/types for the API, define API-facing enums in `schemas.common`
  or map model enums to API enums explicitly at the boundary.
- Treat datetimes as timezone-aware (UTC). When serializing, prefer ISO 8601 with `Z` suffix.
- Use clear naming: `<Resource><Action>` for inputs (e.g., `RideCreate`, `UserUpdate`),
  `<Resource>Out` for outputs (e.g., `RideOut`, `UserOut`).
- Represent money in minor units (e.g., `price_cents: int`) and include a 3-letter ISO currency code.
- Provide pagination wrappers (items + total + limit + offset) for list endpoints.
- Keep validation close to schemas (e.g., E.164 phone validation, lat/lng range checks).
- Use `model_dump()`/`model_dump_json()` at the API edge; do not expose ORM instances.

Example skeletons for future reference (do not uncomment directly here):

    # common.py
    # from pydantic import BaseModel, ConfigDict, Field
    # class ORMBaseModel(BaseModel):
    #     model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    #
    # class Page(BaseModel):
    #     total: int
    #     limit: int
    #     offset: int
    #     # items: list[T]  # Use generics when needed

    # user.py
    # from pydantic import BaseModel, EmailStr, Field
    # class UserCreate(BaseModel):
    #     full_name: str = Field(..., min_length=1, max_length=200)
    #     email: EmailStr
    #     password: str = Field(..., min_length=8, max_length=128)
    #
    # class UserOut(ORMBaseModel):
    #     id: str
    #     full_name: str
    #     email: EmailStr
    #     created_at: datetime
    #     updated_at: datetime

    # ride.py
    # from pydantic import BaseModel, Field, field_validator
    # class RideCreate(BaseModel):
    #     rider_id: str
    #     origin_lat: float
    #     origin_lng: float
    #     dest_lat: float
    #     dest_lng: float
    #     currency: str = Field(default="USD", min_length=3, max_length=3)
    #
    #     @field_validator("origin_lat", "dest_lat")
    #     @classmethod
    #     def _lat(cls, v: float) -> float:
    #         if not (-90 <= v <= 90):
    #             raise ValueError("latitude must be between -90 and 90")
    #         return v
    #
    #     @field_validator("origin_lng", "dest_lng")
    #     @classmethod
    #     def _lng(cls, v: float) -> float:
    #         if not (-180 <= v <= 180):
    #             raise ValueError("longitude must be between -180 and 180")
    #         return v

Notes:
- Keep this package free of framework-specific concerns other than Pydantic.
- Re-export only stable, widely used schemas from `__init__.py` once they’re implemented.
"""

# Intentionally export nothing at the package root for now.
__all__: list[str] = []
