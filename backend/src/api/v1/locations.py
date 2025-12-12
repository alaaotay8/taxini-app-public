"""
Location tracking API endpoints.

Provides REST API for location updates and retrieval.
"""

from typing import List, Optional
from fastapi import Query
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from src.models.location import Location, LocationUpdate, LocationResponse
from src.services.location import LocationService
from src.db.session import get_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/locations", tags=["locations"])


@router.post("/update/{user_id}")
async def update_location(
    user_id: str,
    location_data: LocationUpdate,
    session: Session = Depends(get_session)
) -> dict:
    """
    Update location for a specific user.
    
    Args:
        user_id: User ID to update location for
        location_data: New location coordinates
        session: Database session
        
    Returns:
        Success response with updated location
    """
    try:
        result = LocationService.upsert_location(
            session=session,
            user_id=user_id,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            role=location_data.role or "driver"
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return {
            "success": True,
            "message": "Location updated successfully",
            "location": {
                "id": result["location"].id,
                "user_id": result["location"].user_id,
                "latitude": result["location"].latitude,
                "longitude": result["location"].longitude,
                "role": result["location"].role,
                "updated_at": result["location"].updated_at.isoformat() if result["location"].updated_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update location for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/user/{user_id}")
async def get_user_location(
    user_id: str,
    session: Session = Depends(get_session)
) -> Optional[LocationResponse]:
    """
    Get current location for a specific user.
    
    Args:
        user_id: User ID to get location for
        session: Database session
        
    Returns:
        User's current location or None if not found
    """
    try:
        location = LocationService.get_user_location(session, user_id)
        
        if not location:
            raise HTTPException(status_code=404, detail="Location not found for user")
        
        return LocationResponse(
            id=location.id,
            user_id=location.user_id,
            latitude=location.latitude,
            longitude=location.longitude,
            role=location.role,
            created_at=location.created_at.isoformat(),
            updated_at=location.updated_at.isoformat() if location.updated_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get location for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/drivers")
async def get_all_active_drivers(
    session: Session = Depends(get_session),
    latitude: float = Query(..., description="Latitude of the rider for proximity search"),
    longitude: float = Query(..., description="Longitude of the rider for proximity search")
) -> dict:

    try:
        locations = LocationService.get_all_active_drivers(session)
        drivers = []
        from src.models.user import User, Driver
        for loc in locations:
            user = session.exec(select(User).where(User.id == loc.user_id)).first()
            if not user:
                continue
            
            # Get driver profile for taxi_number and rating
            driver = session.exec(select(Driver).where(Driver.user_id == loc.user_id)).first()
            
            # Calculate distance from rider to driver
            distance_km = round(LocationService.haversine(latitude, longitude, loc.latitude, loc.longitude), 2)
            
            driver_info = {
                "id": loc.id,
                "user_id": loc.user_id,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "role": loc.role,
                "created_at": loc.created_at.isoformat(),
                "updated_at": loc.updated_at.isoformat() if loc.updated_at else None,
                "name": user.name,
                "taxi_number": driver.taxi_number if driver else "N/A",
                "rating": 0.0,  # TODO: Implement rating system
                "distance_km": distance_km
            }
            drivers.append(driver_info)

        # Filter drivers within 5km, sort by distance, and limit to 5 nearest
        max_distance_km = 5  # Only show drivers within 5km
        max_drivers = 5  # Maximum 5 drivers to show
        
        nearby_drivers = [d for d in drivers if d["distance_km"] <= max_distance_km]
        nearby_drivers = sorted(nearby_drivers, key=lambda d: d["distance_km"])
        
        # Limit to maximum 5 nearest drivers
        nearby_drivers = nearby_drivers[:max_drivers]

        if not nearby_drivers:
            return {
                "success": False,
                "message": "No drivers found within 5km of your location.",
                "total": 0,
                "drivers": []
            }

        total = len(nearby_drivers)
        return {
            "success": True,
            "message": f"Found {total} driver(s) within 5km of your location.",
            "total": total,
            "drivers": nearby_drivers
        }
    except Exception as e:
        logger.error(f"Failed to get active drivers: {str(e)}")
        return {
            "success": False,
            "message": "Internal server error.",
            "total": 0,
            "drivers": []
        }


@router.delete("/user/{user_id}")
async def delete_user_location(
    user_id: str,
    session: Session = Depends(get_session)
) -> dict:
    """
    Delete location for a specific user.
    
    Args:
        user_id: User ID to delete location for
        session: Database session
        
    Returns:
        Success response
    """
    try:
        location = LocationService.get_user_location(session, user_id)
        
        if not location:
            raise HTTPException(status_code=404, detail="Location not found for user")
        
        session.delete(location)
        session.commit()
        
        logger.info(f"Deleted location for user {user_id}")
        
        return {
            "success": True,
            "message": "Location deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete location for user {user_id}: {str(e)}")
        session.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
