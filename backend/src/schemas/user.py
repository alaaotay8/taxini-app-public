"""
User-related schemas for API requests and responses.
"""

from pydantic import BaseModel, Field, field_validator, HttpUrl
from typing import Optional, Dict, Any
from src.models.enums import UserRole, DriverAccountStatus, DriverStatus
import re
import html


class CompleteProfileRequest(BaseModel):
    """Request schema for completing user profile."""
    name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    email: str = Field(..., description="User's email address")
    role: UserRole = Field(..., description="User role: driver or rider only")
    role_specific_data: Optional[Dict[str, Any]] = Field(default=None, description="Role-specific fields")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        # Sanitize HTML entities
        v = html.unescape(v).strip()
        # Allow only letters, spaces, hyphens, and apostrophes
        if not re.match(r"^[a-zA-Z\u0600-\u06FF\s'-]+$", v):
            raise ValueError('Name can only contain letters, spaces, hyphens, and apostrophes')
        # Prevent excessive spaces
        if '  ' in v:
            raise ValueError('Name cannot contain consecutive spaces')
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        v = v.strip().lower()
        # Enhanced email validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        if len(v) > 254:  # RFC 5321
            raise ValueError('Email address too long')
        return v

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in [UserRole.RIDER, UserRole.DRIVER]:
            raise ValueError('Only rider and driver roles are allowed')
        return v


class RiderProfileData(BaseModel):
    """Schema for rider-specific profile data."""
    residence_place: str = Field(..., max_length=255, description="Rider's residence location")


class DriverProfileData(BaseModel):
    """Schema for driver-specific profile data."""
    id_card: HttpUrl = Field(..., max_length=500, description="ID card image URL")
    driver_license: HttpUrl = Field(..., max_length=500, description="Driver license image URL")
    taxi_number: str = Field(..., max_length=50, description="Taxi registration number")
    account_status: Optional[str] = Field(default="locked", description="Driver account status: locked, verified, banned")
    driver_status: Optional[str] = Field(default="offline", description="Driver status: offline, online, on_trip")

    @field_validator('account_status')
    @classmethod
    def validate_account_status(cls, v):
        if v and v not in ["locked", "verified", "banned"]:
            raise ValueError('Account status must be locked, verified, or banned')
        return v or "locked"

    @field_validator('driver_status')
    @classmethod
    def validate_driver_status(cls, v):
        if v and v not in ["offline", "online", "on_trip"]:
            raise ValueError('Driver status must be offline, online, or on_trip')
        return v or "offline"




class UpdateProfileRequest(BaseModel):
    """Request schema for updating user profile."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = Field(None)
    residence_place: Optional[str] = Field(None, description="Residence place for rider profile")
    role_specific_data: Optional[Dict[str, Any]] = Field(default=None)
    acting_as: Optional[UserRole] = Field(None, description="Which profile role to update (rider/driver). Required for multi-role users.")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v and not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('Invalid email format')
        return v


class UserResponse(BaseModel):
    """Response schema for user information."""
    id: str
    auth_id: str
    name: str
    email: str
    phone_number: str
    role: UserRole
    auth_status: str
    created_at: str
    updated_at: Optional[str] = None


class RiderResponse(BaseModel):
    """Response schema for rider profile."""
    id: str
    user_id: str
    residence_place: str
    created_at: str
    updated_at: Optional[str] = None


class DriverResponse(BaseModel):
    """Response schema for driver profile."""
    id: str
    user_id: str
    id_card: str
    driver_license: str
    taxi_number: str
    account_status: str
    driver_status: str
    created_at: str
    updated_at: Optional[str] = None




class CompleteUserProfileResponse(BaseModel):
    """Response schema for complete user profile with role data."""
    success: bool
    message: str
    user: Optional[UserResponse] = None
    role_profile: Optional[Dict[str, Any]] = None


class PasswordResetRequest(BaseModel):
    """Request schema for password reset."""
    phone_number: str = Field(..., description="User's phone number to look up email")

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^\+?1?\d{9,15}$', v):
            raise ValueError('Invalid phone number format')
        return v


class PasswordResetResponse(BaseModel):
    """Response schema for password reset."""
    success: bool
    message: str


class DriverStatusUpdate(BaseModel):
    """Request model for updating driver status."""
    status: DriverStatus


class DriverStatusResponse(BaseModel):
    """Response model for driver status operations."""
    success: bool
    message: str
    driver_id: str
    status: DriverStatus
    streaming_active: bool
