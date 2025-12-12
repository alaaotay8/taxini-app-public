"""
Helper functions to extend UserService for admin operations.
"""

import logging
from typing import Dict, Any, List, Optional
from sqlmodel import Session, select, func
from datetime import datetime

from src.models.user import User, Driver, Rider, Admin
from src.models.enums import UserRole
from src.schemas.admin import DriverSummary, RiderSummary

logger = logging.getLogger(__name__)


def get_users_count(session: Session) -> int:
    """
    Get total count of users.
    
    Args:
        session: Database session
        
    Returns:
        Total number of users
    """
    return session.exec(select(func.count(User.id))).one()


def get_drivers_count(session: Session) -> int:
    """
    Get total count of drivers.
    
    Args:
        session: Database session
        
    Returns:
        Total number of drivers
    """
    return session.exec(select(func.count(Driver.id))).one()


def get_riders_count(session: Session) -> int:
    """
    Get total count of riders.
    
    Args:
        session: Database session
        
    Returns:
        Total number of riders
    """
    return session.exec(select(func.count(Rider.id))).one()


def get_all_drivers(session: Session, page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
    """
    Get all drivers with pagination.
    
    Args:
        session: Database session
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Returns:
        List of driver data with pagination
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Query drivers with join to users
    drivers_with_users = session.exec(
        select(Driver, User)
        .join(User, Driver.user_id == User.id)
        .offset(offset)
        .limit(page_size)
    ).all()
    
    # Log the number of drivers found and a sample of their document fields
    logger.info(f"Found {len(drivers_with_users)} drivers")
    if drivers_with_users:
        sample_driver = drivers_with_users[0][0]
        logger.info(f"Sample driver document fields - ID Card: {sample_driver.id_card}, Driver License: {sample_driver.driver_license}")
    
    # Format response
    result = []
    from src.core.settings import settings
    
    # Get Supabase URL for building document URLs
    supabase_url = settings.supabase_url
    bucket_name = settings.supabase_storage_bucket
    
    for driver, user in drivers_with_users:
        # Construct full URLs for documents if they exist
        id_card_url = None
        driver_license_url = None
        
        if driver.id_card:
            # Check if it's already a full URL or just a path
            if driver.id_card.startswith('http'):
                id_card_url = driver.id_card
            else:
                # Construct Supabase storage URL
                id_card_url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/{driver.id_card}"
                
        if driver.driver_license:
            # Check if it's already a full URL or just a path
            if driver.driver_license.startswith('http'):
                driver_license_url = driver.driver_license
            else:
                # Construct Supabase storage URL
                driver_license_url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/{driver.driver_license}"
        
        result.append({
            "id": driver.id,
            "name": user.name,
            "email": user.email,
            "phone_number": user.phone_number,
            "taxi_number": driver.taxi_number,
            "account_status": driver.account_status,
            "driver_status": driver.driver_status,
            "id_card": id_card_url,
            "driver_license": driver_license_url,
            "created_at": driver.created_at
        })
    
    return result


def get_all_riders(session: Session, page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
    """
    Get all riders with pagination.
    
    Args:
        session: Database session
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Returns:
        List of rider data with pagination
    """
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Query riders with join to users
    riders_with_users = session.exec(
        select(Rider, User)
        .join(User, Rider.user_id == User.id)
        .offset(offset)
        .limit(page_size)
    ).all()
    
    # Format response
    result = []
    for rider, user in riders_with_users:
        result.append({
            "id": rider.id,
            "name": user.name,
            "email": user.email,
            "phone_number": user.phone_number,
            "residence_place": rider.residence_place,
            "created_at": rider.created_at
        })
    
    return result


def update_driver_account_status(
    session: Session, 
    driver_id: str, 
    account_status: str
) -> Dict[str, Any]:
    """
    Update driver account status.
    
    Args:
        session: Database session
        driver_id: ID of the driver to update
        account_status: New account status
        
    Returns:
        Dict with success/failure and message
    """
    try:
        # Get driver by ID
        driver = session.get(Driver, driver_id)
        
        if not driver:
            return {
                "success": False,
                "message": "Driver not found"
            }
        
        # Validate account status value
        valid_statuses = ["locked", "verified", "banned"]
        if account_status not in valid_statuses:
            return {
                "success": False,
                "message": f"Invalid account status. Must be one of: {', '.join(valid_statuses)}"
            }
        
        # Update account status
        driver.account_status = account_status
        session.add(driver)
        session.commit()
        session.refresh(driver)
        
        return {
            "success": True,
            "message": f"Driver account status updated to {account_status}"
        }
        
    except Exception as e:
        logger.error(f"Failed to update driver account status: {str(e)}")
        session.rollback()
        return {
            "success": False,
            "message": f"Failed to update driver account status: {str(e)}"
        }


def get_user_by_auth_id(session: Session, auth_id: str) -> Optional[User]:
    """
    Get user by auth ID or email.
    
    Args:
        session: Database session
        auth_id: Auth user ID or email
        
    Returns:
        User or None if not found
    """
    # Try to find by auth_id first
    user = session.exec(
        select(User).where(User.auth_id == auth_id)
    ).first()
    
    if user:
        return user
        
    # If not found by auth_id, try by email (for JWT tokens that use email as identifier)
    return session.exec(
        select(User).where(User.email == auth_id)
    ).first()


def get_driver_by_id(session: Session, driver_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific driver by ID with all details including document files.
    
    Args:
        session: Database session
        driver_id: Driver ID
        
    Returns:
        Driver data with document URLs or None if not found
    """
    # Query driver with join to user
    driver_with_user = session.exec(
        select(Driver, User)
        .join(User, Driver.user_id == User.id)
        .where(Driver.id == driver_id)
    ).first()
    
    if not driver_with_user:
        return None
        
    driver, user = driver_with_user
    
    # For debugging purposes, log the actual values of id_card and driver_license
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Driver {driver_id} document files - ID Card: {driver.id_card}, Driver License: {driver.driver_license}")
    
    from src.core.settings import settings
    
    # Get Supabase URL for building document URLs
    supabase_url = settings.supabase_url
    bucket_name = settings.supabase_storage_bucket
    
    # Construct full URLs for documents if they exist
    id_card_url = None
    driver_license_url = None
    
    if driver.id_card:
        # Check if it's already a full URL or just a path
        if driver.id_card.startswith('http'):
            id_card_url = driver.id_card
        else:
            # Construct Supabase storage URL
            id_card_url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/{driver.id_card}"
            
    if driver.driver_license:
        # Check if it's already a full URL or just a path
        if driver.driver_license.startswith('http'):
            driver_license_url = driver.driver_license
        else:
            # Construct Supabase storage URL
            driver_license_url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/{driver.driver_license}"
    
    return {
        "id": driver.id,
        "name": user.name,
        "email": user.email,
        "phone_number": user.phone_number,
        "taxi_number": driver.taxi_number,
        "account_status": driver.account_status,
        "driver_status": driver.driver_status,
        "id_card": id_card_url,
        "driver_license": driver_license_url,
        "created_at": driver.created_at
    }
