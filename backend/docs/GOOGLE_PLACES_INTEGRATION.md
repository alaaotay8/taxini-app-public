# Google Places API Integration for Tunisia Addresses

## Overview
This guide helps you integrate Google Places Autocomplete API to provide real Tunisia address suggestions and location permissions.

## Step 1: Get Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable these APIs:
   - **Maps JavaScript API**
   - **Places API**
   - **Geocoding API**
   - **Geolocation API**
4. Go to **Credentials** → **Create Credentials** → **API Key**
5. Restrict your API key:
   - **Application restrictions**: HTTP referrers
   - **API restrictions**: Select only the 4 APIs above
   - **Add referrers**:
     - `http://localhost:*`
     - `https://yourdomain.com/*`

## Step 2: Install Required Package

```bash
cd Taxini-Frontend
npm install @googlemaps/js-api-loader
```

## Step 3: Add API Key to Environment

Create/update `.env.local`:
```env
VITE_GOOGLE_MAPS_API_KEY=your_api_key_here
VITE_GOOGLE_MAPS_TUNISIA_BOUNDS=32.0,7.5,38.0,12.0
```

## Step 4: Create Google Places Service

Create `src/services/googlePlaces.js`:

```javascript
import { Loader } from '@googlemaps/js-api-loader'

const loader = new Loader({
  apiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
  version: 'weekly',
  libraries: ['places']
})

let placesService = null
let autocompleteService = null

// Initialize Google Places services
export async function initGooglePlaces() {
  try {
    await loader.load()
    placesService = new google.maps.places.PlacesService(document.createElement('div'))
    autocompleteService = new google.maps.places.AutocompleteService()
    console.log('✅ Google Places initialized')
    return true
  } catch (error) {
    console.error('❌ Failed to load Google Places:', error)
    return false
  }
}

// Search for Tunisia addresses with autocomplete
export async function searchTunisiaAddresses(input) {
  if (!autocompleteService) {
    await initGooglePlaces()
  }

  if (!input || input.length < 3) {
    return []
  }

  return new Promise((resolve, reject) => {
    const request = {
      input: input,
      componentRestrictions: { country: 'tn' }, // Restrict to Tunisia
      types: ['geocode', 'establishment'], // Addresses and places
      language: 'fr' // French for Tunisia (or 'ar' for Arabic)
    }

    autocompleteService.getPlacePredictions(request, (predictions, status) => {
      if (status === google.maps.places.PlacesServiceStatus.OK) {
        const results = predictions.map(prediction => ({
          placeId: prediction.place_id,
          description: prediction.description,
          mainText: prediction.structured_formatting.main_text,
          secondaryText: prediction.structured_formatting.secondary_text
        }))
        resolve(results)
      } else if (status === google.maps.places.PlacesServiceStatus.ZERO_RESULTS) {
        resolve([])
      } else {
        reject(new Error(`Places API error: ${status}`))
      }
    })
  })
}

// Get detailed place info (coordinates) from place ID
export async function getPlaceDetails(placeId) {
  if (!placesService) {
    await initGooglePlaces()
  }

  return new Promise((resolve, reject) => {
    const request = {
      placeId: placeId,
      fields: ['name', 'formatted_address', 'geometry', 'place_id']
    }

    placesService.getDetails(request, (place, status) => {
      if (status === google.maps.places.PlacesServiceStatus.OK) {
        resolve({
          placeId: place.place_id,
          name: place.name,
          address: place.formatted_address,
          coordinates: {
            lat: place.geometry.location.lat(),
            lng: place.geometry.location.lng()
          }
        })
      } else {
        reject(new Error(`Place details error: ${status}`))
      }
    })
  })
}

// Request user's current location with permissions
export async function requestUserLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation not supported by browser'))
      return
    }

    // Show loading indicator
    console.log('📍 Requesting location permission...')

    const options = {
      enableHighAccuracy: true, // Use GPS if available
      timeout: 10000, // 10 seconds
      maximumAge: 0 // Don't use cached location
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const location = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
          accuracy: position.coords.accuracy
        }
        console.log('✅ Location obtained:', location)
        resolve(location)
      },
      (error) => {
        console.error('❌ Location error:', error.message)
        let errorMessage = 'Failed to get location'
        
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = 'Location permission denied. Please enable location access in your browser settings.'
            break
          case error.POSITION_UNAVAILABLE:
            errorMessage = 'Location information unavailable. Please check your GPS/internet connection.'
            break
          case error.TIMEOUT:
            errorMessage = 'Location request timed out. Please try again.'
            break
        }
        
        reject(new Error(errorMessage))
      },
      options
    )
  })
}

// Reverse geocode coordinates to address
export async function reverseGeocode(lat, lng) {
  const geocoder = new google.maps.Geocoder()
  
  return new Promise((resolve, reject) => {
    geocoder.geocode(
      { location: { lat, lng } },
      (results, status) => {
        if (status === 'OK' && results[0]) {
          resolve({
            formatted_address: results[0].formatted_address,
            place_id: results[0].place_id,
            coordinates: { lat, lng }
          })
        } else {
          reject(new Error(`Geocoding failed: ${status}`))
        }
      }
    )
  })
}
```

## Step 5: Update Rider Dashboard to Use Google Places

Update `src/views/rider/RiderDashboard.vue`:

```javascript
// Add import at top
import { searchTunisiaAddresses, getPlaceDetails, requestUserLocation, reverseGeocode } from '@/services/googlePlaces'

// In your onMounted hook:
onMounted(async () => {
  try {
    // Request location permission
    const location = await requestUserLocation()
    userLocation.value = location
    
    // Get address from coordinates
    const addressInfo = await reverseGeocode(location.lat, location.lng)
    pickupLocation.value = addressInfo.formatted_address
    
    // Initialize map with user location
    initializeMap()
    
    // Fetch nearby drivers
    fetchNearbyDrivers(location.lat, location.lng)
  } catch (error) {
    console.error('Location setup failed:', error)
    // Show error to user
    showLocationError(error.message)
  }
})

// Update destination search to use Google Places
const searchDestinations = async (query) => {
  if (!query || query.length < 3) {
    destinationSuggestions.value = []
    return
  }

  try {
    const results = await searchTunisiaAddresses(query)
    destinationSuggestions.value = results
    showDestinationSuggestions.value = true
  } catch (error) {
    console.error('Search failed:', error)
  }
}

// When user selects a destination
const selectDestinationFromGoogle = async (place) => {
  try {
    const details = await getPlaceDetails(place.placeId)
    destination.value = details.address
    tempDestinationCoords.value = details.coordinates
    showDestinationConfirmation.value = true
    showDestinationSuggestions.value = false
  } catch (error) {
    console.error('Failed to get place details:', error)
  }
}
```

## Step 6: Alternative - Mapbox Geocoding (Cheaper Option)

If Google is too expensive, use Mapbox:

### Install Mapbox SDK:
```bash
npm install @mapbox/mapbox-sdk
```

### Create `src/services/mapboxGeocoding.js`:
```javascript
import mbxGeocoding from '@mapbox/mapbox-sdk/services/geocoding'

const geocodingClient = mbxGeocoding({
  accessToken: import.meta.env.VITE_MAPBOX_ACCESS_TOKEN
})

export async function searchTunisiaAddresses(query) {
  try {
    const response = await geocodingClient
      .forwardGeocode({
        query: query,
        countries: ['TN'], // Tunisia
        language: ['fr'], // French
        limit: 5,
        types: ['place', 'address', 'poi']
      })
      .send()

    return response.body.features.map(feature => ({
      id: feature.id,
      name: feature.place_name,
      coordinates: {
        lng: feature.center[0],
        lat: feature.center[1]
      }
    }))
  } catch (error) {
    console.error('Mapbox geocoding error:', error)
    return []
  }
}

export async function reverseGeocode(lat, lng) {
  try {
    const response = await geocodingClient
      .reverseGeocode({
        query: [lng, lat],
        countries: ['TN'],
        limit: 1
      })
      .send()

    if (response.body.features.length > 0) {
      return {
        formatted_address: response.body.features[0].place_name,
        coordinates: { lat, lng }
      }
    }
    return null
  } catch (error) {
    console.error('Reverse geocoding error:', error)
    return null
  }
}
```

## Pricing Comparison

### Google Maps Platform (Monthly Free Tier)
- Autocomplete: $0/1000 requests (up to $200 credit)
- Geocoding: $5/1000 requests
- Maps: $7/1000 loads
- **Free tier**: $200/month credit

### Mapbox
- Autocomplete: FREE up to 100,000 requests/month
- Geocoding: FREE up to 100,000 requests/month
- Maps: FREE up to 50,000 loads/month
- **Cheaper for small/medium apps**

## Recommendation

🎯 **Start with Mapbox** (free tier is generous)
- Easy to integrate
- Better free tier
- Good Tunisia coverage
- Then upgrade to Google if needed

## Next Steps

1. ✅ Run the new SQL script with locations
2. ✅ Choose Google or Mapbox
3. ✅ Install packages
4. ✅ Add API key to .env
5. ✅ Integrate autocomplete in frontend
6. ✅ Test with real Tunisia addresses!
