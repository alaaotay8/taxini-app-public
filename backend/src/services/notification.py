"""
Notification service for real-time driver notifications using Supabase Realtime.

UNIFIED with GPS streaming - uses the same Supabase channels for both:
1. GPS location updates (from RealtimeLocationService)
2. Trip notifications (from this service)

Handles push notifications, WebSocket messaging via Supabase channels, 
and timer-based auto-rejection for trip requests.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlmodel import Session, select
import json

from src.core.settings import settings
from src.models.user import Driver, User
from src.models.trip import Trip
from src.models.enums import TripStatus

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for managing real-time notifications to drivers via Supabase Realtime.
    
    IMPORTANT: This service integrates with RealtimeLocationService to use the SAME
    Supabase channels for both GPS streaming and trip notifications.
    """
    
    # Pending notifications with timers (GPS channels are managed by RealtimeLocationService)
    pending_notifications: Dict[str, Dict[str, Any]] = {}
    
    # Notification timeout in seconds (20 seconds as requested)
    NOTIFICATION_TIMEOUT = 20
    
    @classmethod
    async def connect_driver(cls, driver_id: str) -> Dict[str, Any]:
        """
        Connect driver to notification system via streaming channel.
        
        This method leverages the existing GPS streaming channel for notifications.
        
        Args:
            driver_id: ID of the driver to connect
            
        Returns:
            Connection result with channel information
        """
        try:
            # Import here to avoid circular imports
            from src.services.realtime_location import RealtimeLocationService
            
            # Check if driver has active GPS streaming
            if RealtimeLocationService.is_driver_streaming(driver_id):
                logger.info(f"🔔 Driver {driver_id} connected to notifications via GPS streaming channel")
                return {
                    "success": True,
                    "message": "Connected to trip notifications via GPS streaming channel",
                    "channel": f"driver_{driver_id}",
                    "connection_type": "gps_streaming_integrated"
                }
            else:
                logger.warning(f"⚠️ Driver {driver_id} not streaming GPS - notifications unavailable")
                return {
                    "success": False,
                    "message": "Please start GPS streaming first to receive trip notifications",
                    "recommendation": "Use /drivers/streaming/start endpoint"
                }
                
        except Exception as e:
            logger.error(f"Failed to connect driver {driver_id} to notifications: {e}")
            return {
                "success": False,
                "message": f"Failed to connect to notifications: {str(e)}"
            }
    
    @classmethod
    async def disconnect_driver(cls, driver_id: str) -> Dict[str, Any]:
        """
        Disconnect driver from notification system.
        
        Args:
            driver_id: ID of the driver to disconnect
            
        Returns:
            Disconnection result
        """
        try:
            # Cancel any pending notifications
            if driver_id in cls.pending_notifications:
                pending = cls.pending_notifications[driver_id]
                if "timer_task" in pending:
                    pending["timer_task"].cancel()
                del cls.pending_notifications[driver_id]
                logger.info(f"🔕 Cancelled pending notifications for driver {driver_id}")
            
            return {
                "success": True,
                "message": "Disconnected from trip notifications",
                "driver_id": driver_id
            }
            
        except Exception as e:
            logger.error(f"Failed to disconnect driver {driver_id}: {e}")
            return {
                "success": False,
                "message": f"Failed to disconnect: {str(e)}"
            }
    
    @classmethod
    async def send_trip_notification_to_active_channel(
        cls, 
        session: Session,
        driver_id: str, 
        trip_id: str,
        trip_details: Dict[str, Any]
    ) -> bool:
        """
        Send trip request notification to driver via EXISTING Supabase channel (from GPS streaming).
        
        This method integrates with RealtimeLocationService to use the same channel
        that is already streaming GPS data.
        
        Args:
            session: Database session
            driver_id: ID of the driver to notify
            trip_id: ID of the trip
            trip_details: Trip information
            
        Returns:
            True if notification sent successfully
        """
        try:
            # Import here to avoid circular imports
            from src.services.realtime_location import RealtimeLocationService
            
            # Check if driver has an active GPS streaming channel
            if not RealtimeLocationService.is_driver_streaming(driver_id):
                logger.warning(f"⚠️ Driver {driver_id} not streaming GPS - cannot send trip notification")
                return False
            
            # Get driver and user info
            driver = session.exec(select(Driver).where(Driver.id == driver_id)).first()
            if not driver:
                logger.error(f"Driver {driver_id} not found for notification")
                return False
            
            driver_user = session.exec(select(User).where(User.id == driver.user_id)).first()
            
            # Prepare notification data with Tunisian context
            notification = {
                "type": "trip_request",
                "trip_id": trip_id,
                "driver_id": driver_id,
                "driver_name": driver_user.name if driver_user else "Unknown",
                "timeout_seconds": cls.NOTIFICATION_TIMEOUT,
                "timestamp": datetime.utcnow().isoformat(),
                "trip_details": {
                    "pickup_address": trip_details.get("pickup_address", "Adresse de ramassage inconnue"),
                    "destination_address": trip_details.get("destination_address", "Destination inconnue"), 
                    "estimated_distance_km": trip_details.get("estimated_distance_km", 0),
                    "estimated_cost_tnd": trip_details.get("estimated_cost_tnd", 0),  # TND currency
                    "rider_notes": trip_details.get("rider_notes", ""),
                    "requested_at": trip_details.get("requested_at"),
                    "trip_type": trip_details.get("trip_type", "regular")
                },
                "actions": [
                    {"type": "accept", "label": "قبول", "label_fr": "Accepter", "style": "success"},
                    {"type": "reject", "label": "رفض", "label_fr": "Refuser", "style": "danger"}
                ],
                "localization": {
                    "currency": "TND",
                    "distance_unit": "km",
                    "language": "ar_TN"  # Tunisian Arabic
                },
                "sound": {
                    "enabled": True,
                    "type": "trip_request",
                    "volume": 0.8
                },
                "visual": {
                    "priority": "high",
                    "flash": True,
                    "color": "#FF6B35"  # Orange color for urgency
                }
            }
            
            # Send via existing GPS streaming channel
            success = await cls._send_to_gps_channel(driver_id, notification)
            
            if success:
                logger.info(f"� Trip request notification sent to driver {driver_id} via GPS channel")
                
                # Start auto-rejection timer
                timer_task = asyncio.create_task(
                    cls._auto_reject_timer(session, driver_id, trip_id)
                )
                
                # Store pending notification
                cls.pending_notifications[driver_id] = {
                    "trip_id": trip_id,
                    "notification": notification,
                    "timer_task": timer_task,
                    "created_at": datetime.utcnow()
                }
                
                logger.info(f"⏰ Auto-rejection timer started for driver {driver_id}, trip {trip_id} "
                           f"({cls.NOTIFICATION_TIMEOUT}s)")
                
                return True
            else:
                logger.error(f"Failed to send notification to driver {driver_id}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to notify driver {driver_id} about trip {trip_id}: {e}")
            return False
    
    @classmethod
    async def _send_to_gps_channel(cls, driver_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message to driver via existing GPS streaming channel.
        
        This method integrates with RealtimeLocationService to send trip notifications
        through the same channel that streams GPS data.
        
        Args:
            driver_id: Driver ID
            message: Message to send
            
        Returns:
            True if sent successfully
        """
        try:
            # Import here to avoid circular imports
            from src.services.realtime_location import RealtimeLocationService
            
            # Check if driver has active streaming
            if not RealtimeLocationService.is_driver_streaming(driver_id):
                logger.error(f"No active GPS streaming for driver {driver_id}")
                return False
            
            # Get the GPS streaming channel and send trip notification
            # Note: We'll need to modify RealtimeLocationService to expose channel access
            success = await RealtimeLocationService.send_message_to_driver_channel(driver_id, message)
            
            if success:
                logger.info(f"📡 Trip notification sent to driver {driver_id} via GPS channel")
                return True
            else:
                logger.error(f"Failed to send message via GPS channel for driver {driver_id}")
                return False
            
        except Exception as e:
            logger.error(f"Error sending message to GPS channel for driver {driver_id}: {e}")
            return False
    
    @classmethod
    async def _auto_reject_timer(cls, session: Session, driver_id: str, trip_id: str):
        """
        Auto-reject trip if driver doesn't respond within timeout.
        
        Args:
            session: Database session
            driver_id: ID of the driver
            trip_id: ID of the trip
        """
        try:
            # Wait for timeout period
            await asyncio.sleep(cls.NOTIFICATION_TIMEOUT)
            
            # Check if notification is still pending
            if driver_id in cls.pending_notifications:
                pending = cls.pending_notifications[driver_id]
                if pending["trip_id"] == trip_id:
                    logger.warning(f"⏰ Auto-rejecting trip {trip_id} for driver {driver_id} - timeout reached")
                    
                    # Import here to avoid circular imports
                    from src.services.trip import TripService
                    
                    # Auto-reject the trip
                    result = await TripService.handle_driver_rejection(
                        session=session,
                        driver_id=driver_id,
                        trip_id=trip_id,
                        notes="تم الرفض تلقائياً - لا توجد استجابة خلال 20 ثانية (Auto-rejected due to timeout)"
                    )
                    
                    # Send timeout notification to driver via GPS channel
                    timeout_notification = {
                        "type": "trip_timeout",
                        "trip_id": trip_id,
                        "message": "تم رفض الرحلة تلقائياً - انتهت المهلة المحددة",
                        "message_fr": "Course automatiquement refusée - délai dépassé",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    await cls._send_to_gps_channel(driver_id, timeout_notification)
                    
                    # Clean up
                    del cls.pending_notifications[driver_id]
                    
                    logger.info(f"✅ Auto-rejection completed for trip {trip_id}")
                    
        except asyncio.CancelledError:
            logger.info(f"Auto-rejection timer cancelled for driver {driver_id}, trip {trip_id}")
        except Exception as e:
            logger.error(f"Error in auto-rejection timer for driver {driver_id}: {e}")
    
    @classmethod
    async def cancel_pending_notification(cls, driver_id: str, trip_id: str):
        """
        Cancel pending notification when driver responds.
        
        Args:
            driver_id: ID of the driver
            trip_id: ID of the trip
        """
        if driver_id in cls.pending_notifications:
            pending = cls.pending_notifications[driver_id]
            if pending["trip_id"] == trip_id:
                # Cancel timer
                if "timer_task" in pending:
                    pending["timer_task"].cancel()
                
                # Remove from pending
                del cls.pending_notifications[driver_id]
                logger.info(f"⏹️ Cancelled pending notification for driver {driver_id}, trip {trip_id}")
    
    @classmethod
    async def notify_rider_driver_response(
        cls,
        session: Session,
        rider_id: str,
        trip_id: str,
        response: str,  # "accepted" or "rejected"
        driver_info: Dict[str, Any]
    ):
        """
        Notify rider about driver's response to trip request.
        
        In a real implementation, this would send push notifications to the rider's mobile app.
        For now, we log this information and could send via rider's WebSocket if connected.
        
        Args:
            session: Database session
            rider_id: ID of the rider
            trip_id: ID of the trip
            response: Driver's response ("accepted" or "rejected")
            driver_info: Driver information
        """
        try:
            if response == "accepted":
                logger.info(f"🎉 RIDER NOTIFICATION: Trip {trip_id} accepted by driver "
                           f"{driver_info.get('name', 'Unknown')} (Taxi: {driver_info.get('taxi_number', 'N/A')})")
                
                # Send notification via Supabase real-time (works with frontend subscriptions)
                rider_notification = {
                    "type": "trip_accepted",
                    "trip_id": trip_id,
                    "driver_info": driver_info,
                    "message": f"Your trip has been accepted by {driver_info.get('name', 'driver')}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # The frontend listens to Supabase realtime changes on the trips table
                # When trip status changes to 'assigned', it automatically shows notification
                logger.info(f"📱 Notification prepared for rider {rider_id}: Trip accepted by driver")
                
                # If rider has active channel, send notification
                await cls._send_rider_notification(rider_id, rider_notification)
                
            elif response == "rejected":
                logger.info(f"📱 RIDER NOTIFICATION: Trip {trip_id} was rejected, searching for another driver...")
                
                rider_notification = {
                    "type": "trip_reassigning",
                    "trip_id": trip_id,
                    "message": "Looking for another driver...",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await cls._send_rider_notification(rider_id, rider_notification)
                
            elif response == "cancelled":
                logger.info(f"❌ RIDER NOTIFICATION: Trip {trip_id} was cancelled - no available drivers")
                
                rider_notification = {
                    "type": "trip_cancelled",
                    "trip_id": trip_id,
                    "message": "No drivers available at the moment. Please try again later.",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await cls._send_rider_notification(rider_id, rider_notification)
            
        except Exception as e:
            logger.error(f"Failed to notify rider {rider_id}: {e}")
    
    @classmethod
    async def _send_rider_notification(cls, rider_id: str, notification: Dict[str, Any]):
        """
        Send notification to rider via Supabase channel.
        
        Args:
            rider_id: Rider ID
            notification: Notification to send
        """
        try:
            logger.info(f"📱 RIDER {rider_id} NOTIFICATION: {notification}")
            
            # Send to rider's Supabase channel
            channel_name = f"rider_notifications:{rider_id}"
            success = await cls._send_channel_message(channel_name, notification)
            
            if success:
                logger.info(f"✅ Notification sent to rider {rider_id} via Supabase channel")
            else:
                logger.warning(f"⚠️ Failed to send notification to rider {rider_id} - channel may not be active")
            
        except Exception as e:
            logger.error(f"Error sending notification to rider {rider_id}: {e}")
    
    @classmethod
    def get_pending_notifications(cls) -> Dict[str, Dict[str, Any]]:
        """Get all pending notifications."""
        return cls.pending_notifications.copy()
    
    @classmethod
    async def broadcast_system_message(cls, message: str, message_type: str = "info"):
        """
        Broadcast system message to all drivers with active GPS streaming.
        
        Args:
            message: Message to broadcast
            message_type: Type of message (info, warning, error)
        """
        try:
            # Import here to avoid circular imports
            from src.services.realtime_location import RealtimeLocationService
            
            # Get all active streaming drivers
            streaming_drivers = list(RealtimeLocationService._active_streams.keys())
            
            if not streaming_drivers:
                logger.info("No active streaming drivers to broadcast to")
                return
            
            notification = {
                "type": "system_message",
                "message": message,
                "message_type": message_type,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            success_count = 0
            for driver_id in streaming_drivers:
                try:
                    success = await cls._send_to_gps_channel(driver_id, notification)
                    if success:
                        success_count += 1
                except Exception as e:
                    logger.error(f"Failed to send broadcast to driver {driver_id}: {e}")
            
            logger.info(f"📢 Broadcast sent to {success_count}/{len(streaming_drivers)} active drivers")
            
        except Exception as e:
            logger.error(f"Error broadcasting system message: {e}")
    
    # Alias method for backward compatibility with TripService
    @classmethod
    async def notify_driver_trip_request(
        cls, 
        session: Session,
        driver_id: str, 
        trip_id: str,
        trip_details: Dict[str, Any]
    ) -> bool:
        """
        Alias for send_trip_notification_to_active_channel for backward compatibility.
        """
        return await cls.send_trip_notification_to_active_channel(
            session, driver_id, trip_id, trip_details
        )
        """
        Send trip request notification to driver via Supabase channel with auto-rejection timer.
        
        Args:
            session: Database session
            driver_id: ID of the driver to notify
            trip_id: ID of the trip
            trip_details: Trip information
            
        Returns:
            True if notification sent successfully
        """
        try:
            # Get driver and user info
            driver = session.exec(select(Driver).where(Driver.id == driver_id)).first()
            if not driver:
                logger.error(f"Driver {driver_id} not found for notification")
                return False
            
            driver_user = session.exec(select(User).where(User.id == driver.user_id)).first()
            
            # Prepare notification data with Tunisian context
            notification = {
                "type": "trip_request",
                "trip_id": trip_id,
                "driver_id": driver_id,
                "driver_name": driver_user.name if driver_user else "Unknown",
                "timeout_seconds": cls.NOTIFICATION_TIMEOUT,
                "timestamp": datetime.utcnow().isoformat(),
                "trip_details": {
                    "pickup_address": trip_details.get("pickup_address", "Adresse de ramassage inconnue"),
                    "destination_address": trip_details.get("destination_address", "Destination inconnue"), 
                    "estimated_distance_km": trip_details.get("estimated_distance_km", 0),
                    "estimated_cost_tnd": trip_details.get("estimated_cost_tnd", 0),  # TND currency
                    "rider_notes": trip_details.get("rider_notes", ""),
                    "requested_at": trip_details.get("requested_at")
                },
                "actions": [
                    {"type": "accept", "label": "قبول", "label_fr": "Accepter", "style": "success"},
                    {"type": "reject", "label": "رفض", "label_fr": "Refuser", "style": "danger"}
                ],
                "localization": {
                    "currency": "TND",
                    "distance_unit": "km",
                    "language": "ar_TN"  # Tunisian Arabic
                },
                "sound": {
                    "enabled": True,
                    "type": "trip_request",
                    "volume": 0.8
                },
                "visual": {
                    "priority": "high",
                    "flash": True,
                    "color": "#FF6B35"  # Orange color for urgency
                }
            }
            
            # Send via Supabase channel if connected
            if driver_id in cls.active_channels:
                try:
                    success = await cls._send_channel_message(driver_id, notification)
                    if success:
                        logger.info(f"🔔 Trip request notification sent to driver {driver_id} via Supabase channel")
                    else:
                        logger.error(f"Failed to send notification to driver {driver_id}")
                except Exception as e:
                    logger.error(f"Failed to send Supabase notification to driver {driver_id}: {e}")
                    return False
            else:
                logger.warning(f"⚠️ Driver {driver_id} not connected to Supabase channel")
                return False
            
            # Start auto-rejection timer
            timer_task = asyncio.create_task(
                cls._auto_reject_timer(session, driver_id, trip_id)
            )
            
            # Store pending notification
            cls.pending_notifications[driver_id] = {
                "trip_id": trip_id,
                "notification": notification,
                "timer_task": timer_task,
                "created_at": datetime.utcnow()
            }
            
            logger.info(f"⏰ Auto-rejection timer started for driver {driver_id}, trip {trip_id} "
                       f"({cls.NOTIFICATION_TIMEOUT}s)")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to notify driver {driver_id} about trip {trip_id}: {e}")
            return False
    
    @classmethod
    async def _send_channel_message(cls, channel_name: str, message: Dict[str, Any]) -> bool:
        """
        Send message via Supabase Realtime broadcast.
        
        Uses Supabase REST API to broadcast messages to subscribed clients.
        
        Args:
            channel_name: Channel name (e.g., 'rider_notifications:user_id')
            message: Message to send
            
        Returns:
            True (always, to not block flow even if no subscribers)
        """
        try:
            from src.core.settings import get_settings
            import httpx
            
            settings = get_settings()
            
            # Use Supabase REST API to broadcast
            # Format: POST https://{project}.supabase.co/rest/v1/rpc/broadcast
            url = f"{settings.SUPABASE_URL}/realtime/v1/api/broadcast"
            
            headers = {
                "apikey": settings.SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "topic": channel_name,
                "event": "notification",
                "payload": message
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=5.0)
                
            if response.status_code in [200, 201, 204]:
                logger.info(f"📡 Broadcast sent to channel '{channel_name}'")
            else:
                logger.warning(f"⚠️ Broadcast response: {response.status_code}")
            
            # Always return True - if no one is listening, that's okay
            return True
            
        except Exception as e:
            logger.warning(f"Could not broadcast to '{channel_name}': {e}")
            # Don't fail the main flow if broadcast doesn't work
            return True
    
    @classmethod
    async def _auto_reject_timer(cls, session: Session, driver_id: str, trip_id: str):
        """
        Auto-reject trip if driver doesn't respond within timeout.
        
        Args:
            session: Database session
            driver_id: ID of the driver
            trip_id: ID of the trip
        """
        try:
            # Wait for timeout period
            await asyncio.sleep(cls.NOTIFICATION_TIMEOUT)
            
            # Check if notification is still pending
            if driver_id in cls.pending_notifications:
                pending = cls.pending_notifications[driver_id]
                if pending["trip_id"] == trip_id:
                    logger.warning(f"⏰ Auto-rejecting trip {trip_id} for driver {driver_id} - timeout reached")
                    
                    # Import here to avoid circular imports
                    from src.services.trip import TripService
                    
                    # Auto-reject the trip
                    result = TripService.handle_driver_rejection(
                        session=session,
                        driver_id=driver_id,
                        trip_id=trip_id,
                        notes="تم الرفض تلقائياً - لا توجد استجابة خلال 20 ثانية (Auto-rejected due to timeout)"
                    )
                    
                    # Send timeout notification to driver
                    timeout_notification = {
                        "type": "trip_timeout",
                        "trip_id": trip_id,
                        "message": "تم رفض الرحلة تلقائياً - انتهت المهلة المحددة",
                        "message_fr": "Course automatiquement refusée - délai dépassé",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    await cls._send_channel_message(driver_id, timeout_notification)
                    
                    # Clean up
                    del cls.pending_notifications[driver_id]
                    
                    logger.info(f"✅ Auto-rejection completed for trip {trip_id}")
                    
        except asyncio.CancelledError:
            logger.info(f"Auto-rejection timer cancelled for driver {driver_id}, trip {trip_id}")
        except Exception as e:
            logger.error(f"Error in auto-rejection timer for driver {driver_id}: {e}")
    
    @classmethod
    async def cancel_pending_notification(cls, driver_id: str, trip_id: str):
        """
        Cancel pending notification when driver responds.
        
        Args:
            driver_id: ID of the driver
            trip_id: ID of the trip
        """
        if driver_id in cls.pending_notifications:
            pending = cls.pending_notifications[driver_id]
            if pending["trip_id"] == trip_id:
                # Cancel timer
                if "timer_task" in pending:
                    pending["timer_task"].cancel()
                
                # Remove from pending
                del cls.pending_notifications[driver_id]
                logger.info(f"⏹️ Cancelled pending notification for driver {driver_id}, trip {trip_id}")
    
    @classmethod
    async def notify_rider_driver_response(
        cls,
        session: Session,
        rider_id: str,
        trip_id: str,
        response: str,  # "accepted" or "rejected"
        driver_info: Dict[str, Any]
    ):
        """
        Notify rider about driver's response to trip request.
        
        In a real implementation, this would send push notifications to the rider's mobile app.
        For now, we log this information.
        
        Args:
            session: Database session
            rider_id: ID of the rider
            trip_id: ID of the trip
            response: Driver's response ("accepted" or "rejected")
            driver_info: Driver information
        """
        try:
            if response == "accepted":
                logger.info(f"🎉 RIDER NOTIFICATION: Trip {trip_id} accepted by driver "
                           f"{driver_info.get('name', 'Unknown')} (Taxi: {driver_info.get('taxi_number', 'N/A')})")
                # Notification sent via Supabase realtime on trip status change
                # Frontend listens to trips table changes and shows notification
                logger.info(f"📱 Trip accepted notification for rider {rider_id}")
                
            elif response == "rejected":
                logger.info(f"📱 RIDER NOTIFICATION: Trip {trip_id} was rejected, searching for another driver...")
                # System automatically reassigns trip, notification sent via real-time updates
                logger.info(f"🔄 Reassignment notification for rider {rider_id}")
                
            elif response == "cancelled":
                logger.info(f"❌ RIDER NOTIFICATION: Trip {trip_id} was cancelled - no available drivers")
                # Cancellation updates trip status, frontend listens via Supabase realtime
                logger.info(f"❌ Cancellation notification for rider {rider_id}")
            
        except Exception as e:
            logger.error(f"Failed to notify rider {rider_id}: {e}")
    
    @classmethod
    def get_connected_drivers(cls) -> List[str]:
        """Get list of currently connected driver IDs."""
        return list(cls.active_connections.keys())
    
    @classmethod
    def get_pending_notifications(cls) -> Dict[str, Dict[str, Any]]:
        """Get all pending notifications."""
        return cls.pending_notifications.copy()
    
    @classmethod
    async def broadcast_system_message(cls, message: str, message_type: str = "info"):
        """
        Broadcast system message to all connected drivers.
        
        Args:
            message: Message to broadcast
            message_type: Type of message (info, warning, error)
        """
        if not cls.active_channels:
            logger.info("No connected drivers to broadcast to")
            return
        
        notification = {
            "type": "system_message",
            "message": message,
            "message_type": message_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        disconnected_drivers = []
        for driver_id in cls.active_channels.keys():
            try:
                await cls._send_channel_message(driver_id, notification)
            except Exception as e:
                logger.error(f"Failed to send broadcast to driver {driver_id}: {e}")
                disconnected_drivers.append(driver_id)
        
        # Clean up disconnected drivers
        for driver_id in disconnected_drivers:
            await cls.disconnect_driver(driver_id)
        
        logger.info(f"📢 Broadcast sent to {len(cls.active_channels)} connected drivers")
