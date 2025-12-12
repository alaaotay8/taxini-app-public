"""
Admin trip history service for managing and viewing ride data.

This service provides comprehensive trip management functionality for admins
including filtering, searching, and detailed trip information.
"""

import logging
from typing import Dict, Any, List, Optional
from sqlmodel import Session, select, and_, or_, func
from sqlalchemy.orm import aliased
from datetime import datetime, date

from src.models.trip import Trip
from src.models.user import User
from src.models.enums import TripStatus
from src.schemas.admin import TripSummary, TripStatsFilter

logger = logging.getLogger(__name__)


class AdminTripService:
    """Service for managing trip data from admin perspective."""
    
    @staticmethod
    def get_all_trips(
        session: Session,
        page: int = 1,
        page_size: int = 20,
        driver_id: Optional[str] = None,
        rider_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all trips with comprehensive filtering options.
        
        Args:
            session: Database session
            page: Page number (1-indexed)
            page_size: Number of trips per page
            driver_id: Filter by driver ID
            rider_id: Filter by rider ID
            status: Filter by trip status
            start_date: Filter trips from this date
            end_date: Filter trips until this date
            search: Search in addresses, names, or phone numbers
            
        Returns:
            Dict with trips list and pagination info
        """
        try:
            # Build the base query - select trips and then get user data separately
            base_query = select(Trip)
            
            # Apply filters
            conditions = []
            
            if driver_id:
                conditions.append(Trip.driver_id == driver_id)
            
            if rider_id:
                conditions.append(Trip.rider_id == rider_id)
            
            if status:
                conditions.append(Trip.status == status)
            
            if start_date:
                conditions.append(func.date(Trip.created_at) >= start_date)
            
            if end_date:
                conditions.append(func.date(Trip.created_at) <= end_date)
            
            if search:
                search_conditions = [
                    Trip.pickup_address.ilike(f"%{search}%"),
                    Trip.destination_address.ilike(f"%{search}%")
                ]
                conditions.append(or_(*search_conditions))
            
            if conditions:
                base_query = base_query.where(and_(*conditions))
            
            # Get total count for pagination
            count_query = select(func.count(Trip.id))
            if conditions:
                count_query = count_query.where(and_(*conditions))
            
            total_count = session.exec(count_query).one()
            
            # Apply pagination and ordering
            offset = (page - 1) * page_size
            trips = session.exec(
                base_query.order_by(Trip.created_at.desc())
                .offset(offset)
                .limit(page_size)
            ).all()
            
            # Get user data for each trip
            trip_summaries = []
            for trip in trips:
                # Get rider info
                rider = session.exec(
                    select(User).where(User.id == trip.rider_id)
                ).first()
                
                # Get driver info if exists
                driver = None
                if trip.driver_id:
                    driver = session.exec(
                        select(User).where(User.id == trip.driver_id)
                    ).first()
                
                trip_summary = TripSummary(
                    id=trip.id,
                    rider_id=trip.rider_id,
                    rider_name=rider.name if rider else "Unknown",
                    rider_phone=rider.phone_number if rider else "Unknown",
                    driver_id=trip.driver_id,
                    driver_name=driver.name if driver else None,
                    driver_phone=driver.phone_number if driver else None,
                    pickup_address=trip.pickup_address,
                    destination_address=trip.destination_address,
                    status=trip.status,
                    trip_type=trip.trip_type,
                    estimated_distance_km=trip.estimated_distance_km,
                    estimated_cost_tnd=trip.estimated_cost_tnd,
                    requested_at=trip.requested_at,
                    started_at=trip.started_at,
                    completed_at=trip.completed_at,
                    cancelled_at=trip.cancelled_at,
                    rider_rating=trip.rider_rating,
                    driver_rating=trip.driver_rating,
                    created_at=trip.created_at
                )
                trip_summaries.append(trip_summary)
            
            total_pages = (total_count + page_size - 1) // page_size
            
            return {
                "trips": trip_summaries,
                "total": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
            
        except Exception as e:
            logger.error(f"Failed to get trips: {str(e)}")
            return {
                "trips": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "error": str(e)
            }
    
    @staticmethod
    def get_trip_by_id(session: Session, trip_id: str) -> Optional[TripSummary]:
        """
        Get detailed information for a specific trip.
        
        Args:
            session: Database session
            trip_id: Trip ID to retrieve
            
        Returns:
            TripSummary object if found, None otherwise
        """
        try:
            # Get the trip first
            trip = session.exec(
                select(Trip).where(Trip.id == trip_id)
            ).first()
            
            if not trip:
                return None
            
            # Get rider info
            rider = session.exec(
                select(User).where(User.id == trip.rider_id)
            ).first()
            
            # Get driver info if exists
            driver = None
            if trip.driver_id:
                driver = session.exec(
                    select(User).where(User.id == trip.driver_id)
                ).first()
            
            return TripSummary(
                id=trip.id,
                rider_id=trip.rider_id,
                rider_name=rider.name if rider else "Unknown",
                rider_phone=rider.phone_number if rider else "Unknown",
                driver_id=trip.driver_id,
                driver_name=driver.name if driver else None,
                driver_phone=driver.phone_number if driver else None,
                pickup_address=trip.pickup_address,
                destination_address=trip.destination_address,
                status=trip.status,
                trip_type=trip.trip_type,
                estimated_distance_km=trip.estimated_distance_km,
                estimated_cost_tnd=trip.estimated_cost_tnd,
                requested_at=trip.requested_at,
                started_at=trip.started_at,
                completed_at=trip.completed_at,
                cancelled_at=trip.cancelled_at,
                rider_rating=trip.rider_rating,
                driver_rating=trip.driver_rating,
                created_at=trip.created_at
            )
            
        except Exception as e:
            logger.error(f"Failed to get trip {trip_id}: {str(e)}")
            return None
    
    @staticmethod
    def get_trips_by_driver(
        session: Session,
        driver_id: str,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get trips for a specific driver.
        
        Args:
            session: Database session
            driver_id: Driver ID to filter by
            page: Page number
            page_size: Items per page
            status: Optional status filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dict with trips and pagination info
        """
        return AdminTripService.get_all_trips(
            session=session,
            page=page,
            page_size=page_size,
            driver_id=driver_id,
            status=status,
            start_date=start_date,
            end_date=end_date
        )
    
    @staticmethod
    def get_trip_status_distribution(session: Session) -> Dict[str, int]:
        """
        Get distribution of trips by status.
        
        Args:
            session: Database session
            
        Returns:
            Dict with status counts
        """
        try:
            status_counts = session.exec(
                select(Trip.status, func.count(Trip.id))
                .group_by(Trip.status)
            ).all()
            
            return {status: count for status, count in status_counts}
            
        except Exception as e:
            logger.error(f"Failed to get trip status distribution: {str(e)}")
            return {}
    
    @staticmethod
    def get_top_drivers_by_trips(
        session: Session,
        limit: int = 10,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get top drivers by number of completed trips.
        
        Args:
            session: Database session
            limit: Number of top drivers to return
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of drivers with trip counts
        """
        try:
            query = select(
                Trip.driver_id,
                User.name,
                User.phone_number,
                func.count(Trip.id).label('trip_count'),
                func.avg(Trip.driver_rating).label('avg_rating'),
                func.sum(Trip.estimated_cost_tnd).label('total_revenue')
            ).join(User, Trip.driver_id == User.id).where(
                Trip.status == TripStatus.COMPLETED.value,
                Trip.driver_id.is_not(None)
            )
            
            if start_date:
                query = query.where(func.date(Trip.completed_at) >= start_date)
            
            if end_date:
                query = query.where(func.date(Trip.completed_at) <= end_date)
            
            results = session.exec(
                query.group_by(Trip.driver_id, User.name, User.phone_number)
                .order_by(func.count(Trip.id).desc())
                .limit(limit)
            ).all()
            
            return [
                {
                    "driver_id": result.driver_id,
                    "driver_name": result.name,
                    "driver_phone": result.phone_number,
                    "completed_trips": result.trip_count,
                    "average_rating": round(float(result.avg_rating), 2) if result.avg_rating else None,
                    "total_revenue": float(result.total_revenue) if result.total_revenue else 0.0
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Failed to get top drivers: {str(e)}")
            return []
