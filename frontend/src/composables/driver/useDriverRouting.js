/**
 * Driver Routing Composable
 * Manages route visualization for driver:
 * - Trip route (pickup → destination) in yellow
 * - Driver-to-pickup route in blue
 * - Real-time progress tracking
 */

import { ref, computed, watch } from 'vue'
import mapboxgl from 'mapbox-gl'

export function useDriverRouting(map, driverLocation) {
  // Route data
  const tripRoute = ref(null) // Pickup → Destination
  const driverToPickupRoute = ref(null) // Driver → Pickup
  
  // Route layers
  const tripRouteLayerId = 'trip-route-layer'
  const driverRouteLayerId = 'driver-to-pickup-layer'
  const tripRouteSourceId = 'trip-route-source'
  const driverRouteSourceId = 'driver-to-pickup-source'
  
  // State
  const isRoutesVisible = ref(false)
  const routeMode = ref(null) // 'preview' | 'to-pickup' | 'in-trip'

  /**
   * Fetch route from Mapbox Directions API
   */
  const fetchRoute = async (start, end) => {
    try {
      const url = `https://api.mapbox.com/directions/v5/mapbox/driving/${start.lng},${start.lat};${end.lng},${end.lat}?geometries=geojson&access_token=${mapboxgl.accessToken}`
      console.log('🛣️ Fetching route:', { start, end })
      
      const response = await fetch(url)
      
      if (!response.ok) {
        console.error('Route fetch failed:', response.status, response.statusText)
        return null
      }
      
      const data = await response.json()
      
      if (data.routes && data.routes.length > 0) {
        console.log('✅ Route fetched successfully:', data.routes[0].geometry.coordinates.length, 'points')
        return data.routes[0].geometry
      } else {
        console.warn('⚠️ No routes found in response:', data)
        return null
      }
    } catch (error) {
      console.error('❌ Error fetching route:', error)
      return null
    }
  }

  /**
   * Add route layer to map
   */
  const addRouteLayer = (sourceId, layerId, color, width = 6) => {
    if (!map.value) return

    // Remove existing layer and source if present
    if (map.value.getLayer(layerId)) {
      map.value.removeLayer(layerId)
    }
    if (map.value.getSource(sourceId)) {
      map.value.removeSource(sourceId)
    }

    // Add source
    map.value.addSource(sourceId, {
      type: 'geojson',
      data: {
        type: 'Feature',
        properties: {},
        geometry: {
          type: 'LineString',
          coordinates: []
        }
      }
    })

    // Add layer
    map.value.addLayer({
      id: layerId,
      type: 'line',
      source: sourceId,
      layout: {
        'line-join': 'round',
        'line-cap': 'round'
      },
      paint: {
        'line-color': color,
        'line-width': width,
        'line-opacity': 0.8
      }
    })
  }

  /**
   * Update route on map
   */
  const updateRoute = (sourceId, geometry) => {
    if (!map.value || !geometry) return

    const source = map.value.getSource(sourceId)
    if (source) {
      source.setData({
        type: 'Feature',
        properties: {},
        geometry: geometry
      })
    }
  }

  /**
   * Show trip route preview (pickup → destination)
   * Called when driver receives trip request
   */
  const showTripRoutePreview = async (pickupLocation, destinationLocation) => {
    console.log('🗺️ showTripRoutePreview called')
    
    if (!map.value) {
      console.error('❌ Map not initialized')
      return
    }
    
    if (!pickupLocation?.longitude || !pickupLocation?.latitude) {
      console.error('❌ Invalid pickup location:', pickupLocation)
      return
    }
    
    if (!destinationLocation?.longitude || !destinationLocation?.latitude) {
      console.error('❌ Invalid destination location:', destinationLocation)
      return
    }

    console.log('📍 Valid coordinates, initializing layer...')

    // Initialize layers if needed
    if (!map.value.getLayer(tripRouteLayerId)) {
      console.log('Creating trip route layer')
      addRouteLayer(tripRouteSourceId, tripRouteLayerId, '#FFC107', 6) // Yellow
    }

    console.log('🛣️ Fetching route...')
    // Fetch and display trip route
    const route = await fetchRoute(
      { lng: pickupLocation.longitude, lat: pickupLocation.latitude },
      { lng: destinationLocation.longitude, lat: destinationLocation.latitude }
    )

    if (route) {
      console.log('✅ Route fetched, updating map...')
      tripRoute.value = route
      updateRoute(tripRouteSourceId, route)
      isRoutesVisible.value = true
      routeMode.value = 'preview'
      
      // Fit map to show entire route
      const coordinates = route.coordinates
      const bounds = coordinates.reduce((bounds, coord) => {
        return bounds.extend(coord)
      }, new mapboxgl.LngLatBounds(coordinates[0], coordinates[0]))
      
      map.value.fitBounds(bounds, {
        padding: 100,
        duration: 1000
      })
      
      console.log('✅ Route preview displayed successfully')
    } else {
      console.error('❌ Failed to fetch route')
    }
  }

  /**
   * Show driver-to-pickup route (in addition to trip route)
   * Called when driver accepts the trip
   */
  const showDriverToPickupRoute = async (pickupLocation) => {
    console.log('🗺️ Showing driver-to-pickup route (BLUE)')
    
    if (!map.value || !driverLocation.value) {
      console.error('Map or driver location not available')
      return
    }

    // Initialize layers if needed
    if (!map.value.getLayer(driverRouteLayerId)) {
      addRouteLayer(driverRouteSourceId, driverRouteLayerId, '#2196F3', 7) // Blue, thicker line
    } else {
      // Make sure layer is visible and blue
      map.value.setLayoutProperty(driverRouteLayerId, 'visibility', 'visible')
      map.value.setPaintProperty(driverRouteLayerId, 'line-color', '#2196F3')
      map.value.setPaintProperty(driverRouteLayerId, 'line-width', 7)
    }

    // Fetch and display driver-to-pickup route
    const route = await fetchRoute(
      { lng: driverLocation.value.longitude, lat: driverLocation.value.latitude },
      { lng: pickupLocation.longitude, lat: pickupLocation.latitude }
    )

    if (route) {
      driverToPickupRoute.value = route
      updateRoute(driverRouteSourceId, route)
      routeMode.value = 'to-pickup'
      
      console.log('✅ Driver-to-pickup route displayed in BLUE')
      
      // Keep both routes visible - trip route (yellow) + driver route (blue)
      // Fit map to show both routes
      if (tripRoute.value) {
        const allCoordinates = [
          ...tripRoute.value.coordinates,
          ...route.coordinates
        ]
        const bounds = allCoordinates.reduce((bounds, coord) => {
          return bounds.extend(coord)
        }, new mapboxgl.LngLatBounds(allCoordinates[0], allCoordinates[0]))
        
        map.value.fitBounds(bounds, {
          padding: 100,
          duration: 1000
        })
      }
    }
  }

  /**
   * Update driver-to-pickup route in real-time as driver moves
   */
  const updateDriverToPickupRoute = async (pickupLocation) => {
    if (!map.value || !driverLocation.value || routeMode.value !== 'to-pickup') {
      return
    }

    const route = await fetchRoute(
      { lng: driverLocation.value.longitude, lat: driverLocation.value.latitude },
      { lng: pickupLocation.longitude, lat: pickupLocation.latitude }
    )

    if (route) {
      driverToPickupRoute.value = route
      updateRoute(driverRouteSourceId, route)
    }
  }

  /**
   * Hide driver-to-pickup route, keep only trip route
   * Called when driver confirms pickup
   */
  const hideDriverToPickupRoute = () => {
    console.log('🗺️ Hiding driver-to-pickup route')
    
    if (!map.value) return

    // Hide driver route layer
    if (map.value.getLayer(driverRouteLayerId)) {
      map.value.setLayoutProperty(driverRouteLayerId, 'visibility', 'none')
    }

    driverToPickupRoute.value = null
    routeMode.value = 'in-trip'
    
    // Fit map to show only trip route
    if (tripRoute.value && tripRoute.value.coordinates) {
      const bounds = tripRoute.value.coordinates.reduce((bounds, coord) => {
        return bounds.extend(coord)
      }, new mapboxgl.LngLatBounds(
        tripRoute.value.coordinates[0], 
        tripRoute.value.coordinates[0]
      ))
      
      map.value.fitBounds(bounds, {
        padding: 100,
        duration: 1000
      })
    }
  }

  /**
   * Clear all routes
   */
  const clearAllRoutes = () => {
    console.log('🗺️ Clearing all routes')
    
    if (!map.value) return

    // Clear trip route
    if (map.value.getSource(tripRouteSourceId)) {
      updateRoute(tripRouteSourceId, {
        type: 'LineString',
        coordinates: []
      })
    }

    // Clear driver route
    if (map.value.getSource(driverRouteSourceId)) {
      updateRoute(driverRouteSourceId, {
        type: 'LineString',
        coordinates: []
      })
    }

    tripRoute.value = null
    driverToPickupRoute.value = null
    isRoutesVisible.value = false
    routeMode.value = null
  }

  /**
   * Toggle route visibility (for clicking outside modal)
   */
  const toggleRouteVisibility = () => {
    if (!map.value) return

    const newVisibility = isRoutesVisible.value ? 'none' : 'visible'
    
    if (map.value.getLayer(tripRouteLayerId)) {
      map.value.setLayoutProperty(tripRouteLayerId, 'visibility', newVisibility)
    }
    
    if (map.value.getLayer(driverRouteLayerId) && routeMode.value === 'to-pickup') {
      map.value.setLayoutProperty(driverRouteLayerId, 'visibility', newVisibility)
    }
    
    isRoutesVisible.value = !isRoutesVisible.value
  }

  // Watch driver location for real-time route updates
  watch(driverLocation, () => {
    // Only update if we're in "to-pickup" mode
    if (routeMode.value === 'to-pickup' && tripRoute.value) {
      // Debounce updates to avoid too many API calls
      // Update every ~10 seconds or significant distance change
      // This would be implemented with a debounce timer
    }
  }, { deep: true })

  return {
    // State
    tripRoute,
    driverToPickupRoute,
    isRoutesVisible,
    routeMode,
    
    // Methods
    showTripRoutePreview,
    showDriverToPickupRoute,
    updateDriverToPickupRoute,
    hideDriverToPickupRoute,
    clearAllRoutes,
    toggleRouteVisibility
  }
}
