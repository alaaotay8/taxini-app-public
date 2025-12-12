"""
Pure WebSocket Channel GPS Streaming

NO TABLES - Just direct channel broadcasting!
Frontend subscribes to channel 'driver_{driver_id}' and gets live GPS data.
"""

import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime
from realtime import AsyncRealtimeClient
from sqlmodel import select
from src.core.settings import settings

logger = logging.getLogger(__name__)


class RealtimeLocationService:
    """Pure WebSocket GPS streaming - no database tables."""
    
    # Hardcoded GPS route (39 coordinates)
    GPS_ROUTE = [
        {"lat": 33.8938, "lng": 35.5018},  # Beirut, Lebanon - Start
        {"lat": 33.8948, "lng": 35.5028},
        {"lat": 33.8958, "lng": 35.5038},
        {"lat": 33.8968, "lng": 35.5048},
        {"lat": 33.8978, "lng": 35.5058},
        {"lat": 33.8988, "lng": 35.5068},
        {"lat": 33.8998, "lng": 35.5078},
        {"lat": 33.9008, "lng": 35.5088},
        {"lat": 33.9018, "lng": 35.5098},
        {"lat": 33.9028, "lng": 35.5108},
        {"lat": 33.9028, "lng": 35.5118},
        {"lat": 33.9028, "lng": 35.5128},
        {"lat": 33.9038, "lng": 35.5138},
        {"lat": 33.9048, "lng": 35.5148},
        {"lat": 33.9058, "lng": 35.5158},
        {"lat": 33.9068, "lng": 35.5168},
        {"lat": 33.9078, "lng": 35.5178},
        {"lat": 33.9088, "lng": 35.5178},
        {"lat": 33.9098, "lng": 35.5178},
        {"lat": 33.9108, "lng": 35.5178},
        {"lat": 33.9108, "lng": 35.5168},
        {"lat": 33.9108, "lng": 35.5158},
        {"lat": 33.9098, "lng": 35.5148},
        {"lat": 33.9088, "lng": 35.5138},
        {"lat": 33.9078, "lng": 35.5128},
        {"lat": 33.9068, "lng": 35.5118},
        {"lat": 33.9058, "lng": 35.5108},
        {"lat": 33.9048, "lng": 35.5098},
        {"lat": 33.9038, "lng": 35.5088},
        {"lat": 33.9028, "lng": 35.5078},
        {"lat": 33.9018, "lng": 35.5068},
        {"lat": 33.9008, "lng": 35.5058},
        {"lat": 33.8998, "lng": 35.5048},
        {"lat": 33.8988, "lng": 35.5038},
        {"lat": 33.8978, "lng": 35.5028},
        {"lat": 33.8968, "lng": 35.5018},
        {"lat": 33.8958, "lng": 35.5008},
        {"lat": 33.8948, "lng": 35.4998},
        {"lat": 33.8938, "lng": 35.5008},
    ]
    
    # Track active streams
    _active_streams: Dict[str, Dict] = {}
    _streaming_tasks: Dict[str, asyncio.Task] = {}
    
    @classmethod
    async def start_driver_streaming(cls, driver_id: str) -> Dict:
        """Start pure WebSocket GPS streaming."""
        try:
            if driver_id in cls._active_streams:
                return {"success": True, "message": "Already streaming", "channel": f"driver_{driver_id}"}
            
            # Initialize stream
            cls._active_streams[driver_id] = {
                "started_at": datetime.utcnow(),
                "updates_sent": 0
            }
            
            # Start streaming task
            task = asyncio.create_task(cls._stream_gps_to_channel(driver_id))
            cls._streaming_tasks[driver_id] = task
            
            # Channel name for the client to subscribe to
            channel_name = f"driver_{driver_id}"
            
            logger.info(f"🚀 Started pure WebSocket streaming for driver {driver_id}")
            return {"success": True, "message": "WebSocket streaming started", "channel": channel_name}
            
        except Exception as e:
            logger.error(f"Failed to start streaming: {e}")
            return {"success": False, "message": str(e)}
    
    @classmethod
    async def stop_driver_streaming(cls, driver_id: str) -> Dict:
        """Stop WebSocket streaming."""
        try:
            if driver_id in cls._streaming_tasks:
                cls._streaming_tasks[driver_id].cancel()
                del cls._streaming_tasks[driver_id]
            
            stream_info = cls._active_streams.pop(driver_id, {})
            
            logger.info(f"⏹️ Stopped WebSocket streaming for driver {driver_id}")
            return {
                "success": True,
                "message": "WebSocket streaming stopped",
                "updates_sent": stream_info.get("updates_sent", 0)
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    @classmethod
    def is_driver_streaming(cls, driver_id: str) -> bool:
        return driver_id in cls._active_streams
    
    @classmethod
    def get_streaming_status(cls, driver_id: str) -> Optional[Dict]:
        return cls._active_streams.get(driver_id)
    
    @classmethod
    def manage_streaming_based_on_status(
        cls,
        new_status: str, 
        old_status: str, 
        driver_id: str, 
        background_tasks
    ) -> bool:
        """
        Helper function to manage streaming based on status changes.
        
        Args:
            new_status: New driver status (DriverStatus enum value)
            old_status: Previous driver status
            driver_id: Driver ID
            background_tasks: FastAPI background tasks
            
        Returns:
            bool: Whether streaming is currently active
        """
        from src.models.enums import DriverStatus
        
        if new_status in [DriverStatus.ONLINE.value, DriverStatus.ON_TRIP.value]:
            background_tasks.add_task(cls.start_driver_streaming, driver_id)
            logger.info(f"Started streaming for driver {driver_id}")
            return True
            
        elif old_status in ["online", "on_trip"] and new_status == DriverStatus.OFFLINE.value:
            background_tasks.add_task(cls.stop_driver_streaming, driver_id)
            logger.info(f"Stopped streaming for driver {driver_id}")
            return False
            
        return False
    
    @classmethod
    async def _stream_gps_to_channel(cls, driver_id: str):
        """Stream GPS directly to WebSocket channel and save location every 1 minute."""
        from src.db.session import get_session
        from src.services.location import LocationService
        
        client = None
        last_lat = None
        last_lng = None
        save_counter = 0
        
        try:
            # Create async Realtime client for WebSocket
            realtime_url = settings.supabase_url.replace("https://", "wss://").replace("http://", "ws://") + "/realtime/v1/websocket"
            
            logger.info(f"🔗 Connecting to: {realtime_url}")
            logger.info(f"🔑 Using API Key: {settings.supabase_api_key[:10]}...")
            
            client = AsyncRealtimeClient(realtime_url, settings.supabase_api_key)
            
            # Connect to WebSocket first
            await client.connect()
            logger.info(f"✅ WebSocket connected successfully!")
            
            # Create channel with broadcast config - use driver-specific channel
            channel_name = f"driver_{driver_id}"
            channel = client.channel(channel_name, {"config": {"broadcast": {"ack": False, "self": False}}})
            
            # Subscribe to channel with callback
            def on_subscribe(status, err):
                if err:
                    logger.error(f"❌ Channel subscription error: {err}")
                else:
                    logger.info(f"📡 Channel subscription status: {status}")
            
            await channel.subscribe(on_subscribe)
            logger.info(f"📡 Subscribed to channel '{channel_name}'")
            
            logger.info(f"📡 Pure WebSocket streaming started for driver {driver_id}")
            logger.info(f"🌐 Channel: '{channel_name}'")
            logger.info(f"📍 Broadcasting {len(cls.GPS_ROUTE)} GPS coordinates")
            logger.info(f"💾 Location will be saved every 1 minute (12 updates)")
            
            step = 0
            while driver_id in cls._active_streams:
                # Get next GPS coordinate
                coord = cls.GPS_ROUTE[step % len(cls.GPS_ROUTE)]
                lat, lng = coord["lat"], coord["lng"]
                
                # Update last coordinates
                last_lat = lat
                last_lng = lng
                
                # Create GPS payload
                gps_data = {
                    "driver_id": driver_id,
                    "latitude": lat,
                    "longitude": lng,
                    "timestamp": datetime.utcnow().isoformat(),
                    "step": step + 1,
                    "total_steps": len(cls.GPS_ROUTE)
                }
                
                # 🔴 PURE WEBSOCKET BROADCAST - NO TABLES!
                try:
                    # Send GPS data via broadcast
                    await channel.send_broadcast("gps_update", gps_data)
                    
                    logger.info(f"🔴 LIVE GPS BROADCAST: Driver {driver_id} → ({lat}, {lng}) [Step {step + 1}]")
                    logger.info(f"📡 Broadcast sent to '{channel_name}' channel!")
                    
                except Exception as broadcast_error:
                    logger.error(f"❌ WebSocket broadcast failed: {broadcast_error}")
                    # Continue anyway - this is expected during development
                
                # 💾 SAVE LOCATION TO DATABASE EVERY 1 MINUTE (12 * 5 seconds = 60 seconds)
                save_counter += 1
                if save_counter >= 12 and last_lat is not None and last_lng is not None:
                    try:
                        # Get database session
                        session = next(get_session())
                        
                        # Get the user_id associated with this driver_id
                        from src.models.user import Driver
                        driver_record = session.exec(
                            select(Driver).where(Driver.id == driver_id)
                        ).first()
                        
                        if driver_record:
                            user_id = driver_record.user_id
                            
                            # Save location using existing LocationService
                            result = LocationService.upsert_location(
                                session=session,
                                user_id=user_id,  # Use the user_id, not driver_id
                                latitude=last_lat,
                                longitude=last_lng,
                                role="driver"
                            )
                            
                            if result["success"]:
                                logger.info(f"💾 LOCATION SAVED: Driver {driver_id} (User {user_id}) → ({last_lat}, {last_lng})")
                            else:
                                logger.error(f"❌ Failed to save location for driver {driver_id}: {result['message']}")
                        else:
                            logger.error(f"❌ Driver record not found for driver_id: {driver_id}")
                        
                        session.close()
                        
                    except Exception as db_error:
                        logger.error(f"❌ Database error saving location: {db_error}")
                    
                    # Reset counter
                    save_counter = 0
                
                # Update stats
                cls._active_streams[driver_id]["updates_sent"] += 1
                
                # Wait 5 seconds
                await asyncio.sleep(5)
                step += 1
            
            logger.info(f"✅ WebSocket streaming completed for driver {driver_id}")
            
        except asyncio.CancelledError:
            logger.info(f"🛑 WebSocket streaming cancelled for driver {driver_id}")
        except Exception as e:
            logger.error(f"❌ Error in WebSocket streaming: {e}")
        finally:
            # Clean up
            if client:
                try:
                    await client.disconnect()
                    logger.info(f"🔌 WebSocket disconnected")
                except Exception:
                    pass
            
            # Remove from tracking dictionaries
            cls._active_streams.pop(driver_id, None)
            cls._streaming_tasks.pop(driver_id, None)
