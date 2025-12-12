"""
Admin statistics service for generating platform insights and metrics.

This service provides comprehensive statistics about the platform including
rides, revenue, driver activity, and user metrics.
"""

import logging
from typing import Dict, Any, Optional, List
from sqlmodel import Session, select, func, and_, or_
from datetime import datetime, date, timedelta

from src.models.user import User, Driver, Rider
from src.models.trip import Trip
from src.models.enums import UserRole, DriverStatus, TripStatus
from src.schemas.admin import GlobalStats, TripStatsFilter

logger = logging.getLogger(__name__)


class AdminStatsService:
    """Service for generating admin statistics and metrics."""
    
    @staticmethod
    def get_global_statistics(
        session: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> GlobalStats:
        """
        Get comprehensive platform statistics.
        
        Args:
            session: Database session
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            GlobalStats object with all platform metrics
        """
        try:
            # Basic user counts
            total_users = session.exec(select(func.count(User.id))).one()
            total_drivers = session.exec(
                select(func.count(Driver.id))
            ).one()
            total_riders = session.exec(
                select(func.count(Rider.id))
            ).one()
            
            # Active drivers (verified and not banned)
            active_drivers = session.exec(
                select(func.count(Driver.id)).where(
                    Driver.account_status == "verified"
                )
            ).one()
            
            # Driver status distribution
            online_drivers = session.exec(
                select(func.count(Driver.id)).where(
                    and_(
                        Driver.account_status == "verified",
                        Driver.driver_status == DriverStatus.ONLINE.value
                    )
                )
            ).one()
            
            busy_drivers = session.exec(
                select(func.count(Driver.id)).where(
                    and_(
                        Driver.account_status == "verified",
                        Driver.driver_status == DriverStatus.ON_TRIP.value
                    )
                )
            ).one()
            
            offline_drivers = active_drivers - online_drivers - busy_drivers
            
            # Trip statistics
            total_trips = session.exec(select(func.count(Trip.id))).one()
            
            # Today's trips
            today = datetime.now().date()
            trips_today = session.exec(
                select(func.count(Trip.id)).where(
                    func.date(Trip.created_at) == today
                )
            ).one()
            
            # This week's trips
            week_start = today - timedelta(days=today.weekday())
            trips_this_week = session.exec(
                select(func.count(Trip.id)).where(
                    func.date(Trip.created_at) >= week_start
                )
            ).one()
            
            # This month's trips
            month_start = today.replace(day=1)
            trips_this_month = session.exec(
                select(func.count(Trip.id)).where(
                    func.date(Trip.created_at) >= month_start
                )
            ).one()
            
            # Revenue calculations (only completed trips)
            total_revenue_result = session.exec(
                select(func.coalesce(func.sum(Trip.estimated_cost_tnd), 0)).where(
                    Trip.status == TripStatus.COMPLETED.value
                )
            ).one()
            total_revenue = float(total_revenue_result) if total_revenue_result else 0.0
            
            revenue_today_result = session.exec(
                select(func.coalesce(func.sum(Trip.estimated_cost_tnd), 0)).where(
                    and_(
                        Trip.status == TripStatus.COMPLETED.value,
                        func.date(Trip.completed_at) == today
                    )
                )
            ).one()
            revenue_today = float(revenue_today_result) if revenue_today_result else 0.0
            
            revenue_this_week_result = session.exec(
                select(func.coalesce(func.sum(Trip.estimated_cost_tnd), 0)).where(
                    and_(
                        Trip.status == TripStatus.COMPLETED.value,
                        func.date(Trip.completed_at) >= week_start
                    )
                )
            ).one()
            revenue_this_week = float(revenue_this_week_result) if revenue_this_week_result else 0.0
            
            revenue_this_month_result = session.exec(
                select(func.coalesce(func.sum(Trip.estimated_cost_tnd), 0)).where(
                    and_(
                        Trip.status == TripStatus.COMPLETED.value,
                        func.date(Trip.completed_at) >= month_start
                    )
                )
            ).one()
            revenue_this_month = float(revenue_this_month_result) if revenue_this_month_result else 0.0
            
            # Trip status distribution
            completed_trips = session.exec(
                select(func.count(Trip.id)).where(
                    Trip.status == TripStatus.COMPLETED.value
                )
            ).one()
            
            cancelled_trips = session.exec(
                select(func.count(Trip.id)).where(
                    Trip.status == TripStatus.CANCELLED.value
                )
            ).one()
            
            # Completion rate calculation
            total_ended_trips = completed_trips + cancelled_trips
            completion_rate = (completed_trips / total_ended_trips * 100) if total_ended_trips > 0 else 0.0
            
            # Average metrics for completed trips
            avg_metrics = session.exec(
                select(
                    func.avg(
                        func.extract('epoch', Trip.completed_at - Trip.started_at) / 60
                    ).label('avg_duration'),
                    func.avg(Trip.estimated_distance_km).label('avg_distance'),
                    func.avg(Trip.estimated_cost_tnd).label('avg_cost')
                ).where(
                    and_(
                        Trip.status == TripStatus.COMPLETED.value,
                        Trip.started_at.is_not(None),
                        Trip.completed_at.is_not(None)
                    )
                )
            ).one()
            
            avg_duration = float(avg_metrics.avg_duration) if avg_metrics.avg_duration else None
            avg_distance = float(avg_metrics.avg_distance) if avg_metrics.avg_distance else None
            avg_cost = float(avg_metrics.avg_cost) if avg_metrics.avg_cost else None
            
            return GlobalStats(
                # Basic counts
                total_users=total_users,
                total_drivers=total_drivers,
                total_riders=total_riders,
                active_drivers=active_drivers,
                
                # Trip statistics
                total_trips=total_trips,
                trips_today=trips_today,
                trips_this_week=trips_this_week,
                trips_this_month=trips_this_month,
                
                # Revenue statistics
                total_revenue=total_revenue,
                revenue_today=revenue_today,
                revenue_this_week=revenue_this_week,
                revenue_this_month=revenue_this_month,
                
                # Average metrics
                average_trip_duration_minutes=avg_duration,
                average_trip_distance_km=avg_distance,
                average_trip_cost=avg_cost,
                
                # Status distribution
                completed_trips=completed_trips,
                cancelled_trips=cancelled_trips,
                completion_rate=round(completion_rate, 2),
                
                # Driver metrics
                online_drivers=online_drivers,
                busy_drivers=busy_drivers,
                offline_drivers=offline_drivers
            )
            
        except Exception as e:
            logger.error(f"Failed to get global statistics: {str(e)}")
            # Return zero stats in case of error
            return GlobalStats(
                total_users=0, total_drivers=0, total_riders=0, active_drivers=0,
                total_trips=0, trips_today=0, trips_this_week=0, trips_this_month=0,
                total_revenue=0.0, revenue_today=0.0, revenue_this_week=0.0, revenue_this_month=0.0,
                average_trip_duration_minutes=None, average_trip_distance_km=None, average_trip_cost=None,
                completed_trips=0, cancelled_trips=0, completion_rate=0.0,
                online_drivers=0, busy_drivers=0, offline_drivers=0
            )
    
    @staticmethod
    def get_trip_statistics_by_date_range(
        session: Session,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Get trip statistics for a specific date range.
        
        Args:
            session: Database session
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            Dictionary with trip statistics for the date range
        """
        try:
            # Trip counts by status in date range
            trips_in_range = session.exec(
                select(
                    Trip.status,
                    func.count(Trip.id).label('count'),
                    func.coalesce(func.sum(Trip.estimated_cost_tnd), 0).label('revenue')
                ).where(
                    and_(
                        func.date(Trip.created_at) >= start_date,
                        func.date(Trip.created_at) <= end_date
                    )
                ).group_by(Trip.status)
            ).all()
            
            # Format results
            stats = {
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "trips_by_status": {},
                "total_trips": 0,
                "total_revenue": 0.0
            }
            
            for trip_stat in trips_in_range:
                stats["trips_by_status"][trip_stat.status] = {
                    "count": trip_stat.count,
                    "revenue": float(trip_stat.revenue)
                }
                stats["total_trips"] += trip_stat.count
                if trip_stat.status == TripStatus.COMPLETED.value:
                    stats["total_revenue"] += float(trip_stat.revenue)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get trip statistics by date range: {str(e)}")
            return {
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "trips_by_status": {},
                "total_trips": 0,
                "total_revenue": 0.0,
                "error": str(e)
            }
