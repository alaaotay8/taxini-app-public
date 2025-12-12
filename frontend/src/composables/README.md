# Composables

This folder contains reusable Vue 3 Composition API functions organized by domain.

## Structure

```
composables/
├── rider/           # Rider-specific composables
│   ├── useMap.js                    # Map initialization & geolocation
│   ├── useTripManagement.js         # Trip state & API calls
│   ├── useDestinationPicker.js      # Map-based destination selection
│   └── useUIState.js                # UI state & touch gestures
│
└── driver/          # Driver-specific composables
    ├── useDriverMap.js              # Map, markers & route drawing
    ├── useDriverStatus.js           # Online/offline status & stats
    ├── useDriverTrip.js             # Trip management & polling
    └── useDriverUI.js               # UI state & navigation
```

## Rider Composables

### `useMap.js`
- **Purpose**: Mapbox map initialization and user location tracking
- **Exports**: mapContainer, map, userLocation, initMap(), getCurrentLocation(), setDestinationMarker()
- **Used by**: RiderDashboard.vue

### `useTripManagement.js`
- **Purpose**: Trip state management and backend API integration
- **Exports**: tripState, selectedDriver, requestRide(), selectDriverForTrip()
- **Used by**: RiderDashboard.vue

### `useDestinationPicker.js`
- **Purpose**: Map-based destination selection with marker placement
- **Exports**: destination, enableDestinationPicker(), confirmDestination()
- **Used by**: RiderDashboard.vue

### `useUIState.js`
- **Purpose**: UI visibility state and touch gesture handling
- **Exports**: showSideMenu, showBottomSheet, handleMapClick(), toggleBottomSheet()
- **Used by**: RiderDashboard.vue

## Driver Composables

### `useDriverMap.js`
- **Purpose**: Map management, markers, location tracking, route drawing
- **Exports**: map, driverLocation, initMap(), addPickupMarker(), drawRoute()
- **Used by**: DriverDashboard.vue

### `useDriverStatus.js`
- **Purpose**: Driver online/offline status, earnings, stats tracking
- **Exports**: isOnline, todayEarnings, toggleOnlineStatus(), startLocationUpdates()
- **Used by**: DriverDashboard.vue

### `useDriverTrip.js`
- **Purpose**: Trip request polling, acceptance, trip lifecycle management
- **Exports**: incomingRequest, currentTrip, acceptTrip(), startTrip(), completeTrip()
- **Used by**: DriverDashboard.vue

### `useDriverUI.js`
- **Purpose**: UI state, menu visibility, bottom sheet gestures, navigation
- **Exports**: showMenu, showBottomSheet, handleMapClick(), toggleMenu()
- **Used by**: DriverDashboard.vue

## Usage Example

```vue
<script setup>
import { useMap } from '@/composables/rider/useMap'
import { useTripManagement } from '@/composables/rider/useTripManagement'

const { map, initMap, getCurrentLocation } = useMap()
const { tripState, requestRide } = useTripManagement()

onMounted(() => {
  initMap()
  getCurrentLocation()
})
</script>
```

## Benefits

- ✅ **Separation of Concerns**: Each composable handles one specific domain
- ✅ **Reusability**: Can be used across multiple components
- ✅ **Testability**: Each composable can be tested independently
- ✅ **Maintainability**: Changes are isolated to specific files
- ✅ **Type Safety**: Clear exports and function signatures
