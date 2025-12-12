"""
Geocoding service for converting coordinates to addresses.
Uses Mapbox Geocoding API for reverse geocoding.
"""

import httpx
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class GeocodingService:
    """Service for geocoding operations."""
    
    def __init__(self, mapbox_token: str):
        self.mapbox_token = mapbox_token
        self.base_url = "https://api.mapbox.com/geocoding/v5/mapbox.places"
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Convert coordinates to a human-readable address.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Formatted address string or None if geocoding fails
        """
        try:
            url = f"{self.base_url}/{longitude},{latitude}.json"
            params = {
                "access_token": self.mapbox_token,
                "types": "address,poi,place",
                "limit": 1,
                "language": "en"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=5.0)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("features") and len(data["features"]) > 0:
                        feature = data["features"][0]
                        
                        # Extract address components
                        place_name = feature.get("place_name", "")
                        
                        # Try to build a detailed address
                        context = feature.get("context", [])
                        address_parts = []
                        
                        # Get street/POI name
                        text = feature.get("text", "")
                        if text:
                            address_parts.append(text)
                        
                        # Extract neighborhood, place (city), and region
                        for item in context:
                            item_id = item.get("id", "")
                            if item_id.startswith("neighborhood"):
                                address_parts.append(item.get("text", ""))
                            elif item_id.startswith("place"):
                                address_parts.append(item.get("text", ""))
                                break  # Stop after city name
                        
                        if address_parts:
                            # Format: "Street Name, Neighborhood, City (lat, lon)"
                            formatted_address = ", ".join(address_parts)
                            formatted_address += f" ({latitude:.4f}°, {longitude:.4f}°)"
                            return formatted_address
                        else:
                            # Fallback to place_name
                            return f"{place_name} ({latitude:.4f}°, {longitude:.4f}°)"
                    
                logger.warning(f"No geocoding results for {latitude}, {longitude}")
                return f"{latitude:.4f}°, {longitude:.4f}°"
                    
        except Exception as e:
            logger.error(f"Geocoding error for {latitude}, {longitude}: {e}")
            return f"{latitude:.4f}°, {longitude:.4f}°"
    
    async def geocode_trip_locations(self, trip) -> Dict[str, Optional[str]]:
        """
        Geocode both pickup and destination for a trip.
        
        Args:
            trip: Trip object with coordinates
            
        Returns:
            Dictionary with pickup_address and destination_address
        """
        pickup_address = None
        destination_address = None
        
        if trip.pickup_latitude and trip.pickup_longitude:
            pickup_address = await self.reverse_geocode(
                trip.pickup_latitude, 
                trip.pickup_longitude
            )
        
        if trip.destination_latitude and trip.destination_longitude:
            destination_address = await self.reverse_geocode(
                trip.destination_latitude,
                trip.destination_longitude
            )
        
        return {
            "pickup_address": pickup_address,
            "destination_address": destination_address
        }
