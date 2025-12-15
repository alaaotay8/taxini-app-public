"""
Geocoding service for converting coordinates to addresses using Mapbox API.
Optimized for Tunisia with street names, POIs, neighborhoods, and cities.
"""

import httpx
from typing import Optional, Dict, Any
from src.core.settings import Settings

# Get settings instance
settings = Settings()


class GeocodingService:
    """Service for reverse geocoding coordinates to professional addresses."""
    
    def __init__(self):
        self.mapbox_token = settings.mapbox_access_token
        self.base_url = "https://api.mapbox.com/geocoding/v5/mapbox.places"
        # Cache to avoid repeated API calls for same coordinates
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def _cache_key(self, lat: float, lon: float) -> str:
        """Generate cache key from coordinates (rounded to 4 decimals)."""
        return f"{round(lat, 4)},{round(lon, 4)}"
    
    async def reverse_geocode(
        self, 
        latitude: float, 
        longitude: float,
        include_coords: bool = True
    ) -> str:
        """
        Convert coordinates to professional address with street, POI, neighborhood, city.
        
        Format: "Street Name, Near POI, Neighborhood, City (lat°, lon°)"
        Example: "Avenue Habib Bourguiba, Near Théâtre Municipal, Centre Ville, Tunis (36.8065°, 10.1815°)"
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            include_coords: Whether to append coordinates to the address
            
        Returns:
            Professionally formatted address string
        """
        if not self.mapbox_token:
            return f"{latitude:.4f}°, {longitude:.4f}°"
        
        # Check cache first
        cache_key = self._cache_key(latitude, longitude)
        if cache_key in self._cache:
            return self._format_address(self._cache[cache_key], latitude, longitude, include_coords)
        
        try:
            # Mapbox Reverse Geocoding with multiple place types for best results
            url = f"{self.base_url}/{longitude},{latitude}.json"
            params = {
                "access_token": self.mapbox_token,
                "types": "address,street,poi,neighborhood,locality",
                "limit": 5,  # Get top 5 results for best match
                "language": "en"  # English for international compatibility
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=5.0)
                response.raise_for_status()
                data = response.json()
                
                if data.get("features") and len(data["features"]) > 0:
                    # Extract detailed location info from best match
                    location_data = self._extract_location_details(data["features"])
                    
                    # Cache the result
                    self._cache[cache_key] = location_data
                    
                    return self._format_address(location_data, latitude, longitude, include_coords)
                    
        except Exception as e:
            logger.error(f"Geocoding error for ({latitude}, {longitude}): {e}")
        
        return f"{latitude:.4f}°, {longitude:.4f}°"
    
    def _extract_location_details(self, features: list) -> Dict[str, Any]:
        """
        Extract street, POI, neighborhood, and city from Mapbox features.
        
        Returns dict with: street, poi, neighborhood, city, governorate, full_address
        """
        details = {
            "street": None,
            "poi": None,
            "neighborhood": None,
            "city": None,
            "governorate": None,
            "full_address": None
        }
        
        # Process features in order (most specific first)
        for feature in features:
            place_type = feature.get("place_type", [])
            text = feature.get("text", "")
            context = feature.get("context", [])
            
            # Extract POI (point of interest - landmarks, shops, etc.)
            if "poi" in place_type and not details["poi"]:
                category = feature.get("properties", {}).get("category")
                details["poi"] = text
            
            # Extract street name
            if ("address" in place_type or "street" in place_type) and not details["street"]:
                details["street"] = text
            
            # Extract from context (neighborhood, city, governorate)
            for ctx in context:
                ctx_id = ctx.get("id", "")
                ctx_text = ctx.get("text", "")
                
                if "neighborhood" in ctx_id and not details["neighborhood"]:
                    details["neighborhood"] = ctx_text
                elif "locality" in ctx_id or "place" in ctx_id:
                    if not details["city"]:
                        details["city"] = ctx_text
                elif "region" in ctx_id and not details["governorate"]:
                    details["governorate"] = ctx_text
            
            # Store full address from first feature
            if not details["full_address"]:
                details["full_address"] = feature.get("place_name", "")
        
        return details
    
    def _format_address(
        self, 
        details: Dict[str, Any], 
        lat: float, 
        lon: float,
        include_coords: bool
    ) -> str:
        """
        Format address professionally: "Street, Near POI, Neighborhood, City (coords)"
        """
        parts = []
        
        # Add street name
        if details.get("street"):
            parts.append(details["street"])
        
        # Add POI with "Near" prefix
        if details.get("poi"):
            parts.append(f"Near {details['poi']}")
        
        # Add neighborhood
        if details.get("neighborhood"):
            parts.append(details["neighborhood"])
        
        # Add city
        if details.get("city"):
            parts.append(details["city"])
        
        # Build address string
        address = ", ".join(parts) if parts else details.get("full_address", "Unknown Location")
        
        # Append coordinates if requested
        if include_coords:
            address += f" ({lat:.4f}°, {lon:.4f}°)"
        
        return address
