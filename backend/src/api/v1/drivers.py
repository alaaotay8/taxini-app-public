"""
Driver management API endpoints.

Provides comprehensive REST API for driver operations including:
- Basic status management (admin features)
- Real-time GPS streaming and notifications 
- Trip management and acceptance/rejection
- Trip history and active trip tracking

Combines both admin functionality and command platform features.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlmodel import Session, select, func, or_, and_
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import logging
import math

from src.models.user import Driver, User
from src.models.location import Location
from src.db.session import get_session
from src.schemas.auth import CurrentUser
from src.services.auth import AuthService
from src.schemas.user import DriverStatusUpdate, DriverStatusResponse
from src.core.settings import Settings
from src.services.geocoding import GeocodingService

settings = Settings()

# Import trip-related dependencies only if they exist
try:
    from src.models.trip import Trip
    from src.services.realtime_location import RealtimeLocationService
    from src.services.notification import NotificationService
    from src.services.trip import TripService
    TRIP_FEATURES_AVAILABLE = True
except ImportError:
    TRIP_FEATURES_AVAILABLE = False
    logger.warning("Trip features not available - some endpoints will be disabled")

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/drivers", tags=["drivers"])


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def calculate_distance_from_driver(session: Session, driver_id: str, trip: Trip) -> float:
    """
    Calculate distance in kilometers from driver's current location to trip pickup point.
    Uses Haversine formula for great-circle distance.
    
    Args:
        session: Database session for querying driver location
        driver_id: Driver's user ID
        trip: Trip object with pickup_latitude and pickup_longitude
    
    Returns:
        Distance in kilometers, rounded to 2 decimal places, or 0.0 if location unavailable
    """
    # Get driver's latest location from locations table
    driver_location = session.exec(
        select(Location)
        .where(Location.user_id == driver_id)
        .where(Location.role == "driver")
        .order_by(Location.updated_at.desc())
    ).first()
    
    if not driver_location or not all([trip.pickup_latitude, trip.pickup_longitude]):
        return 0.0
    
    # Haversine formula
    R = 6371  # Earth's radius in kilometers
    
    lat1 = math.radians(driver_location.latitude)
    lat2 = math.radians(trip.pickup_latitude)
    delta_lat = math.radians(trip.pickup_latitude - driver_location.latitude)
    delta_lon = math.radians(trip.pickup_longitude - driver_location.longitude)
    
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c
    
    return round(distance, 2)


# =============================================================================
# REQUEST/RESPONSE MODELS FOR TRIP FEATURES
# =============================================================================

class TripActionRequest(BaseModel):
    """Request model for trip acceptance/rejection."""
    action: str = Field(..., pattern="^(accept|reject)$", description="Action to take: accept or reject")
    trip_id: str = Field(..., min_length=1, max_length=100, description="Trip ID")
    notes: Optional[str] = Field(None, max_length=1000, description="Optional notes")


class TripActionResponse(BaseModel):
    """Response model for trip actions."""
    success: bool
    message: str
    trip_id: str
    action: str
    driver_status: Optional[str] = None
    details: Optional[dict] = None


class TripStatusUpdateRequest(BaseModel):
    """Request model for trip status updates."""
    trip_id: str = Field(..., min_length=1, max_length=100, description="Trip ID")
    status: str = Field(..., pattern="^(started|completed)$", description="New status: started or completed")
    notes: Optional[str] = Field(None, max_length=1000, description="Optional notes")


class TripStatusUpdateResponse(BaseModel):
    """Response model for trip status updates."""
    success: bool
    message: str
    trip_id: str
    old_status: str
    new_status: str
    updated_at: str


# =============================================================================
# CORE DRIVER STATUS MANAGEMENT (ADMIN + COMMAND FEATURES)
# =============================================================================

@router.put("/status")
async def update_driver_status(
    status_update: DriverStatusUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> DriverStatusResponse:
    """
    Update driver status (online/offline/on_trip).
    
    Enhanced version that combines admin functionality with command features.
    Includes streaming status if real-time features are available.
    """
    try:
        # Handle development vs production mode for user lookup
        from src.core.settings import settings
        
        if settings.development_mode:
            user = session.exec(select(User).where(User.id == current_user.auth_id)).first()
        else:
            user = session.exec(select(User).where(User.auth_id == current_user.auth_id)).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get driver
        driver = session.exec(
            select(Driver).where(Driver.user_id == user.id)
        ).first()
        
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        # Update status
        driver.driver_status = status_update.status.value
        session.add(driver)
        session.commit()
        session.refresh(driver)
        
        # Check streaming status if available
        streaming_active = False
        if TRIP_FEATURES_AVAILABLE:
            try:
                streaming_active = RealtimeLocationService.is_driver_streaming(driver.id)
            except:
                streaming_active = False
        
        return DriverStatusResponse(
            success=True,
            message=f"Driver status updated to {status_update.status.value}",
            driver_id=driver.id,
            status=status_update.status,
            streaming_active=streaming_active
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update driver status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/me")
async def get_driver_profile(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
):
    """
    Get the current driver's profile including account status.
    """
    try:
        # Handle development vs production mode for user lookup
        from src.core.settings import settings
        
        if settings.development_mode:
            user = session.exec(select(User).where(User.id == current_user.auth_id)).first()
        else:
            user = session.exec(select(User).where(User.auth_id == current_user.auth_id)).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get driver profile
        driver = session.exec(
            select(Driver).where(Driver.user_id == user.id)
        ).first()
        
        if not driver:
            raise HTTPException(status_code=404, detail="Driver profile not found")
        
        return {
            "success": True,
            "driver": {
                "id": str(driver.id),
                "user_id": str(driver.user_id),
                "taxi_number": driver.taxi_number,
                "account_status": driver.account_status,  # locked, verified, banned
                "driver_status": driver.driver_status,    # offline, online, on_trip
            },
            "user": {
                "id": str(user.id),
                "name": user.name,
                "phone_number": user.phone_number,
                "email": user.email
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"Failed to get driver profile: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/status")
async def get_driver_status(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> dict:
    """
    Get current driver status.
    
    Enhanced version that includes additional user information and streaming status.
    """
    try:
        # Handle development vs production mode for user lookup
        from src.core.settings import settings
        
        if settings.development_mode:
            user = session.exec(select(User).where(User.id == current_user.auth_id)).first()
        else:
            user = session.exec(select(User).where(User.auth_id == current_user.auth_id)).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get driver record
        driver = session.exec(
            select(Driver).where(Driver.user_id == user.id)
        ).first()
        
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        # Base response (admin features)
        response = {
            "success": True,
            "driver_id": driver.id,
            "status": driver.driver_status,
            "account_status": driver.account_status,
            "user": {
                "name": user.name,
                "phone": user.phone_number
            }
        }
        
        # Add streaming status if command features available
        if TRIP_FEATURES_AVAILABLE:
            try:
                response["streaming_active"] = RealtimeLocationService.is_driver_streaming(driver.id)
            except:
                response["streaming_active"] = False
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get driver status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# GPS STREAMING (COMMAND FEATURES)
# =============================================================================

@router.post("/streaming/start")
async def start_streaming(
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> dict:
    """
    Start real-time GPS streaming for the authenticated driver.
    Automatically sets driver status to ONLINE.
    """
    if not TRIP_FEATURES_AVAILABLE:
        raise HTTPException(
            status_code=501, 
            detail="GPS streaming features not available in this deployment"
        )
    
    try:
        # First find the user by auth_id, then find their driver profile
        user = session.exec(
            select(User).where(User.auth_id == current_user.auth_id)
        ).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Now find driver profile by user_id
        driver = session.exec(
            select(Driver).where(Driver.user_id == user.id)
        ).first()
        
        if not driver:
            raise HTTPException(status_code=404, detail="Driver profile not found")
        
        driver_id = driver.id
        
        # Update driver status to ONLINE
        driver.driver_status = "online"
        session.add(driver)
        session.commit()
        session.refresh(driver)
        
        # Start real-time streaming
        background_tasks.add_task(
            RealtimeLocationService.start_driver_streaming,
            driver_id
        )
        
        logger.info(f"Started GPS streaming for driver {driver_id}, status set to online")
        
        return {
            "success": True,
            "message": "GPS streaming started, driver status set to online",
            "driver_id": driver_id,
            "status": driver.driver_status,
            "channel": f"driver_{driver_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start streaming: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/streaming/stop")
async def stop_streaming(
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> dict:
    """
    Stop real-time GPS streaming for the authenticated driver.
    Automatically sets driver status to OFFLINE.
    """
    if not TRIP_FEATURES_AVAILABLE:
        raise HTTPException(
            status_code=501, 
            detail="GPS streaming features not available in this deployment"
        )
    
    try:
        # First find the user by auth_id, then find their driver profile
        user = session.exec(
            select(User).where(User.auth_id == current_user.auth_id)
        ).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Now find driver profile by user_id
        driver = session.exec(
            select(Driver).where(Driver.user_id == user.id)
        ).first()
        
        if not driver:
            raise HTTPException(status_code=404, detail="Driver profile not found")
        
        driver_id = driver.id
        
        # Update driver status to OFFLINE
        driver.driver_status = "offline"
        session.add(driver)
        session.commit()
        session.refresh(driver)
        
        # Stop real-time streaming
        background_tasks.add_task(
            RealtimeLocationService.stop_driver_streaming,
            driver_id
        )
        
        logger.info(f"Stopped GPS streaming for driver {driver_id}, status set to offline")
        
        return {
            "success": True,
            "message": "GPS streaming stopped, driver status set to offline",
            "driver_id": driver_id,
            "status": driver.driver_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop streaming: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# NOTIFICATIONS (COMMAND FEATURES)
# =============================================================================

@router.post("/notifications/connect")
async def connect_to_notifications(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> dict:
    """Connect driver to trip notifications via GPS streaming channel."""
    if not TRIP_FEATURES_AVAILABLE:
        raise HTTPException(
            status_code=501, 
            detail="Notification features not available in this deployment"
        )
    
    try:
        user = session.exec(
            select(User).where(User.auth_id == current_user.auth_id)
        ).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        driver = session.exec(
            select(Driver).where(Driver.user_id == user.id)
        ).first()
        
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        result = await NotificationService.connect_driver(driver.id)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to connect to notifications: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/notifications/disconnect")
async def disconnect_from_notifications(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> dict:
    """Disconnect driver from trip notifications."""
    if not TRIP_FEATURES_AVAILABLE:
        raise HTTPException(
            status_code=501, 
            detail="Notification features not available in this deployment"
        )
    
    try:
        user = session.exec(
            select(User).where(User.auth_id == current_user.auth_id)
        ).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        driver = session.exec(
            select(Driver).where(Driver.user_id == user.id)
        ).first()
        
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        result = await NotificationService.disconnect_driver(driver.id)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to disconnect from notifications: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/notifications/status")
async def get_notification_status(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> dict:
    """Get notification connection status and pending notifications."""
    if not TRIP_FEATURES_AVAILABLE:
        raise HTTPException(
            status_code=501, 
            detail="Notification features not available in this deployment"
        )
    
    try:
        user = session.exec(
            select(User).where(User.auth_id == current_user.auth_id)
        ).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        driver = session.exec(
            select(Driver).where(Driver.user_id == user.id)
        ).first()
        
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        streaming_status = RealtimeLocationService.get_streaming_status(driver.id)
        is_streaming = RealtimeLocationService.is_driver_streaming(driver.id)
        
        pending_notifications = NotificationService.get_pending_notifications()
        driver_pending = pending_notifications.get(driver.id)
        
        return {
            "driver_id": driver.id,
            "driver_name": user.name,
            "gps_streaming": {
                "active": is_streaming,
                "status": streaming_status,
                "channel": f"driver_{driver.id}" if is_streaming else None
            },
            "notifications": {
                "connected": is_streaming,
                "pending_count": 1 if driver_pending else 0,
                "pending_notification": {
                    "trip_id": driver_pending["trip_id"],
                    "created_at": driver_pending["created_at"].isoformat(),
                } if driver_pending else None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notification status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# TRIP MANAGEMENT (COMMAND FEATURES)
# =============================================================================

@router.post("/trip-action")
async def handle_trip_action(
    action_request: TripActionRequest,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> TripActionResponse:
    """Handle driver accepting or rejecting a trip request."""
    if not TRIP_FEATURES_AVAILABLE:
        raise HTTPException(
            status_code=501, 
            detail="Trip management features not available in this deployment"
        )
    
    try:
        # Handle development vs production mode for user lookup
        from src.core.settings import settings
        
        if settings.development_mode:
            user = session.exec(select(User).where(User.id == current_user.auth_id)).first()
        else:
            user = session.exec(select(User).where(User.auth_id == current_user.auth_id)).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if action_request.action not in ["accept", "reject"]:
            raise HTTPException(
                status_code=400, 
                detail="Invalid action. Must be 'accept' or 'reject'"
            )
        
        driver = session.exec(
            select(Driver).where(Driver.user_id == user.id)
        ).first()
        
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        trip = session.exec(
            select(Trip).where(Trip.id == action_request.trip_id)
        ).first()
        
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        # Check trip status and driver assignment
        if trip.driver_id is not None and trip.driver_id != driver.user_id:
            # Trip is already assigned to another driver
            raise HTTPException(
                status_code=403, 
                detail="Trip is already assigned to another driver"
            )
        
        if action_request.action == "accept":
            # CRITICAL: Use database-level locking to prevent race condition
            # Re-fetch trip with FOR UPDATE lock to ensure atomic operation
            trip_locked = session.exec(
                select(Trip).where(Trip.id == action_request.trip_id).with_for_update()
            ).first()
            
            if not trip_locked:
                raise HTTPException(status_code=404, detail="Trip not found")
            
            # Check if trip is still available after acquiring lock
            if trip_locked.driver_id is not None and trip_locked.driver_id != driver.user_id:
                session.rollback()
                raise HTTPException(
                    status_code=409, 
                    detail="Trip was just accepted by another driver"
                )
            
            if trip_locked.status in ["cancelled", "completed"]:
                session.rollback()
                raise HTTPException(
                    status_code=400, 
                    detail=f"Trip is {trip_locked.status} and cannot be accepted"
                )
            
            # If trip has no driver, assign this driver atomically
            if trip_locked.driver_id is None:
                trip_locked.driver_id = driver.user_id
                trip_locked.status = "assigned"
                trip_locked.assigned_at = datetime.utcnow()
                session.add(trip_locked)
                session.commit()
                session.refresh(trip_locked)
                logger.info(f"✅ Trip {trip_locked.id} assigned to driver {driver.user_id}")
            
            # Now handle acceptance
            result = await TripService.handle_driver_acceptance(
                session=session,
                driver_id=driver.id,
                trip_id=action_request.trip_id,
                notes=action_request.notes
            )
            
            if not result["success"]:
                raise HTTPException(status_code=400, detail=result["message"])
            
            logger.info(f"✅ Driver {driver.id} ({user.name}) accepted trip {action_request.trip_id}")
            
            return TripActionResponse(
                success=True,
                message=result["message"],
                trip_id=action_request.trip_id,
                action="accept",
                driver_status=result.get("new_driver_status"),
                details={
                    "driver_name": result.get("driver_name"),
                    "rider_name": result.get("rider_name"),
                    "pickup_address": result.get("pickup_address"),
                    "destination_address": result.get("destination_address"),
                    "estimated_cost_tnd": result.get("estimated_cost_tnd")
                }
            )
            
        elif action_request.action == "reject":
            logger.info(f"🚫 REJECT ACTION: Driver {driver.user_id} ({user.name}) rejecting trip {trip.id}")
            logger.info(f"📊 Trip status BEFORE reject: driver_id={trip.driver_id}, status={trip.status}")
            
            # If trip has no driver yet, driver is declining to pick it up
            # Cancel the trip so the rider is notified
            if trip.driver_id is None:
                logger.info(f"Driver {driver.user_id} ({user.name}) declined unassigned trip {trip.id} - cancelling for rider")
                
                # Cancel the trip
                trip.status = "cancelled"
                trip.cancelled_at = datetime.utcnow()
                trip.cancellation_reason = "Driver declined the trip request"
                session.add(trip)
                session.commit()
                
                # Send notification to rider about trip cancellation
                try:
                    from src.services.notification import NotificationService
                    notification = {
                        "type": "trip_cancelled",
                        "trip_id": trip.id,
                        "reason": "Driver declined the trip request",
                        "message": "The driver declined your trip request. Please try selecting another driver.",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await NotificationService._send_rider_notification(trip.rider_id, notification)
                    logger.info(f"📱 Sent decline notification to rider {trip.rider_id}")
                except Exception as e:
                    logger.error(f"Failed to send decline notification to rider: {e}")
                
                return TripActionResponse(
                    success=True,
                    message="Trip request declined and cancelled",
                    trip_id=action_request.trip_id,
                    action="reject",
                    driver_status="online",
                    details={"note": "Trip cancelled for rider"}
                )
            
            # Trip was already assigned to this driver, handle rejection
            result = await TripService.handle_driver_rejection(
                session=session,
                driver_id=driver.id,
                trip_id=action_request.trip_id,
                notes=action_request.notes
            )
            
            if not result["success"]:
                raise HTTPException(status_code=400, detail=result["message"])
            
            logger.info(f"❌ Driver {driver.id} ({user.name}) rejected trip {action_request.trip_id}")
            
            message = "Trip rejected and cancelled - no more available drivers" if result.get("trip_cancelled") else "Trip rejected and reassigned to next available driver"
            
            return TripActionResponse(
                success=True,
                message=message,
                trip_id=action_request.trip_id,
                action="reject",
                driver_status="online",
                details={
                    "rejecting_driver": result.get("rejecting_driver"),
                    "new_assignment": result.get("new_assignment"),
                    "trip_cancelled": result.get("trip_cancelled", False)
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling trip action: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/trip-status")
async def update_trip_status(
    status_request: TripStatusUpdateRequest,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> TripStatusUpdateResponse:
    """Update trip status during the journey (started/completed)."""
    if not TRIP_FEATURES_AVAILABLE:
        raise HTTPException(
            status_code=501, 
            detail="Trip management features not available in this deployment"
        )
    
    try:
        # Handle development vs production mode for user lookup
        from src.core.settings import settings
        
        if settings.development_mode:
            user = session.exec(select(User).where(User.id == current_user.auth_id)).first()
        else:
            user = session.exec(select(User).where(User.auth_id == current_user.auth_id)).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        driver = session.exec(
            select(Driver).where(Driver.user_id == user.id)
        ).first()
        
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        trip = session.exec(
            select(Trip).where(Trip.id == status_request.trip_id)
        ).first()
        
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        if trip.driver_id != driver.user_id:
            raise HTTPException(
                status_code=403, 
                detail="Trip is not assigned to this driver"
            )
        
        old_status = trip.status
        
        # Validate status transitions
        valid_transitions = {
            "accepted": ["started"],
            "started": ["completed"]
        }
        
        if old_status not in valid_transitions:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot update trip from status '{old_status}'"
            )
        
        if status_request.status not in valid_transitions[old_status]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status transition from '{old_status}' to '{status_request.status}'. Valid transitions: {valid_transitions[old_status]}"
            )
        
        # Additional validation for starting trip - require rider confirmation
        if status_request.status == "started" and not trip.rider_confirmed_pickup:
            raise HTTPException(
                status_code=400,
                detail="Cannot start trip: Rider has not confirmed pickup yet. Please wait for rider confirmation."
            )
        
        # Update trip status
        trip.status = status_request.status
        
        if status_request.status == "started":
            trip.started_at = datetime.utcnow()
        elif status_request.status == "completed":
            trip.completed_at = datetime.utcnow()
            
            # Set final trip cost (use estimated cost if total_cost not set)
            if not trip.total_cost_tnd:
                trip.total_cost_tnd = trip.estimated_cost_tnd
            
            # Set driver back to online when trip is completed
            driver.driver_status = "online"
            session.add(driver)
            
            # Send notification to rider to confirm completion and rate driver
            try:
                await NotificationService.send_trip_notification(
                    user_id=trip.rider_id,
                    notification_type="trip_completed",
                    trip_data={
                        "trip_id": trip.id,
                        "message": "Your trip has been completed!",
                        "driver_name": user.name,
                        "pickup_address": trip.pickup_address,
                        "destination_address": trip.destination_address,
                        "total_cost": trip.total_cost_tnd or trip.estimated_cost_tnd,
                        "action_required": "Please confirm completion and rate your driver"
                    }
                )
                logger.info(f"🔔 Sent trip completion notification to rider {trip.rider_id}")
            except Exception as e:
                logger.error(f"Failed to send completion notification to rider: {e}")
        
        if status_request.notes:
            trip.driver_notes = status_request.notes
        
        session.add(trip)
        session.commit()
        session.refresh(trip)
        
        logger.info(f"🚗 Trip {trip.id} status updated: {old_status} → {status_request.status} by driver {driver.id}")
        
        return TripStatusUpdateResponse(
            success=True,
            message=f"Trip status updated from '{old_status}' to '{status_request.status}'",
            trip_id=status_request.trip_id,
            old_status=old_status,
            new_status=status_request.status,
            updated_at=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating trip status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/trip-history")
async def get_driver_trip_history(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> dict:
    """Get driver's trip history with optional filtering."""
    if not TRIP_FEATURES_AVAILABLE:
        raise HTTPException(
            status_code=501, 
            detail="Trip management features not available in this deployment"
        )
    
    try:
        user = session.exec(
            select(User).where(User.auth_id == current_user.auth_id)
        ).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        driver = session.exec(
            select(Driver).where(Driver.user_id == user.id)
        ).first()
        
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        # Build query for trips assigned to this driver
        query = (
            select(Trip)
            .where(Trip.driver_id == driver.user_id)
            .order_by(Trip.created_at.desc())
        )
        
        if status:
            query = query.where(Trip.status == status)
        
        trips = session.exec(query.offset(offset).limit(limit)).all()
        
        # Initialize geocoding service
        geocoding_service = GeocodingService()
        
        trip_list = []
        for trip in trips:
            rider = session.exec(
                select(User).where(User.id == trip.rider_id)
            ).first()
            
            # Geocode addresses using optimized Mapbox API
            pickup_addr = trip.pickup_address
            dest_addr = trip.destination_address
            
            # Geocode if addresses are missing
            if not pickup_addr and trip.pickup_latitude and trip.pickup_longitude:
                pickup_addr = await geocoding_service.reverse_geocode(
                    trip.pickup_latitude, 
                    trip.pickup_longitude,
                    include_coords=True
                )
            
            if not dest_addr and trip.destination_latitude and trip.destination_longitude:
                dest_addr = await geocoding_service.reverse_geocode(
                    trip.destination_latitude,
                    trip.destination_longitude,
                    include_coords=True
                )
            
            trip_list.append({
                "id": trip.id,
                "status": trip.status,
                "trip_type": trip.trip_type,
                "pickup_address": pickup_addr,
                "pickup_latitude": trip.pickup_latitude,
                "pickup_longitude": trip.pickup_longitude,
                "destination_address": dest_addr,
                "destination_latitude": trip.destination_latitude,
                "destination_longitude": trip.destination_longitude,
                "estimated_distance_km": trip.estimated_distance_km,
                "estimated_cost_tnd": trip.estimated_cost_tnd,
                "requested_at": trip.requested_at.isoformat() if trip.requested_at else None,
                "assigned_at": trip.assigned_at.isoformat() if trip.assigned_at else None,
                "accepted_at": trip.accepted_at.isoformat() if trip.accepted_at else None,
                "started_at": trip.started_at.isoformat() if trip.started_at else None,
                "completed_at": trip.completed_at.isoformat() if trip.completed_at else None,
                "cancelled_at": trip.cancelled_at.isoformat() if trip.cancelled_at else None,
                "rider_name": rider.name if rider else "Unknown",
                "rider_notes": trip.rider_notes,
                "driver_notes": trip.driver_notes,
                "rider_rating": trip.rider_rating,
                "driver_rating": trip.driver_rating
            })
        
        return {
            "success": True,
            "trips": trip_list,
            "total_returned": len(trip_list),
            "offset": offset,
            "limit": limit,
            "filter_status": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting driver trip history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/earnings")
async def get_driver_earnings(
    period: str = Query("today", regex="^(today|week|month)$"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> dict:
    """
    Get driver's earnings summary for specified period.
    
    Args:
        period: Time period - 'today', 'week', or 'month'
        session: Database session
        current_user: Authenticated driver
    
    Returns:
        Detailed earnings breakdown including total fare, commission, and net earnings
    """
    if not TRIP_FEATURES_AVAILABLE:
        raise HTTPException(
            status_code=501, 
            detail="Trip management features not available in this deployment"
        )
    
    try:
        user = session.exec(
            select(User).where(User.auth_id == current_user.auth_id)
        ).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        driver = session.exec(
            select(Driver).where(Driver.user_id == user.id)
        ).first()
        
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        # Calculate date range based on period
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        
        if period == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_date = now - timedelta(days=7)
        else:  # month
            start_date = now - timedelta(days=30)
        
        # Get completed trips in the period
        completed_trips = session.exec(
            select(Trip)
            .where(
                and_(
                    Trip.driver_id == driver.user_id,
                    Trip.status == "completed",
                    Trip.completed_at >= start_date
                )
            )
        ).all()
        
        # Calculate earnings
        total_fare = sum(trip.total_cost_tnd or 0 for trip in completed_trips)
        total_trips = len(completed_trips)
        
        # Use default commission rate (20%)
        # TODO: Move to platform settings when settings table is implemented
        commission_rate = 20.0
        
        commission = (total_fare * commission_rate) / 100
        net_earnings = total_fare - commission
        
        # Calculate average rating
        rated_trips = [trip for trip in completed_trips if trip.driver_rating is not None]
        avg_rating = (sum(trip.driver_rating for trip in rated_trips) / len(rated_trips)) if rated_trips else 0.0
        
        # Calculate total distance
        total_distance = sum(trip.estimated_distance_km or 0 for trip in completed_trips)
        
        # Calculate peak hours data
        peak_hours = {
            "morning": {"trips": 0, "earnings": 0.0, "hours": 0.0},  # 6AM-12PM
            "afternoon": {"trips": 0, "earnings": 0.0, "hours": 0.0},  # 12PM-6PM
            "evening": {"trips": 0, "earnings": 0.0, "hours": 0.0},  # 6PM-12AM
            "night": {"trips": 0, "earnings": 0.0, "hours": 0.0}  # 12AM-6AM
        }
        
        for trip in completed_trips:
            if trip.completed_at:
                hour = trip.completed_at.hour
                earnings = (trip.total_cost_tnd or 0) * (1 - commission_rate / 100)
                
                # Calculate trip duration in hours
                trip_hours = 0
                if trip.started_at and trip.completed_at:
                    trip_hours = (trip.completed_at - trip.started_at).total_seconds() / 3600
                
                if 6 <= hour < 12:
                    peak_hours["morning"]["trips"] += 1
                    peak_hours["morning"]["earnings"] += earnings
                    peak_hours["morning"]["hours"] += trip_hours
                elif 12 <= hour < 18:
                    peak_hours["afternoon"]["trips"] += 1
                    peak_hours["afternoon"]["earnings"] += earnings
                    peak_hours["afternoon"]["hours"] += trip_hours
                elif 18 <= hour < 24:
                    peak_hours["evening"]["trips"] += 1
                    peak_hours["evening"]["earnings"] += earnings
                    peak_hours["evening"]["hours"] += trip_hours
                else:
                    peak_hours["night"]["trips"] += 1
                    peak_hours["night"]["earnings"] += earnings
                    peak_hours["night"]["hours"] += trip_hours
        
        # Round earnings and hours values
        for period_key in peak_hours:
            peak_hours[period_key]["earnings"] = round(peak_hours[period_key]["earnings"], 2)
            peak_hours[period_key]["hours"] = round(peak_hours[period_key]["hours"], 2)
        
        # Calculate online hours for today (estimate from trip times)
        online_hours = 0.0
        if period == "today":
            for trip in completed_trips:
                if trip.started_at and trip.completed_at:
                    duration = (trip.completed_at - trip.started_at).total_seconds() / 3600
                    online_hours += duration
            # Add buffer time between trips (assume 10 min between each trip)
            online_hours += (total_trips * 10 / 60) if total_trips > 0 else 0
        
        return {
            "success": True,
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": now.isoformat(),
            "total_trips": total_trips,
            "online_hours": round(online_hours, 1),
            "total_fare": round(total_fare, 2),
            "commission_rate": commission_rate,
            "commission": round(commission, 2),
            "net_earnings": round(net_earnings, 2),
            "average_rating": round(avg_rating, 2) if avg_rating > 0 else 0.0,
            "avg_rating": round(avg_rating, 2) if avg_rating > 0 else 0.0,  # Frontend expects this
            "total_distance_km": round(total_distance, 2),
            "avg_fare_per_trip": round(total_fare / total_trips, 2) if total_trips > 0 else 0,
            "peak_hours": peak_hours
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting driver earnings: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/active-trip")
async def get_driver_active_trip(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> dict:
    """Get the active trip for the authenticated driver."""
    if not TRIP_FEATURES_AVAILABLE:
        raise HTTPException(
            status_code=501, 
            detail="Trip management features not available in this deployment"
        )
    
    try:
        logger.info(f"🔍 Checking active trip for auth_id: {current_user.auth_id}")
        user = session.exec(
            select(User).where(User.auth_id == current_user.auth_id)
        ).first()
        
        if not user:
            logger.error(f"❌ User not found for auth_id: {current_user.auth_id}")
            raise HTTPException(status_code=404, detail="User not found")

        logger.info(f"✅ User found: {user.id}, role: {user.role}")
        driver = session.exec(
            select(Driver).where(Driver.user_id == user.id)
        ).first()
        
        if not driver:
            logger.error(f"❌ Driver profile not found for user_id: {user.id}")
            raise HTTPException(status_code=404, detail="Driver not found")
        
        logger.info(f"✅ Driver found: {driver.id}")
        
        trip = TripService.get_driver_active_trip(session, driver.id)
        
        # Double-check trip is not cancelled (extra safety)
        if trip and trip.status == "cancelled":
            trip = None
        
        if not trip:
            return {
                "has_active_trip": False,
                "message": "No active trip found for driver"
            }
        
        rider = session.exec(
            select(User).where(User.id == trip.rider_id)
        ).first()
        
        # Geocode addresses if they're missing or generic
        geocoding_service = GeocodingService()
        pickup_address = trip.pickup_address
        destination_address = trip.destination_address
        
        # Check if addresses need geocoding (missing or generic placeholders)
        if not pickup_address or "Pickup Location" in pickup_address:
            try:
                pickup_address = await geocoding_service.reverse_geocode(
                    trip.pickup_latitude,
                    trip.pickup_longitude
                )
            except Exception as e:
                logger.warning(f"Failed to geocode pickup address: {e}")
                pickup_address = trip.pickup_address or f"({trip.pickup_latitude:.4f}°, {trip.pickup_longitude:.4f}°)"
        
        if not destination_address or "Destination" in destination_address:
            try:
                destination_address = await geocoding_service.reverse_geocode(
                    trip.destination_latitude,
                    trip.destination_longitude
                )
            except Exception as e:
                logger.warning(f"Failed to geocode destination address: {e}")
                destination_address = trip.destination_address or f"({trip.destination_latitude:.4f}°, {trip.destination_longitude:.4f}°)"
        
        return {
            "has_active_trip": True,
            "trip": {
                "id": trip.id,
                "status": trip.status,
                "rider_name": rider.name if rider else "Unknown",
                "pickup_address": pickup_address,
                "destination_address": destination_address,
                "pickup_latitude": trip.pickup_latitude,
                "pickup_longitude": trip.pickup_longitude,
                "destination_latitude": trip.destination_latitude,
                "destination_longitude": trip.destination_longitude,
                "estimated_distance_km": trip.estimated_distance_km,
                "estimated_cost_tnd": trip.estimated_cost_tnd,
                "trip_type": trip.trip_type,
                "requested_at": trip.requested_at.isoformat() if trip.requested_at else None,
                "accepted_at": trip.accepted_at.isoformat() if trip.accepted_at else None,
                "started_at": trip.started_at.isoformat() if trip.started_at else None,
                "completed_at": trip.completed_at.isoformat() if trip.completed_at else None,
                "rider_confirmed_pickup": trip.rider_confirmed_pickup,
                "rider_confirmed_at": trip.rider_confirmed_at.isoformat() if trip.rider_confirmed_at else None,
                "rider_notes": trip.rider_notes
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting active trip: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/pending-requests")
async def get_pending_trip_requests(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> dict:
    """Get pending trip requests assigned to the authenticated driver."""
    if not TRIP_FEATURES_AVAILABLE:
        raise HTTPException(
            status_code=501, 
            detail="Trip management features not available in this deployment"
        )
    
    try:
        from src.core.settings import settings
        
        # Get user based on development mode
        if settings.development_mode:
            user = session.exec(select(User).where(User.id == current_user.auth_id)).first()
        else:
            user = session.exec(select(User).where(User.auth_id == current_user.auth_id)).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        driver = session.exec(
            select(Driver).where(Driver.user_id == user.id)
        ).first()
        
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        # Get pending trip requests - either:
        # 1. Trips in "requested" status (no driver assigned yet - available for any driver)
        # 2. Trips in "assigned" status assigned to THIS driver (driver already accepted)
        pending_trip = session.exec(
            select(Trip)
            .where(
                or_(
                    # Show all unassigned requested trips to all drivers
                    and_(Trip.status == 'requested', Trip.driver_id.is_(None)),
                    # OR trips assigned to this specific driver
                    and_(Trip.driver_id == driver.user_id, Trip.status == 'assigned')
                )
            )
            .order_by(Trip.requested_at.desc())  # Oldest first
        ).first()
        
        if not pending_trip:
            return {
                "success": True,
                "has_request": False,
                "message": "No pending trip requests"
            }
        
        # Get rider details
        rider = session.exec(
            select(User).where(User.id == pending_trip.rider_id)
        ).first()
        
        # Calculate actual rider stats
        rider_trips_count = session.exec(
            select(func.count(Trip.id))
            .where(Trip.rider_id == pending_trip.rider_id)
            .where(Trip.status == 'completed')
        ).first() or 0
        
        # Calculate average rider rating from completed trips
        avg_rating_result = session.exec(
            select(func.avg(Trip.rider_rating))
            .where(Trip.rider_id == pending_trip.rider_id)
            .where(Trip.rider_rating.isnot(None))
        ).first()
        rider_rating = float(avg_rating_result) if avg_rating_result else None
        
        # Geocode addresses if they're missing or generic
        geocoding_service = GeocodingService()
        pickup_address = pending_trip.pickup_address
        destination_address = pending_trip.destination_address
        
        # Check if addresses need geocoding (missing or generic placeholders)
        if not pickup_address or "Pickup Location" in pickup_address:
            try:
                pickup_address = await geocoding_service.reverse_geocode(
                    pending_trip.pickup_latitude,
                    pending_trip.pickup_longitude
                )
            except Exception as e:
                logger.warning(f"Failed to geocode pickup address: {e}")
                pickup_address = pending_trip.pickup_address or f"({pending_trip.pickup_latitude:.4f}°, {pending_trip.pickup_longitude:.4f}°)"
        
        if not destination_address or "Destination" in destination_address:
            try:
                destination_address = await geocoding_service.reverse_geocode(
                    pending_trip.destination_latitude,
                    pending_trip.destination_longitude
                )
            except Exception as e:
                logger.warning(f"Failed to geocode destination address: {e}")
                destination_address = pending_trip.destination_address or f"({pending_trip.destination_latitude:.4f}°, {pending_trip.destination_longitude:.4f}°)"
        
        return {
            "success": True,
            "has_request": True,
            "trip_request": {
                "id": pending_trip.id,
                "rider_name": rider.name if rider else "Unknown",
                "rider_phone": rider.phone_number if rider else "N/A",
                "rider_rating": rider_rating,
                "rider_trips": rider_trips_count,
                "pickup_address": pickup_address,
                "destination_address": destination_address,
                "pickup_latitude": pending_trip.pickup_latitude,
                "pickup_longitude": pending_trip.pickup_longitude,
                "destination_latitude": pending_trip.destination_latitude,
                "destination_longitude": pending_trip.destination_longitude,
                "estimated_distance": pending_trip.estimated_distance_km,
                "estimated_cost": pending_trip.estimated_cost_tnd,
                "distance_from_driver": calculate_distance_from_driver(session, driver.user_id, pending_trip),
                "requested_at": pending_trip.requested_at.isoformat() if pending_trip.requested_at else None,
                "rider_notes": pending_trip.rider_notes
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pending trip requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
