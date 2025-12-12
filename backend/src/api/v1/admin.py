"""
Admin API endpoints.

Provides REST API for admin operations including user management, 
statistics, settings, and trip history.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session
from typing import Optional
from datetime import date
import logging

from src.services.users import UserService
from src.services.admin import (
    get_users_count,
    get_drivers_count,
    get_riders_count,
    get_all_drivers,
    get_all_riders,
    update_driver_account_status,
    get_user_by_auth_id,
    get_driver_by_id
)
from src.services.auth import AuthService
from src.services.admin_auth import authenticate_admin, get_admin_user_dependency
from src.services.admin_stats import AdminStatsService
from src.services.admin_settings import AdminSettingsService
from src.services.admin_trip import AdminTripService
from src.schemas.auth import CurrentUser
from src.schemas.admin import (
    DashboardResponse,
    DriverListResponse,
    RiderListResponse,
    StatusUpdateResponse,
    AdminLoginRequest,
    AdminLoginResponse,
    DriverDetailResponse,
    GlobalStatsResponse,
    TripListResponse,
    TripDetailResponse,
    SettingsListResponse,
    SettingDetailResponse,
    SettingUpdateResponse,
    UpdateSettingRequest
)
from src.models.enums import UserRole
from src.db.session import get_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(
    request: AdminLoginRequest,
    session: Session = Depends(get_session)
):
    """
    Authenticate admin user with email and password.
    
    Args:
        request: Login request with email and password
        session: Database session
        
    Returns:
        Authentication response with JWT token if successful
    """
    try:
        result = authenticate_admin(session, request.email, request.password)
        
        if not result["success"]:
            raise HTTPException(status_code=401, detail=result["message"])
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def require_admin(
    current_user: CurrentUser = Depends(get_admin_user_dependency),
    session: Session = Depends(get_session)
):
    """
    Dependency to ensure current user is an admin.
    
    Args:
        current_user: Current authenticated admin user from dependency
        session: Database session
        
    Returns:
        CurrentUser if user is an admin
        
    Raises:
        HTTPException: If user is not an admin
    """
    # Get user details from database - admin auth middleware has already verified the token,
    # but we double check the database to ensure the user still has admin role
    user = get_user_by_auth_id(session, current_user.auth_id)
    
    # If not found by auth_id, try with email
    if not user and current_user.email:
        user = get_user_by_auth_id(session, current_user.email)
    
    if not user or user.role != UserRole.ADMIN.value:
        logger.warning(f"Non-admin user tried to access admin endpoint: {current_user.auth_id}")
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )
    
    return current_user


@router.get("/dashboard", response_model=DashboardResponse)
async def get_admin_dashboard(
    current_user: CurrentUser = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get admin dashboard statistics.
    
    Args:
        current_user: Current authenticated admin user from dependency
        session: Database session
        
    Returns:
        Dashboard statistics
    """
    try:
        # Get counts from admin service
        users_count = get_users_count(session)
        drivers_count = get_drivers_count(session)
        riders_count = get_riders_count(session)
        
        return {
            "success": True,
            "statistics": {
                "total_users": users_count,
                "total_drivers": drivers_count,
                "total_riders": riders_count
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get admin dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/drivers", response_model=DriverListResponse)
async def get_all_drivers_endpoint(
    current_user: CurrentUser = Depends(require_admin),
    session: Session = Depends(get_session),
    page: int = 1,
    page_size: int = 20
):
    """
    Get all drivers with pagination.
    
    Args:
        current_user: Current authenticated admin user from dependency
        session: Database session
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Returns:
        List of drivers with pagination metadata
    """
    try:
        # Use the imported function, not the endpoint itself
        drivers = get_all_drivers(session, page, page_size)
        total_count = get_drivers_count(session)
        
        return {
            "success": True,
            "data": drivers,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_items": total_count,
                "total_pages": (total_count + page_size - 1) // page_size
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get drivers list: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/riders", response_model=RiderListResponse)
async def get_all_riders_endpoint(
    current_user: CurrentUser = Depends(require_admin),
    session: Session = Depends(get_session),
    page: int = 1,
    page_size: int = 20
):
    """
    Get all riders with pagination.
    
    Args:
        current_user: Current authenticated admin user from dependency
        session: Database session
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Returns:
        List of riders with pagination metadata
    """
    try:
        # Use the imported function, not the endpoint itself
        riders = get_all_riders(session, page, page_size)
        total_count = get_riders_count(session)
        
        return {
            "success": True,
            "data": riders,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_items": total_count,
                "total_pages": (total_count + page_size - 1) // page_size
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get riders list: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/drivers/{driver_id}/account-status", response_model=StatusUpdateResponse)
async def update_driver_status_endpoint(
    driver_id: str,
    account_status: str,
    current_user: CurrentUser = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Update driver account status.
    
    Args:
        driver_id: ID of the driver to update
        account_status: New account status (locked, verified, banned)
        current_user: Current authenticated admin user from dependency
        session: Database session
        
    Returns:
        Success response
    """
    try:
        # Make sure we're calling the service function, not this endpoint itself
        result = update_driver_account_status(
            session, 
            driver_id, 
            account_status
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )
        
        return {
            "success": True,
            "message": f"Driver account status updated to {account_status}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update driver account status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/drivers/{driver_id}", response_model=DriverDetailResponse)
async def get_driver_details(
    driver_id: str,
    current_user: CurrentUser = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get detailed information for a specific driver, including document files.
    
    Args:
        driver_id: ID of the driver to retrieve
        current_user: Current authenticated admin user from dependency
        session: Database session
        
    Returns:
        Detailed driver information including document URLs
    """
    try:
        driver = get_driver_by_id(session, driver_id)
        
        if not driver:
            raise HTTPException(
                status_code=404,
                detail="Driver not found"
            )
        
        return {
            "success": True,
            "data": driver
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get driver details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ===========================
# NEW ADMIN FEATURES ENDPOINTS
# ===========================

@router.get("/statistics/global", response_model=GlobalStatsResponse)
async def get_global_statistics(
    start_date: Optional[date] = Query(None, description="Start date for filtering (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date for filtering (YYYY-MM-DD)"),
    current_user: CurrentUser = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get comprehensive platform statistics including rides/day, revenue, and active drivers.
    
    Subtask 1: Admin can view global platform statistics with KPIs and date filtering.
    
    Args:
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        current_user: Current authenticated admin user
        session: Database session
        
    Returns:
        Comprehensive platform statistics
    """
    try:
        stats = AdminStatsService.get_global_statistics(
            session=session,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get global statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/settings", response_model=SettingsListResponse)
async def get_all_settings(
    category: Optional[str] = Query(None, description="Filter by setting category"),
    current_user: CurrentUser = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get all application settings, optionally filtered by category.
    
    Subtask 2: Admin can view all configurable settings including approach fees rate.
    
    Args:
        category: Optional category filter (pricing, operational, etc.)
        current_user: Current authenticated admin user
        session: Database session
        
    Returns:
        List of all settings
    """
    try:
        # Initialize default settings if they don't exist
        AdminSettingsService.initialize_default_settings(session)
        
        settings = AdminSettingsService.get_all_settings(session, category)
        
        return {
            "success": True,
            "data": settings
        }
        
    except Exception as e:
        logger.error(f"Failed to get settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/settings/{setting_key}", response_model=SettingDetailResponse)
async def get_setting_by_key(
    setting_key: str,
    current_user: CurrentUser = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get a specific setting by its key.
    
    Args:
        setting_key: The setting key to retrieve
        current_user: Current authenticated admin user
        session: Database session
        
    Returns:
        Setting details
    """
    try:
        setting = AdminSettingsService.get_setting_by_key(session, setting_key)
        
        if not setting:
            raise HTTPException(
                status_code=404,
                detail=f"Setting with key '{setting_key}' not found"
            )
        
        return {
            "success": True,
            "data": setting
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get setting {setting_key}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/settings/{setting_key}", response_model=SettingUpdateResponse)
async def update_setting(
    setting_key: str,
    request: UpdateSettingRequest,
    current_user: CurrentUser = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Update a setting value with immediate persistence.
    
    Subtask 2: Admin can dynamically adjust approach fees rate (FA/km) and other settings.
    The changes are saved immediately and will be applied to future calculations.
    
    Args:
        setting_key: The setting key to update
        request: Update request with new value
        current_user: Current authenticated admin user
        session: Database session
        
    Returns:
        Updated setting information
    """
    try:
        result = AdminSettingsService.update_setting(session, setting_key, request)
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )
        
        return {
            "success": True,
            "message": result["message"],
            "data": result["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update setting {setting_key}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/trips", response_model=TripListResponse)
async def get_trips_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    driver_id: Optional[str] = Query(None, description="Filter by driver ID"),
    rider_id: Optional[str] = Query(None, description="Filter by rider ID"),
    status: Optional[str] = Query(None, description="Filter by trip status"),
    start_date: Optional[date] = Query(None, description="Filter trips from this date"),
    end_date: Optional[date] = Query(None, description="Filter trips until this date"),
    search: Optional[str] = Query(None, description="Search in addresses, names, or phone numbers"),
    current_user: CurrentUser = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get filterable history of all trips on the platform.
    
    Subtask 3: Admin can view all trips with comprehensive filtering by driver, date, status.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of trips per page
        driver_id: Filter by specific driver
        rider_id: Filter by specific rider
        status: Filter by trip status (requested, completed, cancelled, etc.)
        start_date: Filter trips from this date
        end_date: Filter trips until this date
        search: Search in addresses, names, or phone numbers
        current_user: Current authenticated admin user
        session: Database session
        
    Returns:
        Paginated list of trips with detailed information
    """
    try:
        result = AdminTripService.get_all_trips(
            session=session,
            page=page,
            page_size=page_size,
            driver_id=driver_id,
            rider_id=rider_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            search=search
        )
        
        return {
            "success": True,
            "data": result["trips"],
            "pagination": {
                "current_page": result["page"],
                "page_size": result["page_size"],
                "total_items": result["total"],
                "total_pages": result["total_pages"]
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get trips history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/trips/{trip_id}", response_model=TripDetailResponse)
async def get_trip_details(
    trip_id: str,
    current_user: CurrentUser = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get detailed information for a specific trip.
    
    Subtask 3: Admin can access detailed information for each trip in the history.
    
    Args:
        trip_id: ID of the trip to retrieve
        current_user: Current authenticated admin user
        session: Database session
        
    Returns:
        Detailed trip information
    """
    try:
        trip = AdminTripService.get_trip_by_id(session, trip_id)
        
        if not trip:
            raise HTTPException(
                status_code=404,
                detail="Trip not found"
            )
        
        return {
            "success": True,
            "data": trip
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get trip details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
