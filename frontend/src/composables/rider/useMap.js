/**
 * Map management composable
 * Handles Mapbox map initialization, markers, and geolocation
 */
import { ref, onMounted, onUnmounted } from 'vue'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

export function useMap() {
  // Configure Mapbox
  mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN || ''

  // Refs
  const mapContainer = ref(null)
  const map = ref(null)
  const userMarker = ref(null)
  const destinationMarker = ref(null)
  const routeLayer = ref(null)

  const userLocation = ref({
    lat: 36.8065, // Default: Tunis
    lng: 10.1815
  })

  /**
   * Initialize the Mapbox map
   */
  const initMap = () => {
    if (!mapContainer.value) {
      console.error('Map container not found')
      return
    }

    console.log('Initializing map...', mapboxgl.accessToken ? 'Token found' : 'NO TOKEN')

    try {
      map.value = new mapboxgl.Map({
        container: mapContainer.value,
        style: 'mapbox://styles/mapbox/dark-v11',
        center: [userLocation.value.lng, userLocation.value.lat],
        zoom: 13,
        pitch: 30,
        padding: { top: 0, bottom: 350, left: 0, right: 0 } // Account for bottom card
      })

      map.value.on('load', () => {
        console.log('Map loaded successfully')
        // Ensure map size is correct (useful when container was hidden before mount)
        try { 
          map.value.resize()
          // Apply padding after resize to ensure proper centering
          map.value.setPadding({ top: 0, bottom: 350, left: 0, right: 0 })
        } catch (e) { /* ignore */ }
        
        // Remove Mapbox attribution and logo
        setTimeout(() => {
          const container = mapContainer.value
          if (container) {
            // Remove all Mapbox attribution elements
            const attributions = container.querySelectorAll('.mapboxgl-ctrl-attrib, .mapboxgl-ctrl-logo, .mapboxgl-ctrl-bottom-left, .mapboxgl-ctrl-bottom-right, .mapboxgl-compact')
            attributions.forEach(el => el.remove())
            
            // Remove any anchor links to Mapbox
            const links = container.querySelectorAll('a[href*="mapbox"]')
            links.forEach(link => link.remove())
          }
        }, 100)
      })

      // Navigation controls removed - using custom controls instead

      map.value.on('error', (e) => {
        console.error('Map error:', e)
      })

      // Create user marker (green circle)
      const userEl = document.createElement('div')
      userEl.className = 'user-location-marker'
      userEl.innerHTML = `
        <div style="
          width: 20px;
          height: 20px;
          background: #22c55e;
          border: 3px solid white;
          border-radius: 50%;
          box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        "></div>
      `
      
      userMarker.value = new mapboxgl.Marker({ element: userEl })
        .setLngLat([userLocation.value.lng, userLocation.value.lat])
        .addTo(map.value)

    } catch (error) {
      console.error('Failed to initialize map:', error)
    }
  }

  /**
   * Reverse geocode coordinates to get precise location information
   * Priority: POI > Street Address > Neighborhood > Locality > District > City
   */
  const reverseGeocode = async (lng, lat) => {
    try {
      const accessToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN
      // Request with limit=1 for most relevant result and prioritize precise types
      const response = await fetch(
        `https://api.mapbox.com/geocoding/v5/mapbox.places/${lng},${lat}.json?access_token=${accessToken}&language=en&limit=1&types=poi,address,neighborhood,locality,place`
      )
      
      if (!response.ok) {
        throw new Error('Failed to reverse geocode')
      }
      
      const data = await response.json()
      console.log('🗺️ Geocoding result:', data.features?.[0])
      
      if (data.features && data.features.length > 0) {
        const feature = data.features[0]
        const placeType = feature.place_type[0]
        
        console.log('📍 Place type:', placeType, '| Text:', feature.text)
        
        // Extract components from context
        let city = null
        let neighborhood = null
        
        if (feature.context) {
          const placeContext = feature.context.find(c => c.id.startsWith('place.'))
          const neighborhoodContext = feature.context.find(c => c.id.startsWith('neighborhood.'))
          
          if (placeContext) city = placeContext.text
          if (neighborhoodContext) neighborhood = neighborhoodContext.text
        }
        
        // Build result based on place type priority
        let specificLocation = null
        let generalLocation = city
        
        if (placeType === 'poi') {
          // POI (supermarket, restaurant, landmark, etc.) - MOST SPECIFIC
          specificLocation = feature.text
          console.log('  🏪 POI found:', specificLocation)
        } else if (placeType === 'address') {
          // Street address with optional number
          const streetNumber = feature.address || null
          specificLocation = streetNumber ? `${streetNumber} ${feature.text}` : feature.text
          console.log('  🏠 Address found:', specificLocation)
        } else if (placeType === 'neighborhood') {
          // Neighborhood
          specificLocation = feature.text
          console.log('  🏘️ Neighborhood found:', specificLocation)
        } else if (placeType === 'locality' || placeType === 'place') {
          // Locality or city
          generalLocation = feature.text
          specificLocation = neighborhood // Use neighborhood if available
          console.log('  🌆 City/Locality found:', generalLocation)
        }
        
        // Format: "City, Specific Location" or just "City" or just "Specific Location"
        const parts = []
        if (generalLocation) parts.push(generalLocation)
        if (specificLocation && specificLocation !== generalLocation) parts.push(specificLocation)
        
        const result = parts.length > 0 ? parts.join(', ') : feature.place_name
        console.log('  ✅ Final:', result)
        return result
      }
      
      // No features found
      console.log('⚠️ No features found')
      return 'Location unavailable'
    } catch (error) {
      console.error('❌ Geocoding error:', error)
      return 'Location unavailable'
    }
  }

  /**
   * Get current user location
   */
  const getCurrentLocation = () => {
    if (!navigator.geolocation) {
      console.error('Geolocation is not supported')
      return
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude: lat, longitude: lng } = position.coords
        
        userLocation.value = { lat, lng }

        // Update map and marker
        if (map.value) {
          map.value.flyTo({
            center: [lng, lat],
            zoom: 16,
            pitch: 30,
            duration: 1200,
            padding: { top: 0, bottom: 350, left: 0, right: 0 } // Push center point up
          })

          if (userMarker.value) {
            userMarker.value.setLngLat([lng, lat])
          }
        }

        console.log('User location updated:', lat, lng)
      },
      (error) => {
        console.error('Geolocation error:', error)
      },
      {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0
      }
    )
  }

  /**
   * Center map on user location
   */
  const centerOnUserLocation = () => {
    if (map.value && userLocation.value) {
      map.value.flyTo({
        center: [userLocation.value.lng, userLocation.value.lat],
        zoom: 16,
        pitch: 30,
        duration: 800,
        padding: { top: 0, bottom: 350, left: 0, right: 0 } // Push center point up
      })
    }
  }

  /**
   * Create or update destination marker
   */
  const setDestinationMarker = (lng, lat) => {
    if (destinationMarker.value) {
      destinationMarker.value.setLngLat([lng, lat])
    } else {
      const el = document.createElement('div')
      el.className = 'destination-marker'
      el.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-red-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 0C7.31 0 3.5 3.81 3.5 8.5c0 5.25 8.5 15.5 8.5 15.5s8.5-10.25 8.5-15.5C20.5 3.81 16.69 0 12 0zm0 11.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
        </svg>
      `
      destinationMarker.value = new mapboxgl.Marker({ element: el, anchor: 'bottom' })
        .setLngLat([lng, lat])
        .addTo(map.value)
    }
  }

  /**
   * Remove destination marker
   */
  const removeDestinationMarker = () => {
    if (destinationMarker.value) {
      destinationMarker.value.remove()
      destinationMarker.value = null
    }
  }

  /**
   * Draw route on map from user location to destination
   */
  const drawRoute = async (destinationLng, destinationLat) => {
    console.log('🚗 drawRoute called with:', { destinationLng, destinationLat })
    console.log('📍 User location:', userLocation.value)
    console.log('🗺️ Map exists:', !!map.value)
    
    if (!map.value || !userLocation.value) {
      console.warn('⚠️ Cannot draw route: missing map or user location')
      return
    }

    try {
      // Remove existing route if any
      if (map.value.getLayer('route')) {
        map.value.removeLayer('route')
      }
      if (map.value.getSource('route')) {
        map.value.removeSource('route')
      }

      // Fetch route from Mapbox Directions API
      const start = `${userLocation.value.lng},${userLocation.value.lat}`
      const end = `${destinationLng},${destinationLat}`
      const url = `https://api.mapbox.com/directions/v5/mapbox/driving/${start};${end}?geometries=geojson&access_token=${mapboxgl.accessToken}`

      const response = await fetch(url)
      const data = await response.json()
      
      console.log('🛣️ Route data received:', data)

      if (data.routes && data.routes.length > 0) {
        const route = data.routes[0].geometry
        console.log('✅ Route geometry:', route)

        // Add route source
        map.value.addSource('route', {
          type: 'geojson',
          data: {
            type: 'Feature',
            properties: {},
            geometry: route
          }
        })

        // Add route layer
        map.value.addLayer({
          id: 'route',
          type: 'line',
          source: 'route',
          layout: {
            'line-join': 'round',
            'line-cap': 'round'
          },
          paint: {
            'line-color': '#FFD000',
            'line-width': 5,
            'line-opacity': 0.8
          }
        })

        // Fit map to show entire route
        const coordinates = route.coordinates
        const bounds = coordinates.reduce((bounds, coord) => {
          return bounds.extend(coord)
        }, new mapboxgl.LngLatBounds(coordinates[0], coordinates[0]))

        map.value.fitBounds(bounds, {
          padding: { top: 100, bottom: 380, left: 50, right: 50 }, // Extra bottom padding for card
          duration: 1000,
          // allow route to zoom in a bit to show more detail
          maxZoom: 16
        })
      }
    } catch (error) {
      console.error('Error drawing route:', error)
    }
  }

  /**
   * Clear route from map
   */
  const clearRoute = () => {
    if (!map.value) return

    if (map.value.getLayer('route')) {
      map.value.removeLayer('route')
    }
    if (map.value.getSource('route')) {
      map.value.removeSource('route')
    }
  }

  /**
   * Cleanup on unmount
   */
  onUnmounted(() => {
    if (map.value) {
      map.value.remove()
    }
  })

  return {
    // Refs
    mapContainer,
    map,
    userMarker,
    destinationMarker,
    userLocation,
    
    // Methods
    initMap,
    getCurrentLocation,
    centerOnUserLocation,
    setDestinationMarker,
    removeDestinationMarker,
    drawRoute,
    clearRoute,
    reverseGeocode
  }
}
