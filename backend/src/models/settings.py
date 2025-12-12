"""
Application settings model for configurable parameters.

This model stores dynamic configuration values that can be modified by admins
such as pricing rates, fees, and other operational parameters.
"""

from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, String, Float, Text, Boolean
from datetime import datetime
from .mixins import TimestampMixin, UUIDMixin


class SettingsBase(SQLModel):
    """Base settings fields shared across create/update/read operations."""
    setting_key: str = Field(unique=True, index=True, max_length=100, description="Unique identifier for the setting")
    setting_value: str = Field(description="The value of the setting (stored as string)")
    data_type: str = Field(default="string", max_length=20, description="Data type of the value (string, float, int, bool)")
    description: Optional[str] = Field(default=None, max_length=500, description="Human-readable description of the setting")
    category: str = Field(default="general", max_length=50, description="Category grouping for the setting")
    is_active: bool = Field(default=True, description="Whether this setting is currently active")
    is_editable: bool = Field(default=True, description="Whether this setting can be modified via admin interface")


class Settings(SettingsBase, UUIDMixin, TimestampMixin, table=True):
    """Settings table for storing configurable application parameters."""
    __tablename__ = "settings"
    
    # Override columns with specific database types
    setting_key: str = Field(sa_column=Column(String(100), unique=True, nullable=False, index=True))
    setting_value: str = Field(sa_column=Column(Text, nullable=False))
    data_type: str = Field(sa_column=Column(String(20), nullable=False, default="string"))
    description: Optional[str] = Field(sa_column=Column(Text, nullable=True))
    category: str = Field(sa_column=Column(String(50), nullable=False, default="general"))
    is_active: bool = Field(sa_column=Column(Boolean, nullable=False, default=True))
    is_editable: bool = Field(sa_column=Column(Boolean, nullable=False, default=True))


class SettingsUpdate(SQLModel):
    """Schema for updating settings."""
    setting_value: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


# Predefined setting keys for the application
class SettingKeys:
    """Constants for predefined setting keys."""
    APPROACH_FEE_RATE_PER_KM = "approach_fee_rate_per_km"
    BASE_FARE = "base_fare"
    PRICE_PER_KM = "price_per_km"
    PRICE_PER_MINUTE = "price_per_minute"
    MINIMUM_FARE = "minimum_fare"
    MAXIMUM_DRIVER_DISTANCE_KM = "maximum_driver_distance_km"
    COMMISSION_RATE = "commission_rate"
    CANCELLATION_FEE = "cancellation_fee"


# Default settings to be created on application startup
DEFAULT_SETTINGS = [
    {
        "setting_key": SettingKeys.APPROACH_FEE_RATE_PER_KM,
        "setting_value": "0.5",
        "data_type": "float",
        "description": "Fee rate per kilometer for driver approach to pickup location (TND/km)",
        "category": "pricing",
        "is_editable": True
    },
    {
        "setting_key": SettingKeys.BASE_FARE,
        "setting_value": "2.0",
        "data_type": "float", 
        "description": "Base fare for all trips (TND)",
        "category": "pricing",
        "is_editable": True
    },
    {
        "setting_key": SettingKeys.PRICE_PER_KM,
        "setting_value": "1.2",
        "data_type": "float",
        "description": "Price per kilometer during trip (TND/km)",
        "category": "pricing",
        "is_editable": True
    },
    {
        "setting_key": SettingKeys.PRICE_PER_MINUTE,
        "setting_value": "0.3",
        "data_type": "float",
        "description": "Price per minute during trip (TND/min)",
        "category": "pricing",
        "is_editable": True
    },
    {
        "setting_key": SettingKeys.MINIMUM_FARE,
        "setting_value": "3.0",
        "data_type": "float",
        "description": "Minimum fare for any trip (TND)",
        "category": "pricing",
        "is_editable": True
    },
    {
        "setting_key": SettingKeys.MAXIMUM_DRIVER_DISTANCE_KM,
        "setting_value": "10.0",
        "data_type": "float",
        "description": "Maximum distance to search for available drivers (km)",
        "category": "operational",
        "is_editable": True
    },
    {
        "setting_key": SettingKeys.COMMISSION_RATE,
        "setting_value": "0.15",
        "data_type": "float",
        "description": "Platform commission rate (percentage as decimal, e.g., 0.15 = 15%)",
        "category": "pricing",
        "is_editable": True
    },
    {
        "setting_key": SettingKeys.CANCELLATION_FEE,
        "setting_value": "1.0",
        "data_type": "float",
        "description": "Fee charged for trip cancellation after driver acceptance (TND)",
        "category": "pricing",
        "is_editable": True
    }
]
