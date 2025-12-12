/**
 * Location Formatting Service
 * Provides consistent location formatting across the entire application
 * 
 * Format Priority:
 * 1. POI: "City, Carrefour" or "City, Coffee Shop XYZ"
 * 2. Address: "City, 123 Main Street" or "City, Avenue Habib Bourguiba"
 * 3. Neighborhood: "City, Medina" or "City, Downtown"
 * 4. City only: "Tunis" (when no more specific data available)
 */

const MAPBOX_ACCESS_TOKEN = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN

/**
 * Reverse geocode coordinates to get precise, formatted location
 * @param {number} lng - Longitude
 * @param {number} lat - Latitude
 * @param {Object} options - Formatting options
 * @param {boolean} options.includeCity - Include city in result (default: true)
 * @param {boolean} options.shortFormat - Use shortest format possible (default: false)
 * @returns {Promise<string>} Formatted location string
 */
export async function formatLocation(lng, lat, options = {}) {
  const {
    includeCity = true,
    shortFormat = false
  } = options

  try {
    // Validate coordinates
    if (!lng || !lat || isNaN(lng) || isNaN(lat)) {
      console.warn('⚠️ Invalid coordinates:', lng, lat)
      return 'Location unavailable'
    }

    // Validate coordinate ranges
    if (lat < -90 || lat > 90) {
      console.warn('⚠️ Invalid latitude (must be -90 to 90):', lat)
      return `Location (${lat}, ${lng})`
    }
    
    if (lng < -180 || lng > 180) {
      console.warn('⚠️ Invalid longitude (must be -180 to 180):', lng)
      return `Location (${lat}, ${lng})`
    }

    // Mapbox reverse geocoding: For coordinates → address conversion, limit causes 422 errors
    // Remove limit parameter to get all available features without type restrictions
    const url = `https://api.mapbox.com/geocoding/v5/mapbox.places/${lng},${lat}.json?` +
      `access_token=${MAPBOX_ACCESS_TOKEN}&` +
      `language=en`
    
    console.log('🌍 Geocoding request:', { lng, lat })
    
    const response = await fetch(url)
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('❌ Mapbox API error:', response.status, errorText)
      throw new Error(`Geocoding API error: ${response.status}`)
    }
    
    const data = await response.json()
    
    if (!data.features || data.features.length === 0) {
      console.warn('⚠️ No features found for coordinates')
      return `Location unavailable (${lat.toFixed(4)}, ${lng.toFixed(4)})`
    }

    console.log('🔍 Mapbox features received:', data.features.map(f => ({ 
      type: f.place_type, 
      text: f.text, 
      place_name: f.place_name 
    })))

    return parseLocationFeatures(data.features, { includeCity, shortFormat }, lng, lat)
    
  } catch (error) {
    console.error('❌ Location formatting error:', error)
    // Return coordinates as fallback
    if (lat && lng) {
      return `Location (${lat.toFixed(4)}, ${lng.toFixed(4)})`
    }
    return 'Location unavailable'
  }
}

/**
 * Parse multiple Mapbox features and combine them for detailed address
 * 
 * Format Structure: "Street, near Landmark, Neighborhood, City (lat, lng)"
 * 
 * Order of Information:
 * 1. Street address - "42 Avenue Habib Bourguiba" (if available)
 * 2. POI/Landmark - "near Carrefour" (if available)
 * 3. Neighborhood/District - "Medina" (if available)
 * 4. Locality - Only if different from city (if available)
 * 5. City/Region - "Monastir" (always included if available)
 * 6. Coordinates - "(35.7773, 10.8053)" (always included)
 * 
 * Examples:
 * - Full: "42 Avenue Habib Bourguiba, near Carrefour, Medina, Monastir (35.7773, 10.8053)"
 * - Street + City: "Avenue de la République, Tunis (36.8065, 10.1815)"
 * - POI + City: "near Monoprix, Sousse (35.8245, 10.6065)"
 * - City only: "Monastir (35.7773, 10.8053)"
 * 
 * @param {Array} features - Array of Mapbox geocoding features
 * @param {Object} options - Formatting options
 * @param {number} lng - Longitude for coordinate display
 * @param {number} lat - Latitude for coordinate display
 * @returns {string} Formatted location string
 */
function parseLocationFeatures(features, options, lng, lat) {
  // Parse multiple Mapbox features to build comprehensive address
  
  // Extract information from all features
  let street = null
  let streetNumber = null
  let poi = null
  let neighborhood = null
  let district = null
  let locality = null
  let city = null
  let region = null
  
  // First pass: extract from main features (prioritize most specific data)
  features.forEach(feature => {
    const placeType = feature.place_type[0]
    
    if (placeType === 'address' && !street) {
      street = feature.text
      streetNumber = feature.address || null
    } else if (placeType === 'poi' && !poi) {
      poi = feature.text
    } else if (placeType === 'neighborhood' && !neighborhood) {
      neighborhood = feature.text
    } else if (placeType === 'district' && !district) {
      district = feature.text
    } else if (placeType === 'locality' && !locality) {
      locality = feature.text
    } else if (placeType === 'place' && !city) {
      city = feature.text
    } else if (placeType === 'region' && !region) {
      region = feature.text
    }
  })
  
  // Second pass: extract from context of ALL features for better coverage
  features.forEach(feature => {
    if (feature.context) {
      feature.context.forEach(c => {
        if (c.id.startsWith('place.') && !city) city = c.text
        if (c.id.startsWith('neighborhood.') && !neighborhood) neighborhood = c.text
        if (c.id.startsWith('region.') && !region) region = c.text
        if (c.id.startsWith('district.') && !district) district = c.text
        if (c.id.startsWith('locality.') && !locality) locality = c.text
        if (c.id.startsWith('address.') && !street) {
          street = c.text
        }
        if (c.id.startsWith('poi.') && !poi) {
          poi = c.text
        }
      })
    }
  })
  
  // Build detailed parts array - prioritize specific over general
  const parts = []
  
  // 1. Street address (most specific) - always include if available
  if (street) {
    const fullStreet = streetNumber ? `${streetNumber} ${street}` : street
    // Don't add if it's just a number (like "50")
    if (!/^\d+$/.test(fullStreet)) {
      parts.push(fullStreet)
    }
  }
  
  // 2. POI/Landmark (nearby reference) - add if available
  if (poi && poi !== street) {
    parts.push(poi)
  }
  
  // 3. Neighborhood or District (for local context) - add if different from street
  if (neighborhood && neighborhood !== street && neighborhood !== poi && neighborhood !== city) {
    parts.push(neighborhood)
  } else if (district && district !== street && district !== poi && district !== city) {
    parts.push(district)
  }
  
  // 4. Locality (if different from city and other parts)
  if (locality && locality !== city && locality !== neighborhood && locality !== district) {
    parts.push(locality)
  }
  
  // 5. City - always include for context (avoid duplicates)
  const finalCity = city || region
  if (finalCity && !parts.includes(finalCity)) {
    parts.push(finalCity)
  }
  
  // 6. Build final string
  let result
  if (parts.length > 1) {
    // We have detailed info beyond just city
    result = parts.join(', ')
  } else if (parts.length === 1 && parts[0] !== finalCity) {
    // We have one specific part (not just city), keep it
    result = parts.join(', ')
  } else {
    // Only have city or nothing - use Mapbox's place_name which has more detail
    const placeName = features[0].place_name || features[0].text
    // Remove the country from the end (usually after the last comma)
    const partsFromName = placeName.split(',').map(p => p.trim())
    // Keep all but the last part (country) and remove duplicates
    if (partsFromName.length > 1) {
      const uniqueParts = [...new Set(partsFromName.slice(0, -1))]
      result = uniqueParts.join(', ')
    } else {
      result = placeName
    }
  }
  
  console.log('📍 Formatted location:', { 
    extracted: { street, poi, neighborhood, district, locality, city, region },
    parts, 
    result,
    rawPlaceName: features[0].place_name
  })
  
  // 7. Always append coordinates for precision
  const coords = `(${lat.toFixed(4)}, ${lng.toFixed(4)})`
  result = `${result} ${coords}`
  
  return result
}

/**
 * Format location from trip data (pickup or destination)
 * @param {Object} trip - Trip object with latitude/longitude
 * @param {string} type - 'pickup' or 'destination'
 * @param {Object} options - Formatting options
 * @returns {Promise<string>} Formatted location string
 */
export async function formatTripLocation(trip, type = 'pickup', options = {}) {
  if (!trip) {
    return type === 'pickup' ? 'Pickup location' : 'Destination'
  }
  
  // Use coordinates to always get consistent detailed formatting
  const lngKey = type === 'pickup' ? 'pickup_longitude' : 'destination_longitude'
  const latKey = type === 'pickup' ? 'pickup_latitude' : 'destination_latitude'
  
  const lng = trip[lngKey]
  const lat = trip[latKey]
  
  if (!lng || !lat) {
    return type === 'pickup' ? 'Pickup location' : 'Destination'
  }
  
  console.log(`📍 Formatting ${type} location from coordinates`)
  return formatLocation(lng, lat, options)
}

/**
 * Format current user location
 * @param {Object} location - Location object with lat/lng
 * @param {Object} options - Formatting options
 * @returns {Promise<string>} Formatted location string
 */
export async function formatCurrentLocation(location, options = {}) {
  if (!location || !location.lat || !location.lng) {
    return 'Current location'
  }
  
  return formatLocation(location.lng, location.lat, options)
}

/**
 * Batch format multiple locations (useful for driver lists, etc.)
 * @param {Array} locations - Array of {lng, lat} objects
 * @param {Object} options - Formatting options
 * @returns {Promise<Array<string>>} Array of formatted location strings
 */
export async function formatLocations(locations, options = {}) {
  if (!Array.isArray(locations) || locations.length === 0) {
    return []
  }
  
  const promises = locations.map(loc => {
    if (loc && loc.lng && loc.lat) {
      return formatLocation(loc.lng, loc.lat, options)
    }
    return Promise.resolve('Location unavailable')
  })
  
  return Promise.all(promises)
}

/**
 * Check if a string looks like raw coordinates
 * @param {string} str - String to check
 * @returns {boolean} True if string contains coordinate pattern
 */
export function looksLikeCoordinates(str) {
  if (!str || typeof str !== 'string') return false
  return /\d+\.\d+.*\d+\.\d+/.test(str)
}

/**
 * Clean up a location string (remove coordinates if present)
 * @param {string} str - String to clean
 * @returns {string} Cleaned string
 */
export function cleanLocationString(str) {
  if (!str || typeof str !== 'string') return str
  
  // Remove coordinate patterns like "(35.7773, 10.8053)"
  const cleaned = str.replace(/\(?\d+\.\d+,?\s*\d+\.\d+\)?/g, '').trim()
  
  // Remove trailing commas
  return cleaned.replace(/,\s*$/, '').trim()
}

export default {
  formatLocation,
  formatTripLocation,
  formatCurrentLocation,
  formatLocations,
  looksLikeCoordinates,
  cleanLocationString
}
