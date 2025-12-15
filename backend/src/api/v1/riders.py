"""
Rider API endpoints.

Provides REST API for rider operations including trip planning, driver matching,
and real trip creation with Supabase Realtime notifications.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlmodel import Session, select
from pydantic import BaseModel, Field
from src.models.location import Location
from src.models.user import User, Driver
from src.models.trip import Trip
from src.services.location import LocationService
from src.services.trip import TripService
from src.schemas.auth import CurrentUser
from src.services.auth import AuthService
from src.db.session import get_session
from src.core.settings import Settings
from src.services.geocoding import GeocodingService

import logging
logger = logging.getLogger(__name__)

settings = Settings()

# Cost configuration
COST_PER_KM_USD = 0.50  # $0.50 per kilometer for pickup

router = APIRouter(prefix="/riders", tags=["riders"])


# Helper function to get user by auth_id (handles dev/prod modes)
def get_user_from_current_user(session: Session, current_user: CurrentUser) -> User:
    """
    Get user from database using current_user auth_id.
    Handles both development and production modes.
    
    In development mode: auth_id is the database user ID
    In production mode: auth_id is the Supabase auth ID
    """
    from src.core.settings import settings
    
    if settings.development_mode:
        # In dev mode, auth_id IS the user ID
        user = session.exec(
            select(User).where(User.id == current_user.auth_id)
        ).first()
    else:
        # In production, auth_id is Supabase auth ID
        user = session.exec(
            select(User).where(User.auth_id == current_user.auth_id)
        ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


class TripRequest(BaseModel):
    """Request model for trip planning."""
    rider_lat: float = Field(..., ge=-90, le=90, description="Rider latitude coordinate")
    rider_lng: float = Field(..., ge=-180, le=180, description="Rider longitude coordinate")
    destination_lat: float = Field(..., ge=-90, le=90, description="Destination latitude coordinate")
    destination_lng: float = Field(..., ge=-180, le=180, description="Destination longitude coordinate")


class TripResponse(BaseModel):
    """Response model for trip planning."""
    success: bool
    driver_name: Optional[str] = None
    taxi_number: Optional[str] = None
    total_distance_km: Optional[float] = None
    rider_to_driver_distance_km: Optional[float] = None
    rider_to_destination_distance_km: Optional[float] = None
    pickup_cost_usd: Optional[float] = None
    message: str


class CreateTripRequest(BaseModel):
    """Request model for creating a real trip."""
    pickup_latitude: float = Field(..., ge=-90, le=90, description="Pickup latitude coordinate")
    pickup_longitude: float = Field(..., ge=-180, le=180, description="Pickup longitude coordinate")
    destination_latitude: float = Field(..., ge=-90, le=90, description="Destination latitude coordinate")
    destination_longitude: float = Field(..., ge=-180, le=180, description="Destination longitude coordinate")
    pickup_address: Optional[str] = Field(None, max_length=500, description="Pickup address")
    destination_address: Optional[str] = Field(None, max_length=500, description="Destination address")
    rider_notes: Optional[str] = Field(None, max_length=1000, description="Rider notes")
    trip_type: str = Field(default="regular", pattern="^(regular|express|scheduled)$", description="Trip type")
    driver_id: Optional[str] = Field(None, description="Selected driver ID (optional)")


class CreateTripResponse(BaseModel):
    """Response model for trip creation."""
    success: bool
    message: str
    trip: Optional[dict] = None
    driver_assignment: Optional[dict] = None
    active_trip: Optional[dict] = None  # Include existing active trip details


@router.post("/command-course")
async def command_course(
    trip_request: TripRequest,
    session: Session = Depends(get_session)
) -> TripResponse:
    """
    Command a course - find the nearest available driver for a trip and calculate distances.

    Args:
        trip_request: Rider's current location and destination
        session: Database session

    Returns:
        Trip details with nearest driver and distance calculations
    """
    try:
        # Get all active drivers within 10km of rider's location
        # We'll use the existing LocationService logic but with our own filtering
        locations = LocationService.get_all_active_drivers(session)

        if not locations:
            return TripResponse(
                success=False,
                message="No active drivers found in the system."
            )

        # Find drivers within 10km and calculate distances
        nearby_drivers = []
        for loc in locations:
            # Calculate distance from rider to driver
            rider_to_driver_distance = LocationService.haversine(
                trip_request.rider_lat,
                trip_request.rider_lng,
                loc.latitude,
                loc.longitude
            )

            # Only include drivers within 10km
            if rider_to_driver_distance <= 10:
                nearby_drivers.append({
                    'location': loc,
                    'rider_to_driver_distance': rider_to_driver_distance
                })

        if not nearby_drivers:
            return TripResponse(
                success=False,
                message="No drivers found within 10km of your location."
            )

        # Sort by distance and get the nearest driver
        nearby_drivers.sort(key=lambda d: d['rider_to_driver_distance'])
        nearest_driver_data = nearby_drivers[0]
        nearest_location = nearest_driver_data['location']
        rider_to_driver_distance = nearest_driver_data['rider_to_driver_distance']

        # Get driver details from database
        driver_record = session.exec(
            select(Driver).where(Driver.user_id == nearest_location.user_id)
        ).first()

        if not driver_record:
            return TripResponse(
                success=False,
                message="Driver details not found."
            )

        # Get user details
        user = session.exec(
            select(User).where(User.id == driver_record.user_id)
        ).first()

        if not user:
            return TripResponse(
                success=False,
                message="Driver user details not found."
            )

        # Calculate distance from rider's current location to destination
        rider_to_destination_distance = LocationService.haversine(
            trip_request.rider_lat,
            trip_request.rider_lng,
            trip_request.destination_lat,
            trip_request.destination_lng
        )

        # Calculate total distance
        total_distance = rider_to_driver_distance + rider_to_destination_distance

        # Calculate pickup cost
        pickup_cost = rider_to_driver_distance * COST_PER_KM_USD

        logger.info(f"Found nearest driver {user.name} for rider trip. "
                   f"Total distance: {total_distance:.2f}km "
                   f"(Rider→Driver: {rider_to_driver_distance:.2f}km, "
                   f"Rider→Destination: {rider_to_destination_distance:.2f}km) "
                   f"Pickup cost: ${pickup_cost:.2f}")

        return TripResponse(
            success=True,
            driver_name=user.name,
            taxi_number=driver_record.taxi_number,
            total_distance_km=round(total_distance, 2),
            rider_to_driver_distance_km=round(rider_to_driver_distance, 2),
            rider_to_destination_distance_km=round(rider_to_destination_distance, 2),
            pickup_cost_usd=round(pickup_cost, 2),
            message=f"Found nearest driver {user.name} for your trip."
        )

    except Exception as e:
        logger.error(f"Failed to find nearest driver: {str(e)}")
        return TripResponse(
            success=False,
            message="Internal server error occurred while finding driver."
        )


@router.post("/create-trip")
async def create_trip(
    trip_request: CreateTripRequest,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> CreateTripResponse:
    """
    Create a real trip request and assign to nearest driver with Supabase notifications.
    
    This endpoint creates an actual trip in the database, finds the nearest available driver,
    and sends real-time notifications via Supabase channels.

    Args:
        trip_request: Trip details including pickup/destination coordinates
        session: Database session
        current_user: Authenticated rider user

    Returns:
        Trip creation result with driver assignment and notification status
    """
    try:
        # Find the user
        user = get_user_from_current_user(session, current_user)
        
        # Log for debugging
        logger.info(f"User attempting to create trip: ID={user.id}, Name={user.name}, Role={user.role}, Phone={user.phone_number}")
        
        if user.role != "rider":
            logger.error(f"Role check failed: user.role='{user.role}', expected 'rider'. User: {user.name} ({user.phone_number})")
            raise HTTPException(
                status_code=403, 
                detail=f"Only riders can create trips. Your account ({user.name}) is registered as a {user.role}. Please log in with a rider account."
            )
        
        # Check if rider already has an active trip
        existing_trip = TripService.get_rider_active_trip(session, user.id)
        if existing_trip:
            # Get driver details if assigned
            driver_info = None
            if existing_trip.driver_id:
                driver = session.exec(
                    select(User).join(Driver).where(
                        Driver.user_id == existing_trip.driver_id
                    )
                ).first()
                if driver:
                    driver_info = {
                        "name": driver.name,
                        "phone": driver.phone_number
                    }
            
            return CreateTripResponse(
                success=False,
                message="You already have an active trip. Please complete or cancel it before creating a new one.",
                active_trip={
                    "id": existing_trip.id,
                    "status": existing_trip.status,
                    "pickup_address": existing_trip.pickup_address,
                    "destination_address": existing_trip.destination_address,
                    "pickup_latitude": existing_trip.pickup_latitude,
                    "pickup_longitude": existing_trip.pickup_longitude,
                    "destination_latitude": existing_trip.destination_latitude,
                    "destination_longitude": existing_trip.destination_longitude,
                    "driver": driver_info,
                    "created_at": existing_trip.created_at.isoformat() if existing_trip.created_at else None
                }
            )
        
        logger.info(f"Creating trip for rider {user.id} ({user.name}) "
                   f"from ({trip_request.pickup_latitude}, {trip_request.pickup_longitude}) "
                   f"to ({trip_request.destination_latitude}, {trip_request.destination_longitude})"
                   f"{f' with selected driver {trip_request.driver_id}' if trip_request.driver_id else ' (auto-assign)'}")
        
        # Create the trip using TripService
        result = TripService.create_trip_request(
            session=session,
            rider_id=user.id,
            pickup_latitude=trip_request.pickup_latitude,
            pickup_longitude=trip_request.pickup_longitude,
            destination_latitude=trip_request.destination_latitude,
            destination_longitude=trip_request.destination_longitude,
            pickup_address=trip_request.pickup_address,
            destination_address=trip_request.destination_address,
            rider_notes=trip_request.rider_notes,
            trip_type=trip_request.trip_type,
            preferred_driver_id=trip_request.driver_id  # Pass selected driver ID
        )
        
        if result["success"]:
            logger.info(f"Trip created successfully: {result['trip']['id']}")
            
            # Log driver assignment details
            assignment = result["driver_assignment"]
            if assignment["success"]:
                logger.info(f"Trip assigned to driver {assignment['driver_name']} "
                           f"(Channel: {assignment.get('channel', 'N/A')})")
            
            return CreateTripResponse(
                success=True,
                message="Trip created and assigned to nearest driver",
                trip=result["trip"],
                driver_assignment=assignment
            )
        else:
            logger.error(f"Failed to create trip: {result['message']}")
            return CreateTripResponse(
                success=False,
                message=result["message"]
            )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"Failed to create trip: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return CreateTripResponse(
            success=False,
            message=f"Internal server error: {str(e)}"
        )


@router.get("/active-trip")
async def get_rider_active_trip(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> dict:
    """
    Get the active trip for the authenticated rider.
    
    Returns:
        Active trip information or None
    """
    try:
        # Find the user
        user = get_user_from_current_user(session, current_user)
        
        if user.role != "rider":
            raise HTTPException(status_code=403, detail="Only riders can access this endpoint")
        
        trip = TripService.get_rider_active_trip(session, user.id)
        
        if not trip:
            return {
                "has_active_trip": False,
                "message": "No active trip found for rider"
            }
        
        # Get driver info if assigned
        driver_info = None
        if trip.driver_id:
            driver_user = session.exec(
                select(User).where(User.id == trip.driver_id)
            ).first()
            
            driver_profile = session.exec(
                select(Driver).where(Driver.user_id == trip.driver_id)
            ).first()
            
            if driver_user and driver_profile:
                driver_info = {
                    "name": driver_user.name,
                    "taxi_number": driver_profile.taxi_number,
                    "status": driver_profile.driver_status
                }
        
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
                "trip_type": trip.trip_type,
                "pickup_address": pickup_address,
                "destination_address": destination_address,
                "pickup_latitude": trip.pickup_latitude,
                "pickup_longitude": trip.pickup_longitude,
                "destination_latitude": trip.destination_latitude,
                "destination_longitude": trip.destination_longitude,
                "estimated_distance_km": trip.estimated_distance_km,
                "estimated_cost_tnd": trip.estimated_cost_tnd,
                # Cost breakdown fields (per documentation)
                "approach_distance_km": trip.approach_distance_km,
                "approach_fee_tnd": trip.approach_fee_tnd,
                "meter_cost_tnd": trip.meter_cost_tnd,
                "total_cost_tnd": trip.total_cost_tnd,
                "requested_at": trip.requested_at.isoformat() if trip.requested_at else None,
                "assigned_at": trip.assigned_at.isoformat() if trip.assigned_at else None,
                "accepted_at": trip.accepted_at.isoformat() if trip.accepted_at else None,
                "rider_notes": trip.rider_notes,
                "driver": driver_info
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting active trip: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/trips/{trip_id}/confirm-pickup")
async def confirm_pickup(
    trip_id: str,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> dict:
    """
    Confirm that driver has arrived for pickup.
    This allows the driver to start the trip.
    
    Args:
        trip_id: ID of the trip
        session: Database session
        current_user: Authenticated rider user
    
    Returns:
        Confirmation status
    """
    try:
        # Find the user
        user = get_user_from_current_user(session, current_user)
        
        if user.role != "rider":
            raise HTTPException(status_code=403, detail="Only riders can confirm pickup")
        
        # Get the trip
        trip = session.exec(
            select(Trip).where(Trip.id == trip_id)
        ).first()
        
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        # Verify trip belongs to this rider
        if trip.rider_id != user.id:
            raise HTTPException(status_code=403, detail="You can only confirm your own trips")
        
        # Check if trip is in accepted status
        if trip.status != "accepted":
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot confirm pickup for trip with status '{trip.status}'. Trip must be in 'accepted' status."
            )
        
        # Update trip with rider confirmation - driver must manually start trip
        from datetime import datetime
        trip.rider_confirmed_pickup = True
        trip.rider_confirmed_at = datetime.utcnow()
        session.add(trip)
        session.commit()
        session.refresh(trip)
        
        logger.info(f"✅ Rider {user.id} confirmed pickup for trip {trip_id} - Waiting for driver to start trip")
        
        # Notify driver that rider confirmed and they can now start the trip
        if trip.driver_id:
            try:
                from src.services.notification import NotificationService
                await NotificationService.send_trip_notification(
                    session=session,
                    user_id=trip.driver_id,
                    trip_id=trip.id,
                    notification_type="rider_confirmed",
                    title="Rider Confirmed Pickup",
                    message=f"Rider has confirmed pickup. You can now start the trip to {trip.destination_address or 'destination'}.",
                    data={
                        "pickup_address": trip.pickup_address,
                        "destination_address": trip.destination_address
                    }
                )
                logger.info(f"📱 Sent rider confirmation notification to driver {trip.driver_id}")
            except Exception as e:
                logger.error(f"Failed to send confirmation notification to driver: {e}")
        
        return {
            "success": True,
            "message": "Pickup confirmed. Driver can now start the trip.",
            "trip": {
                "id": trip.id,
                "status": trip.status,
                "rider_confirmed_pickup": trip.rider_confirmed_pickup,
                "rider_confirmed_at": trip.rider_confirmed_at.isoformat() if trip.rider_confirmed_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming pickup: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/trips/{trip_id}/cancel")
async def cancel_trip(
    trip_id: str,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency),
    reason: Optional[str] = Body(None, embed=True)
) -> dict:
    """
    Cancel an active trip.
    
    Args:
        trip_id: ID of the trip to cancel
        reason: Optional cancellation reason
        session: Database session
        current_user: Authenticated rider user
    
    Returns:
        Cancellation confirmation with updated trip details
    """
    try:
        # Find the user
        user = get_user_from_current_user(session, current_user)
        
        if user.role != "rider":
            raise HTTPException(status_code=403, detail="Only riders can cancel trips")
        
        # Get the trip
        trip = session.exec(
            select(Trip).where(Trip.id == trip_id)
        ).first()
        
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        # Verify trip belongs to this rider
        if trip.rider_id != user.id:
            raise HTTPException(status_code=403, detail="You can only cancel your own trips")
        
        # Check if trip can be cancelled
        if trip.status in ["completed", "cancelled"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot cancel a {trip.status} trip"
            )
        
        # Store driver_id before clearing it
        assigned_driver_id = trip.driver_id
        
        # Cancel the trip
        trip.status = "cancelled"
        trip.cancelled_at = datetime.utcnow()
        if reason:
            trip.cancellation_reason = reason
        
        # Clear driver assignment immediately to prevent sync issues
        trip.driver_id = None
        
        # Set driver back to online if trip was assigned
        if assigned_driver_id:
            from src.models.user import Driver
            driver = session.exec(select(Driver).where(Driver.user_id == assigned_driver_id)).first()
            if driver and driver.driver_status == "on_trip":
                driver.driver_status = "online"
                session.add(driver)
        
        session.add(trip)
        session.commit()
        session.refresh(trip)
        
        logger.info(f"🚫 Trip {trip_id} cancelled by rider {user.id}. Reason: {reason or 'None'}")
        
        # Send notification to driver via Supabase if driver was assigned
        if assigned_driver_id:
            try:
                from src.services.realtime_location import RealtimeLocationService
                from src.services.notification import NotificationService
                
                # Get driver info using the stored driver_id
                driver = session.exec(select(Driver).where(Driver.user_id == assigned_driver_id)).first()
                if driver:
                    # Save notification to database for driver
                    await NotificationService.send_trip_notification(
                        session=session,
                        user_id=assigned_driver_id,
                        trip_id=trip.id,
                        notification_type="trip_cancelled",
                        title="Trip Cancelled",
                        message=f"Trip cancelled by rider. Reason: {reason or 'No reason provided'}",
                        data={
                            "trip_id": str(trip.id),
                            "cancellation_reason": reason or "No reason provided",
                            "cancelled_by": "rider"
                        }
                    )
                    logger.info(f"💾 Saved cancellation notification for driver {driver.id}")
                    
                    # Also send via GPS streaming channel if driver is streaming
                    if RealtimeLocationService.is_driver_streaming(driver.id):
                        notification = {
                            "type": "trip_cancelled",
                            "trip_id": trip.id,
                            "cancelled_by": "rider",
                            "rider_name": user.name,
                            "reason": reason or "No reason provided",
                            "timestamp": datetime.utcnow().isoformat(),
                            "message": f"Trip cancelled by rider: {reason or 'No reason provided'}"
                        }
                        
                        await NotificationService._send_to_gps_channel(driver.id, notification)
                        logger.info(f"📱 Sent cancellation notification to driver {driver.id} via GPS channel")
            except Exception as e:
                logger.error(f"Failed to send cancellation notification to driver: {e}")
        
        return {
            "success": True,
            "message": "Trip cancelled successfully",
            "trip": {
                "id": trip.id,
                "status": trip.status,
                "cancelled_at": trip.cancelled_at.isoformat() if trip.cancelled_at else None,
                "cancellation_reason": trip.cancellation_reason
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling trip: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/trips/{trip_id}/confirm-completion")
async def confirm_trip_completion(
    trip_id: str,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> dict:
    """
    Confirm trip completion by rider.
    
    Args:
        trip_id: ID of the trip to confirm
        session: Database session
        current_user: Authenticated rider user
    
    Returns:
        Confirmation response
    """
    try:
        # Find the user
        user = get_user_from_current_user(session, current_user)
        
        if user.role != "rider":
            raise HTTPException(status_code=403, detail="Only riders can confirm trip completion")
        
        # Get the trip
        trip = session.exec(
            select(Trip).where(Trip.id == trip_id)
        ).first()
        
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        # Verify trip belongs to this rider
        if trip.rider_id != user.id:
            raise HTTPException(status_code=403, detail="You can only confirm your own trips")
        
        # Check if trip is completed by driver
        if trip.status != "completed":
            raise HTTPException(
                status_code=400, 
                detail="Driver has not marked this trip as completed yet"
            )
        
        # Check if already confirmed
        if trip.rider_confirmed_completion:
            raise HTTPException(
                status_code=400, 
                detail="You have already confirmed this trip completion"
            )
        
        # Confirm completion
        trip.rider_confirmed_completion = True
        trip.rider_confirmed_completion_at = datetime.utcnow()
        
        session.add(trip)
        session.commit()
        session.refresh(trip)
        
        logger.info(f"Trip {trip_id} completion confirmed by rider {user.id}")
        
        return {
            "success": True,
            "message": "Trip completion confirmed. Please rate your driver!",
            "trip_id": trip.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming trip completion: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/trips/{trip_id}/rate")
async def rate_trip(
    trip_id: str,
    rating: int = Query(..., ge=1, le=5),
    comment: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> dict:
    """
    Rate a completed trip.
    
    Args:
        trip_id: ID of the trip to rate
        rating: Rating from 1 to 5 stars
        comment: Optional comment about the driver and trip
        session: Database session
        current_user: Authenticated rider user
    
    Returns:
        Rating confirmation with updated trip details
    """
    try:
        # Find the user
        user = get_user_from_current_user(session, current_user)
        
        if user.role != "rider":
            raise HTTPException(status_code=403, detail="Only riders can rate trips")
        
        # Get the trip
        trip = session.exec(
            select(Trip).where(Trip.id == trip_id)
        ).first()
        
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        # Verify trip belongs to this rider
        if trip.rider_id != user.id:
            raise HTTPException(status_code=403, detail="You can only rate your own trips")
        
        # Check if trip is completed
        if trip.status != "completed":
            raise HTTPException(
                status_code=400, 
                detail="You can only rate completed trips"
            )
        
        # Check if rider confirmed completion
        if not trip.rider_confirmed_completion:
            raise HTTPException(
                status_code=400, 
                detail="Please confirm trip completion before rating"
            )
        
        # Check if already rated
        if trip.rider_rating is not None:
            raise HTTPException(
                status_code=400, 
                detail="You have already rated this trip"
            )
        
        # Add rating and comment
        trip.rider_rating = rating
        trip.rider_rating_comment = comment
        
        session.add(trip)
        session.commit()
        session.refresh(trip)
        
        logger.info(f"✨ Trip {trip_id} rated {rating} stars by rider {user.id}")
        
        return {
            "success": True,
            "message": "Rating submitted successfully. Thank you for your feedback!",
            "trip": {
                "id": trip.id,
                "rider_rating": trip.rider_rating,
                "rider_rating_comment": trip.rider_rating_comment
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rating trip: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/trip-history")
async def get_rider_trip_history(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> dict:
    """
    Get trip history for the authenticated rider.
    
    Args:
        limit: Number of trips to return (max 50)
        offset: Number of trips to skip
        session: Database session
        current_user: Authenticated rider user
    
    Returns:
        List of rider's past trips
    """
    try:
        # Find the user
        user = get_user_from_current_user(session, current_user)
        
        logger.info(f"📜 Fetching trip history for rider: {user.name} (ID: {user.id}, Role: {user.role})")
        
        if user.role != "rider":
            raise HTTPException(status_code=403, detail="Only riders can access this endpoint")
        
        # Get trips for this rider with pagination
        trips = session.exec(
            select(Trip)
            .where(Trip.rider_id == user.id)
            .order_by(Trip.created_at.desc())
            .offset(offset)
            .limit(limit)
        ).all()
        
        logger.info(f"📊 Found {len(trips)} trips for rider {user.name}")
        if trips:
            status_summary = {}
            for trip in trips:
                status_summary[trip.status] = status_summary.get(trip.status, 0) + 1
            logger.info(f"📊 Status breakdown: {status_summary}")
        
        trip_list = []
        for trip in trips:
            # Get driver info if assigned
            driver_info = None
            if trip.driver_id:
                driver_user = session.exec(
                    select(User).where(User.id == trip.driver_id)
                ).first()
                
                driver_profile = session.exec(
                    select(Driver).where(Driver.user_id == trip.driver_id)
                ).first()
                
                if driver_user and driver_profile:
                    driver_info = {
                        "name": driver_user.name,
                        "taxi_number": driver_profile.taxi_number
                    }
            
            trip_list.append({
                "id": trip.id,
                "status": trip.status,
                "trip_type": trip.trip_type,
                "pickup_address": trip.pickup_address,
                "destination_address": trip.destination_address,
                "estimated_distance_km": trip.estimated_distance_km,
                "estimated_cost_tnd": trip.estimated_cost_tnd,
                "requested_at": trip.requested_at.isoformat() if trip.requested_at else None,
                "completed_at": trip.completed_at.isoformat() if trip.completed_at else None,
                "cancelled_at": trip.cancelled_at.isoformat() if trip.cancelled_at else None,
                "driver": driver_info,
                "rider_rating": trip.rider_rating,
                "driver_rating": trip.driver_rating
            })
        
        logger.info(f"✅ Returning {len(trip_list)} trips to frontend")
        
        return {
            "success": True,
            "trips": trip_list,
            "total_returned": len(trip_list),
            "offset": offset,
            "limit": limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trip history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


class TripTimeoutCheckRequest(BaseModel):
    trip_id: str
    still_on_trip: bool


@router.post("/trip-timeout-check")
async def rider_trip_timeout_check(
    request: TripTimeoutCheckRequest,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> dict:
    """
    Handle rider's response to 30-minute trip timeout check.
    
    Args:
        request: Request body with trip_id and still_on_trip
        session: Database session
        current_user: Authenticated rider user
    
    Returns:
        Success status and trip status
    """
    try:
        # Find the user
        user = get_user_from_current_user(session, current_user)
        
        if user.role != "rider":
            raise HTTPException(status_code=403, detail="Only riders can respond to timeout checks")
        
        # Get the trip
        trip = session.exec(
            select(Trip).where(Trip.id == request.trip_id)
        ).first()
        
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        # Verify trip belongs to this rider
        if trip.rider_id != user.id:
            raise HTTPException(status_code=403, detail="You can only respond to checks for your own trips")
        
        # Check if trip is in progress
        if trip.status != "started":
            raise HTTPException(
                status_code=400, 
                detail=f"Trip is not in progress (current status: {trip.status})"
            )
        
        if not request.still_on_trip:
            # Rider responded NO or timeout occurred - cancel the trip
            trip.status = "cancelled"
            trip.cancelled_at = datetime.now(timezone.utc)
            trip.cancellation_reason = "Trip timeout - Rider indicated not on trip or no response"
            
            # Set driver back to online
            if trip.driver:
                trip.driver.driver_status = "online"
            
            session.add(trip)
            session.commit()
            session.refresh(trip)
            
            # Notify both parties
            await NotificationService.send_trip_notification(
                session=session,
                user_id=trip.driver_id,
                trip_id=trip.id,
                notification_type="trip_cancelled",
                title="Trip Cancelled - Timeout",
                message=f"Trip cancelled after 30-minute status check (Rider response: No)",
                data={
                    "trip_id": str(trip.id),
                    "cancellation_reason": trip.cancellation_reason,
                    "cancelled_by": "system_timeout"
                }
            )
            
            logger.info(f"Trip {request.trip_id} cancelled due to timeout check from rider")
            
            return {
                "success": True,
                "message": "Trip cancelled due to timeout",
                "trip_status": "cancelled"
            }
        else:
            # Rider responded YES - continue the trip
            logger.info(f"Trip {request.trip_id} status confirmed by rider, continuing")
            
            return {
                "success": True,
                "message": "Trip status confirmed, continuing",
                "trip_status": "started"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling rider timeout check: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
