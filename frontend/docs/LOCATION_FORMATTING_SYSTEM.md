# Location Formatting System

## Overview
Centralized location formatting service for consistent address display across the entire Taxini application.

## Created: December 10, 2025

---

## Service Location
`/src/services/locationFormatter.js`

## Format Priority

The system follows this hierarchy to provide the most specific location information:

1. **🏪 POI (Point of Interest)** - Most Specific
   - Supermarkets, restaurants, landmarks, shops
   - Example: "Tunis, Carrefour"

2. **🏠 Street Address** - Very Specific
   - Exact street name with optional house number
   - Example: "Sousse, 42 Avenue Hédi Chaker"

3. **🏘️ Neighborhood** - Moderately Specific
   - Named neighborhood or district within a city
   - Example: "Tunis, Medina"

4. **🌆 City/Locality** - Least Specific
   - City or town name
   - Example: "Monastir"

---

## API Reference

### `formatLocation(lng, lat, options)`
Core formatting function for any coordinates.

**Parameters:**
- `lng` (number): Longitude
- `lat` (number): Latitude
- `options` (object):
  - `includeCity` (boolean, default: true): Include city in result
  - `shortFormat` (boolean, default: false): Use shortest format possible

**Returns:** `Promise<string>` - Formatted location string

**Example:**
```javascript
import { formatLocation } from '@/services/locationFormatter'

// Full format: "Tunis, Carrefour"
const address = await formatLocation(10.1815, 36.8065)

// Short format: "Carrefour"
const shortAddress = await formatLocation(10.1815, 36.8065, { shortFormat: true })

// No city: "Carrefour"
const noCity = await formatLocation(10.1815, 36.8065, { includeCity: false })
```

---

### `formatTripLocation(trip, type, options)`
Format pickup or destination from trip data.

**Parameters:**
- `trip` (object): Trip object with latitude/longitude fields
- `type` (string): 'pickup' or 'destination'
- `options` (object): Same as formatLocation options

**Returns:** `Promise<string>` - Formatted location string

**Example:**
```javascript
import { formatTripLocation } from '@/services/locationFormatter'

// Format pickup
const pickup = await formatTripLocation(activeTrip, 'pickup')

// Format destination
const destination = await formatTripLocation(activeTrip, 'destination')
```

---

### `formatCurrentLocation(location, options)`
Format user's current location.

**Parameters:**
- `location` (object): Location object with `lat` and `lng`
- `options` (object): Same as formatLocation options

**Returns:** `Promise<string>` - Formatted location string

**Example:**
```javascript
import { formatCurrentLocation } from '@/services/locationFormatter'

const currentAddress = await formatCurrentLocation(userLocation)
// Returns: "Tunis, Avenue Habib Bourguiba"
```

---

### `formatLocations(locations, options)`
Batch format multiple locations (useful for driver lists).

**Parameters:**
- `locations` (array): Array of objects with `lng` and `lat`
- `options` (object): Same as formatLocation options

**Returns:** `Promise<Array<string>>` - Array of formatted location strings

**Example:**
```javascript
import { formatLocations } from '@/services/locationFormatter'

const driverLocations = [
  { lng: 10.1815, lat: 36.8065 },
  { lng: 10.6065, lat: 35.8245 }
]

const addresses = await formatLocations(driverLocations)
// Returns: ["Tunis, Downtown", "Sousse, Marina"]
```

---

### `looksLikeCoordinates(str)`
Check if a string contains raw coordinate patterns.

**Parameters:**
- `str` (string): String to check

**Returns:** `boolean` - True if string contains coordinates

**Example:**
```javascript
import { looksLikeCoordinates } from '@/services/locationFormatter'

looksLikeCoordinates("(35.7773, 10.8053)") // true
looksLikeCoordinates("Tunis, Carrefour") // false
```

---

### `cleanLocationString(str)`
Remove coordinate patterns from a string.

**Parameters:**
- `str` (string): String to clean

**Returns:** `string` - Cleaned string

**Example:**
```javascript
import { cleanLocationString } from '@/services/locationFormatter'

const cleaned = cleanLocationString("Tunis (35.7773, 10.8053)")
// Returns: "Tunis"
```

---

## Integration

### RiderDashboard.vue
The service is integrated in these key functions:

1. **updateFormattedAddresses()** - Updates pickup and destination displays
2. **updatePickupLocationAddress()** - Updates current location in search view
3. **confirmDriverSelection()** - Formats addresses before trip creation

**Usage:**
```javascript
// Import at top
import { formatTripLocation, formatCurrentLocation } from '@/services/locationFormatter'

// Format trip locations
const pickupAddress = await formatTripLocation(activeTrip.value, 'pickup')
const destinationAddress = await formatTripLocation(activeTrip.value, 'destination')

// Format current location
const currentAddress = await formatCurrentLocation(userLocation.value)
```

---

## Mapbox API Configuration

The service uses Mapbox Geocoding API v5:

**Endpoint:**
```
https://api.mapbox.com/geocoding/v5/mapbox.places/{lng},{lat}.json
```

**Parameters:**
- `access_token`: From environment variable `VITE_MAPBOX_ACCESS_TOKEN`
- `language`: `en` (English)
- `limit`: `1` (most relevant result only)
- `types`: `poi,address,neighborhood,locality,place` (ordered by priority)

**Why limit=1?**
- Faster response
- Mapbox returns the most relevant result first
- Reduces API data transfer
- More consistent results

---

## Format Examples

### POI (Highest Priority)
```javascript
// Input: Coordinates near Carrefour supermarket
await formatLocation(10.1815, 36.8065)
// Output: "Tunis, Carrefour"

// Short format
await formatLocation(10.1815, 36.8065, { shortFormat: true })
// Output: "Carrefour"
```

### Street Address
```javascript
// Input: Coordinates on Avenue Habib Bourguiba
await formatLocation(10.1815, 36.8065)
// Output: "Tunis, Avenue Habib Bourguiba"

// With house number
// Output: "Tunis, 42 Avenue Habib Bourguiba"
```

### Neighborhood
```javascript
// Input: Coordinates in Medina district
await formatLocation(10.1815, 36.8065)
// Output: "Tunis, Medina"
```

### City Only
```javascript
// Input: Coordinates with no specific location data
await formatLocation(10.1815, 36.8065)
// Output: "Tunis"
```

---

## Error Handling

The service handles these error cases:

1. **Invalid Coordinates**
   - Returns: `"Location unavailable"`
   - Console warning logged

2. **API Error**
   - Returns: `"Location unavailable"`
   - Error logged to console

3. **No Features Found**
   - Returns: `"Location unavailable"`
   - Warning logged to console

4. **Network Error**
   - Returns: `"Location unavailable"`
   - Error logged to console

---

## Console Logging

The service provides detailed console logs for debugging:

```
📍 Parsing feature: { type: 'poi', text: 'Carrefour', ... }
  🏪 POI: Carrefour
  ✅ Full format: Tunis, Carrefour
```

**Log Icons:**
- 📍 Feature parsing
- 🏪 POI found
- 🏠 Address found
- 🏘️ Neighborhood found
- 🌆 City/Locality found
- ✅ Final result
- ⚠️ Warning
- ❌ Error

---

## Benefits

### 1. Consistency
- All locations formatted the same way across the app
- Single source of truth for location formatting logic

### 2. Maintainability
- Centralized code - one place to update
- Easy to modify format rules
- Clear separation of concerns

### 3. Performance
- Optimized API calls (limit=1)
- Batch operations available
- Reduced data transfer

### 4. User Experience
- Most specific location shown first
- No raw coordinates displayed
- Clean, readable addresses
- Faster loading with single result

### 5. Developer Experience
- Simple API - import and use
- Comprehensive documentation
- Detailed logging
- TypeScript-ready

---

## Future Enhancements

### Possible Additions:
1. **Caching** - Store geocoded results to reduce API calls
2. **Localization** - Support Arabic and French
3. **Custom Formats** - Allow format templates
4. **Distance Indicators** - "Near Carrefour" style
5. **Offline Support** - Fallback when no network

---

## Testing

To test the service:

1. **Open Browser Console**
2. **Navigate to Rider Dashboard**
3. **Allow Location Access**
4. **Check Console Logs:**
   ```
   🔄 Updating formatted addresses with locationFormatter...
   📍 Parsing feature: ...
   ✅ Pickup formatted: Tunis, Avenue Habib Bourguiba
   ```

5. **Verify Display:**
   - Search view shows formatted pickup
   - Driver-approaching shows both addresses
   - No coordinates visible anywhere

---

## Troubleshooting

### Issue: "Location unavailable" shown
**Causes:**
- Invalid coordinates (null, NaN)
- Mapbox API error
- No features returned
- Network error

**Solution:**
1. Check console for error details
2. Verify `VITE_MAPBOX_ACCESS_TOKEN` is set
3. Check network tab for API response
4. Verify coordinates are valid numbers

### Issue: Raw coordinates still visible
**Causes:**
- Old code still using `reverseGeocode` directly
- String concatenation with coordinates

**Solution:**
1. Search for `reverseGeocode(` in codebase
2. Replace with `formatLocation` or related functions
3. Use `cleanLocationString` for existing strings

### Issue: Wrong location name
**Causes:**
- Mapbox returned incorrect feature
- Coordinates are inaccurate

**Solution:**
1. Check console logs for parsed feature
2. Verify input coordinates
3. Test coordinates on Mapbox website
4. Adjust priority types if needed

---

## Related Files

- `/src/services/locationFormatter.js` - Main service
- `/src/views/rider/RiderDashboard.vue` - Primary consumer
- `/src/composables/rider/useMap.js` - Map utilities
- `/docs/LOCATION_FORMATTING_SYSTEM.md` - This documentation

---

## Support

For questions or issues:
1. Check console logs for detailed information
2. Review this documentation
3. Test with known coordinates
4. Check Mapbox Geocoding API documentation

---

**Last Updated:** December 10, 2025
