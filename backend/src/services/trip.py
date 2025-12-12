"""
Trip management service with driver assignment and notification handling.

Integrated with Supabase Realtime notifications for seamless driver communication.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlmodel import Session, select
from sqlalchemy import and_, or_

from src.models.user import User, Driver, Rider
from src.models.trip import Trip
from src.models.location import Location
from src.models.enums import DriverStatus, TripStatus
from src.services.location import LocationService
from src.services.notification import NotificationService

logger = logging.getLogger(__name__)


class TripService:
    """Service for managing trip operations and driver-rider matching with Supabase integration."""

    @staticmethod
    def create_trip_request(
        session: Session,
        rider_id: str,
        pickup_latitude: float,
        pickup_longitude: float,
        destination_latitude: float,
        destination_longitude: float,
        pickup_address: Optional[str] = None,
        destination_address: Optional[str] = None,
        rider_notes: Optional[str] = None,
        trip_type: str = "regular",
        preferred_driver_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new trip request and assign to preferred driver or find nearest available driver.
        
        Args:
            session: Database session
            rider_id: ID of the rider requesting the trip
            pickup_latitude: Pickup location latitude
            pickup_longitude: Pickup location longitude
            destination_latitude: Destination latitude
            destination_longitude: Destination longitude
            pickup_address: Optional pickup address
            destination_address: Optional destination address
            rider_notes: Optional notes from rider
            trip_type: Type of trip (regular, express, scheduled)
            preferred_driver_id: Optional driver ID selected by user (will verify availability)
            
        Returns:
            Dict with trip creation result and assigned driver
        """
        try:
            # Verify rider exists
            rider_user = session.exec(select(User).where(User.id == rider_id)).first()
            if not rider_user:
                return {
                    "success": False,
                    "message": "Rider not found"
                }
            
            # Calculate estimated distance and cost (Tunisian pricing)
            trip_distance = LocationService.haversine(
                pickup_latitude, pickup_longitude,
                destination_latitude, destination_longitude
            )
            
            # Tunisian taxi pricing: Meter-based estimate (will be replaced by actual meter reading)
            # Base fare + distance estimate
            estimated_meter_cost = 5.0 + (trip_distance * 2.5)
            
            # Note: Approach fee will be calculated when driver is assigned
            # For now, estimated_cost = estimated_meter_cost (approach fee added later)
            estimated_cost = estimated_meter_cost
            
            # Create trip record
            trip = Trip(
                rider_id=rider_id,
                pickup_latitude=pickup_latitude,
                pickup_longitude=pickup_longitude,
                pickup_address=pickup_address or "Adresse de ramassage",
                destination_latitude=destination_latitude,
                destination_longitude=destination_longitude,
                destination_address=destination_address or "Destination",
                estimated_distance_km=round(trip_distance, 2),
                estimated_cost_tnd=round(estimated_cost, 2),
                status=TripStatus.REQUESTED.value,
                trip_type=trip_type,
                requested_at=datetime.utcnow(),
                rider_notes=rider_notes
            )
            
            session.add(trip)
            session.commit()
            session.refresh(trip)
            
            logger.info(f"Trip {trip.id} created for rider {rider_id} "
                       f"({trip_distance:.2f}km, {estimated_cost:.2f} TND)")
            
            # Trip stays in "requested" status - no auto-assignment
            # Drivers will see this request and can choose to accept/reject it
            logger.info(f"Trip {trip.id} is now waiting for driver acceptance")
            
            return {
                "success": True,
                "message": "Trip request created successfully. Waiting for driver acceptance...",
                "trip": {
                    "id": trip.id,
                    "status": trip.status,  # Will be "requested"
                    "pickup_address": trip.pickup_address,
                    "destination_address": trip.destination_address,
                    "estimated_distance_km": trip.estimated_distance_km,
                    "estimated_cost_tnd": trip.estimated_cost_tnd,
                    "trip_type": trip.trip_type,
                    "driver_id": None  # No driver assigned yet
                },
                "driver_assignment": {
                    "success": False,
                    "message": "Waiting for driver to accept request",
                    "driver_assigned": False
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create trip request: {str(e)}")
            session.rollback()
            return {
                "success": False,
                "message": f"Failed to create trip request: {str(e)}"
            }

    @staticmethod
    def assign_specific_driver(
        session: Session,
        trip_id: str,
        driver_id: str,
        pickup_latitude: float,
        pickup_longitude: float
    ) -> Dict[str, Any]:
        """
        Assign a specific driver to a trip (user-selected driver).
        Verifies the driver is available before assignment.
        
        Args:
            session: Database session
            trip_id: ID of the trip to assign
            driver_id: ID of the specific driver to assign
            pickup_latitude: Pickup location latitude
            pickup_longitude: Pickup location longitude
            
        Returns:
            Dict with assignment result
        """
        try:
            # Get the driver
            driver = session.exec(select(Driver).where(Driver.user_id == driver_id)).first()
            
            if not driver:
                logger.warning(f"Selected driver {driver_id} not found, falling back to auto-assign")
                return TripService.assign_nearest_driver(
                    session, trip_id, pickup_latitude, pickup_longitude
                )
            
            # Verify driver is online and verified
            if driver.driver_status != DriverStatus.ONLINE.value:
                logger.warning(f"Selected driver {driver_id} is not online ({driver.driver_status}), falling back to auto-assign")
                return TripService.assign_nearest_driver(
                    session, trip_id, pickup_latitude, pickup_longitude
                )
            
            if driver.account_status != "verified":
                logger.warning(f"Selected driver {driver_id} is not verified ({driver.account_status}), falling back to auto-assign")
                return TripService.assign_nearest_driver(
                    session, trip_id, pickup_latitude, pickup_longitude
                )
            
            # Get driver location
            driver_location = session.exec(
                select(Location).where(
                    Location.user_id == driver_id,
                    Location.role == "driver"
                )
            ).first()
            
            if not driver_location:
                logger.warning(f"Selected driver {driver_id} has no location data, falling back to auto-assign")
                return TripService.assign_nearest_driver(
                    session, trip_id, pickup_latitude, pickup_longitude
                )
            
            # Calculate distance to pickup
            distance = LocationService.haversine(
                pickup_latitude, pickup_longitude,
                driver_location.latitude, driver_location.longitude
            )
            
            # Update trip with assigned driver
            trip = session.exec(select(Trip).where(Trip.id == trip_id)).first()
            if not trip:
                return {
                    "success": False,
                    "message": "Trip not found"
                }
            
            trip.driver_id = driver.user_id
            trip.status = TripStatus.ASSIGNED.value
            trip.assigned_at = datetime.utcnow()
            session.add(trip)
            session.commit()
            
            # Get driver user info
            driver_user = session.exec(
                select(User).where(User.id == driver.user_id)
            ).first()
            
            logger.info(f"✅ Trip {trip_id} assigned to SELECTED driver {driver.id} "
                       f"({driver_user.name if driver_user else 'Unknown'}) "
                       f"at {distance:.2f}km distance")
            
            # Send notification to assigned driver via Supabase
            try:
                if asyncio.get_event_loop().is_running():
                    asyncio.create_task(
                        NotificationService.notify_driver_trip_request(
                            session=session,
                            driver_id=driver.id,
                            trip_id=trip_id,
                            trip_details={
                                "pickup_address": trip.pickup_address,
                                "destination_address": trip.destination_address,
                                "estimated_distance_km": trip.estimated_distance_km,
                                "estimated_cost_tnd": trip.estimated_cost_tnd,
                                "rider_notes": trip.rider_notes,
                                "requested_at": trip.requested_at.isoformat() if trip.requested_at else None,
                                "trip_type": trip.trip_type
                            }
                        )
                    )
                else:
                    asyncio.run(
                        NotificationService.notify_driver_trip_request(
                            session=session,
                            driver_id=driver.id,
                            trip_id=trip_id,
                            trip_details={
                                "pickup_address": trip.pickup_address,
                                "destination_address": trip.destination_address,
                                "estimated_distance_km": trip.estimated_distance_km,
                                "estimated_cost_tnd": trip.estimated_cost_tnd,
                                "rider_notes": trip.rider_notes,
                                "requested_at": trip.requested_at.isoformat() if trip.requested_at else None,
                                "trip_type": trip.trip_type
                            }
                        )
                    )
                
                logger.info(f"🔔 Supabase notification sent to selected driver {driver.id} for trip {trip_id}")
                
            except Exception as e:
                logger.error(f"Failed to send Supabase notification to driver: {e}")
            
            return {
                "success": True,
                "message": "Selected driver assigned successfully",
                "driver_id": driver.id,
                "driver_name": driver_user.name if driver_user else "Unknown",
                "distance_km": round(distance, 2),
                "taxi_number": driver.taxi_number,
                "channel": f"driver_{driver.id}"
            }
            
        except Exception as e:
            logger.error(f"Failed to assign selected driver {driver_id} to trip {trip_id}: {str(e)}")
            logger.info("Falling back to auto-assign nearest driver")
            return TripService.assign_nearest_driver(
                session, trip_id, pickup_latitude, pickup_longitude
            )

    @staticmethod
    def assign_nearest_driver(
        session: Session,
        trip_id: str,
        pickup_latitude: float,
        pickup_longitude: float,
        excluded_driver_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Find and assign the nearest available driver to a trip.
        
        Args:
            session: Database session
            trip_id: ID of the trip to assign
            pickup_latitude: Pickup location latitude
            pickup_longitude: Pickup location longitude
            excluded_driver_ids: List of driver IDs to exclude (e.g., drivers who rejected)
            
        Returns:
            Dict with assignment result
        """
        try:
            excluded_driver_ids = excluded_driver_ids or []
            
            # Get all online drivers with locations using existing LocationService
            locations = LocationService.get_all_active_drivers(session)
            
            if not locations:
                return {
                    "success": False,
                    "message": "No active drivers available"
                }
            
            # Find available drivers within 10km radius
            available_drivers = []
            for loc in locations:
                # Calculate distance to pickup
                distance = LocationService.haversine(
                    pickup_latitude, pickup_longitude,
                    loc.latitude, loc.longitude
                )
                
                if distance <= 10.0:  # 10km radius
                    # Get driver details
                    driver = session.exec(
                        select(Driver).where(Driver.user_id == loc.user_id)
                    ).first()
                    
                    if (driver and 
                        driver.driver_status == DriverStatus.ONLINE.value and
                        driver.id not in excluded_driver_ids):
                        
                        available_drivers.append({
                            "driver": driver,
                            "location": loc,
                            "distance": distance
                        })
            
            if not available_drivers:
                return {
                    "success": False,
                    "message": "No available drivers found within 10km"
                }
            
            # Sort by distance and assign to nearest driver
            available_drivers.sort(key=lambda d: d["distance"])
            nearest = available_drivers[0]
            
            # Update trip with assigned driver
            trip = session.exec(select(Trip).where(Trip.id == trip_id)).first()
            if not trip:
                return {
                    "success": False,
                    "message": "Trip not found"
                }
            
            trip.driver_id = nearest["driver"].user_id
            trip.status = TripStatus.ASSIGNED.value
            trip.assigned_at = datetime.utcnow()
            session.add(trip)
            session.commit()
            
            # Get driver user info
            driver_user = session.exec(
                select(User).where(User.id == nearest["driver"].user_id)
            ).first()
            
            logger.info(f"Trip {trip_id} assigned to driver {nearest['driver'].id} "
                       f"({driver_user.name if driver_user else 'Unknown'}) "
                       f"at {nearest['distance']:.2f}km distance")
            
            # Send notification to assigned driver via Supabase
            try:
                # Send notification asynchronously
                if asyncio.get_event_loop().is_running():
                    asyncio.create_task(
                        NotificationService.notify_driver_trip_request(
                            session=session,
                            driver_id=nearest["driver"].id,
                            trip_id=trip_id,
                            trip_details={
                                "pickup_address": trip.pickup_address,
                                "destination_address": trip.destination_address,
                                "estimated_distance_km": trip.estimated_distance_km,
                                "estimated_cost_tnd": trip.estimated_cost_tnd,
                                "rider_notes": trip.rider_notes,
                                "requested_at": trip.requested_at.isoformat() if trip.requested_at else None,
                                "trip_type": trip.trip_type
                            }
                        )
                    )
                else:
                    # Run in new event loop if no loop is running
                    asyncio.run(
                        NotificationService.notify_driver_trip_request(
                            session=session,
                            driver_id=nearest["driver"].id,
                            trip_id=trip_id,
                            trip_details={
                                "pickup_address": trip.pickup_address,
                                "destination_address": trip.destination_address,
                                "estimated_distance_km": trip.estimated_distance_km,
                                "estimated_cost_tnd": trip.estimated_cost_tnd,
                                "rider_notes": trip.rider_notes,
                                "requested_at": trip.requested_at.isoformat() if trip.requested_at else None,
                                "trip_type": trip.trip_type
                            }
                        )
                    )
                
                logger.info(f"🔔 Supabase notification sent to driver {nearest['driver'].id} for trip {trip_id}")
                
            except Exception as e:
                logger.error(f"Failed to send Supabase notification to driver: {e}")
                # Don't fail the assignment if notification fails
            
            return {
                "success": True,
                "message": "Driver assigned successfully",
                "driver_id": nearest["driver"].id,
                "driver_name": driver_user.name if driver_user else "Unknown",
                "distance_km": round(nearest["distance"], 2),
                "taxi_number": nearest["driver"].taxi_number,
                "channel": f"driver_{nearest['driver'].id}"
            }
            
        except Exception as e:
            logger.error(f"Failed to assign driver to trip {trip_id}: {str(e)}")
            session.rollback()
            return {
                "success": False,
                "message": f"Failed to assign driver: {str(e)}"
            }

    @staticmethod
    async def handle_driver_acceptance(
        session: Session,
        driver_id: str,
        trip_id: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle driver accepting a trip request.
        
        Args:
            session: Database session
            driver_id: ID of the driver accepting
            trip_id: ID of the trip being accepted
            notes: Optional driver notes
            
        Returns:
            Dict with acceptance result
        """
        try:
            # Get trip and verify it's assigned to this driver
            trip = session.exec(select(Trip).where(Trip.id == trip_id)).first()
            if not trip:
                return {
                    "success": False,
                    "message": "Trip not found"
                }
            
            # Get driver
            driver = session.exec(select(Driver).where(Driver.id == driver_id)).first()
            if not driver:
                return {
                    "success": False,
                    "message": "Driver not found"
                }
            
            # Verify trip is assigned to this driver
            if trip.driver_id != driver.user_id:
                return {
                    "success": False,
                    "message": "Trip is not assigned to this driver"
                }
            
            if trip.status != TripStatus.ASSIGNED.value:
                return {
                    "success": False,
                    "message": f"Trip cannot be accepted. Current status: {trip.status}"
                }
            
            # Calculate approach fee (FA = Distance_Approche × Taux_Approche)
            # Get driver's current location from locations table
            driver_location = session.exec(
                select(Location).where(Location.user_id == driver.user_id)
            ).first()
            
            if driver_location and driver_location.latitude and driver_location.longitude:
                # Calculate approach distance
                approach_distance = LocationService.haversine(
                    driver_location.latitude, driver_location.longitude,
                    trip.pickup_latitude, trip.pickup_longitude
                )
                
                # Approach rate: 0.500 TND/km (configurable)
                approach_rate = 0.500
                approach_fee = approach_distance * approach_rate
                
                # Store approach details
                trip.approach_distance_km = round(approach_distance, 2)
                trip.approach_fee_tnd = round(approach_fee, 3)
                
                logger.info(f"Approach fee calculated: {approach_distance:.2f}km × {approach_rate} TND/km = {approach_fee:.3f} TND")
            
            # Update trip status
            trip.status = TripStatus.ACCEPTED.value
            trip.accepted_at = datetime.utcnow()
            if notes:
                trip.driver_notes = notes
            
            # Update driver status
            driver.driver_status = DriverStatus.ON_TRIP.value
            
            session.add(trip)
            session.add(driver)
            session.commit()
            
            # Get driver and rider info for logging
            driver_user = session.exec(select(User).where(User.id == driver.user_id)).first()
            rider_user = session.exec(select(User).where(User.id == trip.rider_id)).first()
            
            logger.info(f"Trip {trip_id} accepted by driver {driver_id} "
                       f"({driver_user.name if driver_user else 'Unknown'}) "
                       f"for rider {trip.rider_id} ({rider_user.name if rider_user else 'Unknown'})")
            
            # Handle Supabase notifications
            try:
                # Cancel timeout for accepting driver
                await NotificationService.cancel_pending_notification(driver_id, trip_id)
                
                # Notify rider of acceptance
                driver_info = {
                    "name": driver_user.name if driver_user else "Unknown",
                    "taxi_number": driver.taxi_number
                }
                await NotificationService.notify_rider_driver_response(
                    session=session,
                    rider_id=trip.rider_id,
                    trip_id=trip_id,
                    response="accepted",
                    driver_info=driver_info
                )
                
                logger.info(f"🔔 Supabase notifications handled for trip acceptance {trip_id}")
                
            except Exception as e:
                logger.error(f"Failed to handle Supabase notifications for trip acceptance: {e}")
            
            return {
                "success": True,
                "message": "Trip accepted successfully",
                "trip_id": trip_id,
                "driver_name": driver_user.name if driver_user else "Unknown",
                "rider_name": rider_user.name if rider_user else "Unknown",
                "pickup_address": trip.pickup_address,
                "destination_address": trip.destination_address,
                "estimated_cost_tnd": trip.estimated_cost_tnd,
                "approach_distance_km": trip.approach_distance_km,
                "approach_fee_tnd": trip.approach_fee_tnd,
                "total_estimated_tnd": (trip.approach_fee_tnd or 0) + (trip.estimated_cost_tnd or 0),
                "new_driver_status": driver.driver_status
            }
            
        except Exception as e:
            logger.error(f"Failed to accept trip {trip_id} by driver {driver_id}: {str(e)}")
            session.rollback()
            return {
                "success": False,
                "message": f"Failed to accept trip: {str(e)}"
            }

    @staticmethod
    async def handle_driver_rejection(
        session: Session,
        driver_id: str,
        trip_id: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle driver rejecting a trip request and reassign to next available driver.
        
        Args:
            session: Database session
            driver_id: ID of the driver rejecting
            trip_id: ID of the trip being rejected
            notes: Optional rejection reason
            
        Returns:
            Dict with rejection and reassignment result
        """
        try:
            # Get trip and verify it's assigned to this driver
            trip = session.exec(select(Trip).where(Trip.id == trip_id)).first()
            if not trip:
                return {
                    "success": False,
                    "message": "Trip not found"
                }
            
            # Get driver
            driver = session.exec(select(Driver).where(Driver.id == driver_id)).first()
            if not driver:
                return {
                    "success": False,
                    "message": "Driver not found"
                }
            
            # Verify trip is assigned to this driver
            if trip.driver_id != driver.user_id:
                return {
                    "success": False,
                    "message": "Trip is not assigned to this driver"
                }
            
            # Log rejection
            driver_user = session.exec(select(User).where(User.id == driver.user_id)).first()
            logger.info(f"Trip {trip_id} rejected by driver {driver_id} "
                       f"({driver_user.name if driver_user else 'Unknown'}). "
                       f"Reason: {notes or 'No reason provided'}")
            
            # Keep track of drivers who rejected this trip
            rejected_drivers = [driver_id]
            
            # Set driver back to online (keep them available)
            driver.driver_status = DriverStatus.ONLINE.value
            session.add(driver)
            
            # Cancel pending Supabase notification
            try:
                await NotificationService.cancel_pending_notification(driver_id, trip_id)
                logger.info(f"🔔 Cancelled Supabase notification for rejected trip {trip_id}")
                
            except Exception as e:
                logger.error(f"Failed to cancel Supabase notification: {e}")
            
            # Try to reassign to next available driver
            reassignment_result = TripService.assign_nearest_driver(
                session, trip_id, trip.pickup_latitude, trip.pickup_longitude,
                excluded_driver_ids=rejected_drivers
            )
            
            if reassignment_result["success"]:
                logger.info(f"Trip {trip_id} reassigned to new driver after rejection")
                
                # Notify rider of reassignment
                try:
                    driver_info = {"name": driver_user.name if driver_user else "Unknown"}
                    await NotificationService.notify_rider_driver_response(
                        session=session,
                        rider_id=trip.rider_id,
                        trip_id=trip_id,
                        response="rejected",
                        driver_info=driver_info
                    )
                    
                    logger.info(f"🔔 Notified rider of reassignment for trip {trip_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to notify rider of reassignment: {e}")
                
                return {
                    "success": True,
                    "message": "Trip rejected and reassigned to next available driver",
                    "trip_id": trip_id,
                    "rejecting_driver": driver_user.name if driver_user else "Unknown",
                    "new_assignment": reassignment_result
                }
            else:
                # No other drivers available, cancel the trip
                trip.status = TripStatus.CANCELLED.value
                trip.cancelled_at = datetime.utcnow()
                trip.cancellation_reason = "No available drivers after rejection"
                trip.driver_id = None
                session.add(trip)
                session.commit()
                
                logger.warning(f"Trip {trip_id} cancelled - no more available drivers after rejection")
                
                # Notify rider of cancellation
                try:
                    driver_info = {"name": driver_user.name if driver_user else "Unknown"}
                    await NotificationService.notify_rider_driver_response(
                        session=session,
                        rider_id=trip.rider_id,
                        trip_id=trip_id,
                        response="cancelled",
                        driver_info=driver_info
                    )
                    
                    logger.info(f"🔔 Notified rider of trip cancellation {trip_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to notify rider of cancellation: {e}")
                
                return {
                    "success": True,
                    "message": "Trip rejected and cancelled - no more available drivers",
                    "trip_id": trip_id,
                    "rejecting_driver": driver_user.name if driver_user else "Unknown",
                    "trip_cancelled": True
                }
            
        except Exception as e:
            logger.error(f"Failed to reject trip {trip_id} by driver {driver_id}: {str(e)}")
            session.rollback()
            return {
                "success": False,
                "message": f"Failed to reject trip: {str(e)}"
            }

    @staticmethod
    def get_driver_active_trip(session: Session, driver_id: str) -> Optional[Trip]:
        """
        Get the active trip for a driver.
        
        Args:
            session: Database session
            driver_id: ID of the driver
            
        Returns:
            Active trip or None (explicitly excludes cancelled and completed trips)
        """
        driver = session.exec(select(Driver).where(Driver.id == driver_id)).first()
        if not driver:
            return None
        
        # Get active trip (assigned, accepted, or started)
        # Using .in_() automatically excludes cancelled and completed
        trip = session.exec(
            select(Trip).where(
                and_(
                    Trip.driver_id == driver.user_id,
                    Trip.status.in_([
                        TripStatus.ASSIGNED.value, 
                        TripStatus.ACCEPTED.value, 
                        TripStatus.STARTED.value
                    ])
                )
            ).order_by(Trip.requested_at.desc())
        ).first()
        
        return trip

    @staticmethod
    def get_rider_active_trip(session: Session, rider_id: str) -> Optional[Trip]:
        """
        Get the active trip for a rider.
        Includes completed trips that haven't been confirmed yet so rider can confirm and rate.
        
        Args:
            session: Database session
            rider_id: ID of the rider
            
        Returns:
            Active trip or None
        """
        trip = session.exec(
            select(Trip).where(
                and_(
                    Trip.rider_id == rider_id,
                    or_(
                        Trip.status == TripStatus.REQUESTED.value,
                        Trip.status == TripStatus.ASSIGNED.value,
                        Trip.status == TripStatus.ACCEPTED.value,
                        Trip.status == TripStatus.STARTED.value,
                        # Include completed trips that haven't been confirmed yet
                        and_(
                            Trip.status == TripStatus.COMPLETED.value,
                            Trip.rider_confirmed_completion == False
                        )
                    )
                )
            )
        ).first()
        
        return trip
