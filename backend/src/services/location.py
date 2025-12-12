"""
Location tracking service for GPS coordinates.

This service handles location updates and retrieval using standard REST operations.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from src.models.location import Location, LocationUpdate
from src.models.user import User, Driver
from src.db.session import get_session

logger = logging.getLogger(__name__)


class LocationService:
    """Service for managing driver/rider location tracking."""
    
    @staticmethod
    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees).
        Uses the Haversine formula.
        
        Args:
            lat1: Latitude of first point
            lon1: Longitude of first point
            lat2: Latitude of second point
            lon2: Longitude of second point
            
        Returns:
            Distance in kilometers between the two points
        """
        import math
        R = 6371  # Radius of the earth in km
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
        
    @staticmethod
    def upsert_location(
        session: Session,
        user_id: str,
        latitude: float,
        longitude: float,
        role: str = "driver"
    ) -> Dict[str, Any]:
        """
        Update or insert location for a user.
        
        Args:
            session: Database session
            user_id: User ID from users table
            latitude: GPS latitude coordinate
            longitude: GPS longitude coordinate
            role: User role (driver/rider)
            
        Returns:
            Dict with success status and location data
        """
        try:
            # Check if user exists
            user = session.exec(select(User).where(User.id == user_id)).first()
            if not user:
                return {
                    "success": False,
                    "message": f"User with ID {user_id} not found",
                    "error": "USER_NOT_FOUND"
                }
            
            # Check if location already exists for this user
            existing_location = session.exec(
                select(Location).where(Location.user_id == user_id)
            ).first()
            
            if existing_location:
                # Update existing location
                existing_location.latitude = latitude
                existing_location.longitude = longitude
                existing_location.role = role
                # updated_at will be automatically set by TimestampMixin
                session.add(existing_location)
                location = existing_location
            else:
                # Create new location record
                location = Location(
                    user_id=user_id,
                    latitude=latitude,
                    longitude=longitude,
                    role=role
                )
                session.add(location)
            
            session.commit()
            session.refresh(location)
            
            logger.info(f"Location updated for user {user_id}: ({latitude}, {longitude})")
            
            return {
                "success": True,
                "message": "Location updated successfully",
                "location": location
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to upsert location for user {user_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to update location: {str(e)}",
                "error": str(e)
            }
    
    @staticmethod
    def get_user_location(session: Session, user_id: str) -> Optional[Location]:
        """
        Get the latest location for a specific user.
        
        Args:
            session: Database session
            user_id: User ID to get location for
            
        Returns:
            Location object or None if not found
        """
        try:
            location = session.exec(
                select(Location).where(Location.user_id == user_id)
            ).first()
            return location
        except Exception as e:
            logger.error(f"Failed to get location for user {user_id}: {str(e)}")
            return None
    
    @staticmethod
    def get_all_active_drivers(session: Session) -> List[Location]:
        """
        Get all online and verified driver locations.
        Only returns drivers with:
        - driver_status = 'online' (not offline or on_trip)
        - account_status = 'verified' (not locked or banned)
        
        Args:
            session: Database session
            
        Returns:
            List of online and verified driver locations
        """
        try:
            # Join locations with drivers table to filter by driver_status and account_status
            # Only return drivers who are:
            # 1. Online (driver_status = 'online')
            # 2. Verified (account_status = 'verified')
            query = (
                select(Location)
                .join(Driver, Location.user_id == Driver.user_id)
                .where(Location.role == "driver")
                .where(Driver.driver_status == "online")
                .where(Driver.account_status == "verified")
            )
            
            locations = session.exec(query).all()
            logger.info(f"Found {len(locations)} verified online drivers")
            return list(locations)
        except Exception as e:
            logger.error(f"Failed to get active drivers: {str(e)}")
            return []


# The LocationSimulator class has been removed as it was performing real-time database upserts
