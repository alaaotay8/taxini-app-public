"""
Authentication-related schemas for API requests and responses.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class SendOTPRequest(BaseModel):
    """Request schema for sending OTP."""
    phone_number: str = Field(..., description="Phone number in E.164 format")

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        # Basic E.164 format validation
        if not re.match(r'^\+?1?\d{9,15}$', v):
            raise ValueError('Phone number must be in valid format (e.g., +1234567890)')
        return v


class VerifyOTPRequest(BaseModel):
    """Request schema for verifying OTP."""
    phone_number: str = Field(..., description="Phone number in E.164 format")
    otp_code: str = Field(..., description="6-digit OTP code")

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        if not re.match(r'^\+?1?\d{9,15}$', v):
            raise ValueError('Phone number must be in valid format')
        return v

    @field_validator('otp_code')
    @classmethod
    def validate_otp_code(cls, v):
        if not re.match(r'^\d{6}$', v):
            raise ValueError('OTP code must be 6 digits')
        return v


class RefreshTokenRequest(BaseModel):
    """Request schema for refreshing access token."""
    refresh_token: str = Field(..., description="JWT refresh token")


class AuthResponse(BaseModel):
    """Response schema for authentication operations."""
    success: bool
    message: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    user_id: Optional[str] = None
    expires_in: Optional[int] = None


class UserTokenInfo(BaseModel):
    """User information from token."""
    id: str
    phone: Optional[str] = None
    email: Optional[str] = None
    email_confirmed_at: Optional[str] = None
    phone_confirmed_at: Optional[str] = None


class CurrentUser(BaseModel):
    """Current authenticated user information."""
    auth_id: str
    phone: Optional[str] = None
    email: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None
