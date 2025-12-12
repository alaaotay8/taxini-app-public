import { ref } from 'vue'
import mapboxgl from 'mapbox-gl'

export function useDriverMap() {
  // Refs
  const mapContainer = ref(null)
  const map = ref(null)
  const driverMarker = ref(null)
  const pickupMarker = ref(null)
  const destinationMarker = ref(null)
  const routeLayer = ref(null)
  
  const driverLocation = ref({
    lat: 36.8065, // Default: Tunis
    lng: 10.1815
  })
  
  const gpsActive = ref(false)
  
  // Navigation state
  const isNavigating = ref(false)
  const navigationDestination = ref(null)
  const currentRouteDistance = ref(0)
  const remainingDistance = ref(0)
  let navigationInterval = null
  
  // Location tracking
  let locationWatchId = null

  // Initialize map
  const initMap = () => {
    if (!mapContainer.value) return

    mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN || ''

    map.value = new mapboxgl.Map({
      container: mapContainer.value,
      style: import.meta.env.VITE_MAPBOX_STYLE || 'mapbox://styles/mapbox/dark-v11',
      center: [driverLocation.value.lng, driverLocation.value.lat],
      zoom: 13,
      pitch: 30,
      attributionControl: false,
      padding: { top: 0, bottom: 350, left: 0, right: 0 } // Account for bottom card
    })

    // Navigation controls removed - using custom controls instead
    map.value.on('load', () => {
      try { 
        map.value.resize()
        // Apply padding after resize to ensure proper centering
        map.value.setPadding({ top: 0, bottom: 350, left: 0, right: 0 })
      } catch (e) { /* ignore */ }
    })

    // Add driver marker
    const el = document.createElement('div')
    el.innerHTML = '🚕'
    el.style.fontSize = '32px'
    el.style.cursor = 'pointer'

    driverMarker.value = new mapboxgl.Marker({
      element: el,
      anchor: 'bottom'
    })
      .setLngLat([driverLocation.value.lng, driverLocation.value.lat])
      .addTo(map.value)
  }

  // Get current location with continuous updates
  const getCurrentLocation = (currentTrip, approachDistance, distanceTraveled) => {
    if (navigator.geolocation) {
      locationWatchId = navigator.geolocation.watchPosition(
        (position) => {
          const { latitude, longitude } = position.coords
          driverLocation.value = { lat: latitude, lng: longitude }
          gpsActive.value = true
          
          // Update marker position
          if (driverMarker.value) {
            driverMarker.value.setLngLat([longitude, latitude])
          }
          
          // Don't auto-center map if viewing route preview or if there's an active trip
          // This prevents the map from jumping back to current location while viewing the route
          if (map.value && !currentTrip.value) {
            // Zoom slightly closer for more detail when user is centered
            const targetZoom = Math.max(map.value.getZoom(), 16)
            
            // Add padding to account for bottom card (center driver in visible top half)
            // The card takes up roughly bottom 40% of screen, so offset map center upward
            map.value.easeTo({
              center: [longitude, latitude],
              zoom: targetZoom,
              pitch: 30,
              duration: 800,
              padding: { top: 0, bottom: 350, left: 0, right: 0 } // Push center point up
            })
          }

          // Calculate approach distance if going to pickup
          if (currentTrip.value && currentTrip.value.status === 'accepted') {
            approachDistance.value = calculateDistance(
              latitude,
              longitude,
              currentTrip.value.pickup_lat,
              currentTrip.value.pickup_lng
            )
          }

          // Update distance traveled if trip in progress
          if (currentTrip.value && currentTrip.value.status === 'started') {
            if (!currentTrip.value.startLat) {
              // Store starting position
              currentTrip.value.startLat = latitude
              currentTrip.value.startLng = longitude
              currentTrip.value.lastLat = latitude
              currentTrip.value.lastLng = longitude
              console.log('🚀 Trip tracking started from:', latitude, longitude)
            } else {
              // Calculate distance since last update
              const lastLat = currentTrip.value.lastLat || latitude
              const lastLng = currentTrip.value.lastLng || longitude
              
              const segmentDistance = calculateDistance(
                lastLat,
                lastLng,
                latitude,
                longitude
              )
              
              // Only add if movement is significant (> 10 meters) to filter GPS noise
              if (segmentDistance > 0.01) {
                distanceTraveled.value += segmentDistance
                currentTrip.value.lastLat = latitude
                currentTrip.value.lastLng = longitude
                console.log(`📏 Distance updated: +${segmentDistance.toFixed(3)} km, Total: ${distanceTraveled.value.toFixed(2)} km`)
              }
            }
          }
        },
        (error) => {
          console.error('Geolocation error:', error)
          gpsActive.value = false
        },
        {
          enableHighAccuracy: true,
          maximumAge: 3000,
          timeout: 5000
        }
      )
    }
  }

  // Calculate distance between two points (Haversine formula)
  const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371 // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180
    const dLon = (lon2 - lon1) * Math.PI / 180
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2)
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
    return R * c
  }

  // Add pickup marker
  const addPickupMarker = (lat, lng) => {
    removePickupMarker()
    
    const el = document.createElement('div')
    el.innerHTML = '📍'
    el.style.fontSize = '32px'

    pickupMarker.value = new mapboxgl.Marker({
      element: el,
      anchor: 'bottom'
    })
      .setLngLat([lng, lat])
      .addTo(map.value)
  }

  // Add destination marker
  const addDestinationMarker = (lat, lng) => {
    removeDestinationMarker()
    
    const el = document.createElement('div')
    el.innerHTML = '🏁'
    el.style.fontSize = '32px'

    destinationMarker.value = new mapboxgl.Marker({
      element: el,
      anchor: 'bottom'
    })
      .setLngLat([lng, lat])
      .addTo(map.value)
  }

  // Remove markers
  const removePickupMarker = () => {
    if (pickupMarker.value) {
      pickupMarker.value.remove()
      pickupMarker.value = null
    }
  }

  const removeDestinationMarker = () => {
    if (destinationMarker.value) {
      destinationMarker.value.remove()
      destinationMarker.value = null
    }
  }

  // Fit map to show all markers
  const fitMapToBounds = () => {
    if (!map.value) return

    const bounds = new mapboxgl.LngLatBounds()
    
    if (driverMarker.value) {
      bounds.extend(driverMarker.value.getLngLat())
    }
    if (pickupMarker.value) {
      bounds.extend(pickupMarker.value.getLngLat())
    }
    if (destinationMarker.value) {
      bounds.extend(destinationMarker.value.getLngLat())
    }

    map.value.fitBounds(bounds, {
      padding: { top: 80, bottom: 380, left: 80, right: 80 }, // Extra bottom padding for card
      duration: 1000,
      maxZoom: 16
    })
  }

  // Draw route on map
  const drawRoute = async (pickup, destination, isNavigation = false) => {
    if (!map.value) return

    try {
      const query = await fetch(
        `https://api.mapbox.com/directions/v5/mapbox/driving/${pickup.lng},${pickup.lat};${destination.lng},${destination.lat}?geometries=geojson&steps=true&overview=full&access_token=${mapboxgl.accessToken}`
      )
      const json = await query.json()
      
      if (!json.routes || json.routes.length === 0) {
        console.error('No route found')
        return
      }
      
      const data = json.routes[0]
      const route = data.geometry.coordinates
      
      // Store distance in kilometers
      const distanceInMeters = data.distance
      currentRouteDistance.value = (distanceInMeters / 1000).toFixed(2)
      remainingDistance.value = currentRouteDistance.value
      
      console.log(`🗺️ Route drawn: ${currentRouteDistance.value} km, Duration: ${Math.round(data.duration / 60)} min`)

      const geojson = {
        type: 'Feature',
        properties: {
          distance: data.distance,
          duration: data.duration
        },
        geometry: {
          type: 'LineString',
          coordinates: route
        }
      }

      if (map.value.getSource('route')) {
        map.value.getSource('route').setData(geojson)
      } else {
        map.value.addLayer({
          id: 'route',
          type: 'line',
          source: {
            type: 'geojson',
            data: geojson
          },
          layout: {
            'line-join': 'round',
            'line-cap': 'round'
          },
          paint: {
            'line-color': isNavigation ? '#3B82F6' : '#FFD000',
            'line-width': 6,
            'line-opacity': 0.85
          }
        })
      }
      
      // If this is navigation mode, update route color
      if (isNavigation && map.value.getLayer('route')) {
        map.value.setPaintProperty('route', 'line-color', '#3B82F6')
        map.value.setPaintProperty('route', 'line-width', 6)
      }
      
      return {
        distance: currentRouteDistance.value,
        duration: data.duration
      }
    } catch (error) {
      console.error('Error drawing route:', error)
      return null
    }
  }

  // Start navigation with real-time tracking
  const startNavigation = async (destination) => {
    if (!map.value || !driverLocation.value) {
      console.error('Map or driver location not available')
      return
    }
    
    console.log('🧭 Starting navigation to:', destination)
    isNavigating.value = true
    navigationDestination.value = destination
    
    // Draw initial route
    await drawRoute(driverLocation.value, destination, true)
    
    // Update route every 10 seconds while navigating
    if (navigationInterval) {
      clearInterval(navigationInterval)
    }
    
    navigationInterval = setInterval(async () => {
      if (!isNavigating.value || !driverLocation.value || !navigationDestination.value) {
        stopNavigation()
        return
      }
      
      // Calculate remaining distance
      const distance = calculateDistance(
        driverLocation.value.lat,
        driverLocation.value.lng,
        navigationDestination.value.lat,
        navigationDestination.value.lng
      )
      
      remainingDistance.value = distance.toFixed(2)
      
      // Redraw route with updated position
      await drawRoute(driverLocation.value, navigationDestination.value, true)
      
      console.log(`📍 Navigation update: ${remainingDistance.value} km remaining`)
      
      // Stop navigation if very close (within 50 meters)
      if (distance < 0.05) {
        console.log('🎯 Arrived at destination!')
        stopNavigation()
      }
    }, 10000) // Update every 10 seconds
  }
  
  // Stop navigation
  const stopNavigation = () => {
    console.log('🛑 Stopping navigation')
    isNavigating.value = false
    navigationDestination.value = null
    
    if (navigationInterval) {
      clearInterval(navigationInterval)
      navigationInterval = null
    }
  }
  
  // Clear route from map
  const clearRoute = () => {
    if (map.value && map.value.getLayer('route')) {
      map.value.removeLayer('route')
      map.value.removeSource('route')
    }
    stopNavigation()
  }

  // Stop location tracking
  const stopLocationTracking = () => {
    if (locationWatchId) {
      navigator.geolocation.clearWatch(locationWatchId)
      locationWatchId = null
      gpsActive.value = false
    }
  }

  // Recenter map to driver's current location
  const recenterToDriver = () => {
    if (map.value && driverLocation.value) {
      map.value.easeTo({
        center: [driverLocation.value.lng, driverLocation.value.lat],
        zoom: 16,
        pitch: 30,
        duration: 800,
        padding: { top: 0, bottom: 350, left: 0, right: 0 }
      })
    }
  }

  return {
    // Refs
    mapContainer,
    map,
    driverMarker,
    pickupMarker,
    destinationMarker,
    routeLayer,
    driverLocation,
    gpsActive,
    isNavigating,
    navigationDestination,
    currentRouteDistance,
    remainingDistance,
    
    // Methods
    initMap,
    getCurrentLocation,
    calculateDistance,
    addPickupMarker,
    addDestinationMarker,
    removePickupMarker,
    removeDestinationMarker,
    fitMapToBounds,
    drawRoute,
    startNavigation,
    stopNavigation,
    clearRoute,
    stopLocationTracking,
    recenterToDriver
  }
}
