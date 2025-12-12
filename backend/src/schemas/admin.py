"""
Admin schemas for API requests and responses.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, date


class DriverSummary(BaseModel):
    """Summary information for a driver."""
    id: str
    name: str
    email: str
    phone_number: str
    taxi_number: str
    account_status: str
    driver_status: str
    id_card: Optional[str] = None
    driver_license: Optional[str] = None
    created_at: datetime


class RiderSummary(BaseModel):
    """Summary information for a rider."""
    id: str
    name: str
    email: str
    phone_number: str
    residence_place: str
    created_at: datetime


class DashboardStats(BaseModel):
    """Admin dashboard statistics."""
    total_users: int
    total_drivers: int
    total_riders: int


class GlobalStats(BaseModel):
    """Global platform statistics."""
    # Basic counts
    total_users: int
    total_drivers: int
    total_riders: int
    active_drivers: int
    
    # Trip statistics
    total_trips: int
    trips_today: int
    trips_this_week: int
    trips_this_month: int
    
    # Revenue statistics (in TND)
    total_revenue: float
    revenue_today: float
    revenue_this_week: float
    revenue_this_month: float
    
    # Average metrics
    average_trip_duration_minutes: Optional[float] = None
    average_trip_distance_km: Optional[float] = None
    average_trip_cost: Optional[float] = None
    
    # Status distribution
    completed_trips: int
    cancelled_trips: int
    completion_rate: float  # Percentage
    
    # Driver metrics
    online_drivers: int
    busy_drivers: int  # drivers currently on trip
    offline_drivers: int


class TripStatsFilter(BaseModel):
    """Filter for trip statistics."""
    start_date: Optional[date] = Field(None, description="Start date for filtering (YYYY-MM-DD)")
    end_date: Optional[date] = Field(None, description="End date for filtering (YYYY-MM-DD)")
    driver_id: Optional[str] = Field(None, description="Filter by specific driver ID")
    status: Optional[str] = Field(None, description="Filter by trip status")


class TripSummary(BaseModel):
    """Summary information for a trip."""
    id: str
    rider_id: str
    rider_name: str
    rider_phone: str
    driver_id: Optional[str] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    
    pickup_address: Optional[str] = None
    destination_address: Optional[str] = None
    
    status: str
    trip_type: Optional[str] = None
    estimated_distance_km: Optional[float] = None
    estimated_cost_tnd: Optional[float] = None
    
    requested_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    rider_rating: Optional[int] = None
    driver_rating: Optional[int] = None
    
    created_at: datetime


class SettingSummary(BaseModel):
    """Summary information for a setting."""
    id: str
    setting_key: str
    setting_value: str
    data_type: str
    description: Optional[str] = None
    category: str
    is_active: bool
    is_editable: bool
    updated_at: Optional[datetime] = None


class UpdateSettingRequest(BaseModel):
    """Request schema for updating a setting."""
    setting_value: str = Field(..., description="New value for the setting")
    description: Optional[str] = Field(None, description="Optional description update")


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    current_page: int
    page_size: int
    total_items: int
    total_pages: int


class DriverListResponse(BaseModel):
    """Response schema for listing drivers."""
    success: bool
    data: List[DriverSummary]
    pagination: PaginationMeta


class RiderListResponse(BaseModel):
    """Response schema for listing riders."""
    success: bool
    data: List[RiderSummary]
    pagination: PaginationMeta


class DashboardResponse(BaseModel):
    """Response schema for admin dashboard."""
    success: bool
    statistics: DashboardStats


class UpdateDriverStatusRequest(BaseModel):
    """Request schema for updating driver account status."""
    account_status: str = Field(..., description="New account status (locked, verified, banned)")


class StatusUpdateResponse(BaseModel):
    """Response schema for status update operations."""
    success: bool
    message: str
    
    
class DriverDetailResponse(BaseModel):
    """Response schema for single driver details."""
    success: bool
    data: DriverSummary


class AdminLoginRequest(BaseModel):
    """Request schema for admin login."""
    email: EmailStr = Field(..., description="Admin email address")
    password: str = Field(..., description="Admin password", min_length=6)


class AdminLoginResponse(BaseModel):
    """Response schema for admin login."""
    success: bool
    message: str
    access_token: Optional[str] = None
    admin_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    
    
class UpdateDriverDocumentsRequest(BaseModel):
    """Request schema for updating driver documents."""
    id_card: Optional[str] = Field(None, description="URL or path to the ID card document")
    driver_license: Optional[str] = Field(None, description="URL or path to the driver license document")
    
    
class UpdateDriverDocumentsResponse(BaseModel):
    """Response schema for updating driver documents."""
    success: bool
    message: str
    id_card: Optional[str] = None
    driver_license: Optional[str] = None


# New response schemas for the admin features
class GlobalStatsResponse(BaseModel):
    """Response schema for global statistics."""
    success: bool
    data: GlobalStats


class TripListResponse(BaseModel):
    """Response schema for listing trips."""
    success: bool
    data: List[TripSummary]
    pagination: PaginationMeta


class TripDetailResponse(BaseModel):
    """Response schema for single trip details."""
    success: bool
    data: TripSummary


class SettingsListResponse(BaseModel):
    """Response schema for listing settings."""
    success: bool
    data: List[SettingSummary]


class SettingDetailResponse(BaseModel):
    """Response schema for single setting details."""
    success: bool
    data: SettingSummary


class SettingUpdateResponse(BaseModel):
    """Response schema for setting update."""
    success: bool
    message: str
    data: SettingSummary
