"""
SQLModel mixins for common fields and behaviors.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from uuid import uuid4


class TimestampMixin(SQLModel):
    """Mixin for timestamp fields."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.utcnow})


class UUIDMixin(SQLModel):
    """Mixin for UUID primary key."""
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
