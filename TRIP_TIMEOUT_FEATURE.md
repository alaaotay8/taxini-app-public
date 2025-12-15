# Trip Timeout Feature Implementation

## Overview
Implements a 30-minute trip timeout check that prompts both driver and rider to confirm they're still on the trip.

## Backend Changes

### 1. Trip Cancellation Support (`~/taxini-app/backend/src/api/v1/drivers.py`)

**Added 'cancelled' status to valid transitions:**
```python
valid_transitions = {
    "accepted": ["started", "cancelled"],  # Can cancel after accepting
    "started": ["completed", "cancelled"]   # Can cancel during trip
}
```

**Features:**
- ✅ Driver can cancel trip at any time after accepting
- ✅ Sets `cancelled_at` timestamp
- ✅ Records `cancellation_reason`
- ✅ Sets driver back to `online` status
- ✅ Sends notification to rider about cancellation
- ✅ Updates trip status immediately (rider's polling will detect it)

### 2. Trip Timeout Check Endpoint

**New Endpoint:** `POST /api/v1/drivers/trip-timeout-check`

**Purpose:** Handle responses to 30-minute timeout check

**Request Body:**
```json
{
  "trip_id": "uuid",
  "still_on_trip": true/false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Trip status confirmed" or "Trip cancelled due to timeout",
  "trip_status": "started" or "cancelled"
}
```

**Behavior:**
- If `still_on_trip = false` or no response within 1 minute:
  - Cancels trip automatically
  - Sets driver to online
  - Notifies both parties
  - Records cancellation reason: "Trip timeout - No response to status check"
- If `still_on_trip = true`:
  - Continues trip normally
  - Logs confirmation

## Frontend Implementation Needed

### 1. Trip Duration Tracking (To be implemented)

**Location:** `~/taxini-app/frontend/src/composables/shared/useTripTimeout.js`

```javascript
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { driverAPI } from '@/services/api'

export function useTripTimeout(tripId, userRole) {
  const tripStartTime = ref(null)
  const timeoutCheckShown = ref(false)
  const checkInterval = ref(null)
  const responseTimeout = ref(null)
  
  const tripDurationMinutes = computed(() => {
    if (!tripStartTime.value) return 0
    return Math.floor((Date.now() - tripStartTime.value) / 1000 / 60)
  })
  
  const startTracking = (startedAt) => {
    tripStartTime.value = new Date(startedAt).getTime()
    
    // Check every minute for 30-minute threshold
    checkInterval.value = setInterval(() => {
      if (tripDurationMinutes.value >= 30 && !timeoutCheckShown.value) {
        showTimeoutCheck()
      }
    }, 60000) // Check every minute
  }
  
  const showTimeoutCheck = () => {
    timeoutCheckShown.value = true
    
    // Show dialog asking: "Still on trip?"
    window.$notification?.warning(
      'Trip Duration Check',
      {
        message: 'You have been on this trip for 30 minutes. Are you still traveling?',
        actions: [
          {
            label: 'Yes, Still Traveling',
            onClick: () => respondToCheck(true)
          },
          {
            label: 'No, End Trip',
            onClick: () => respondToCheck(false)
          }
        ],
        priority: 'high',
        persistent: true
      }
    )
    
    // Auto-cancel if no response within 1 minute
    responseTimeout.value = setTimeout(() => {
      if (timeoutCheckShown.value) {
        respondToCheck(false) // Auto-cancel
      }
    }, 60000) // 1 minute timeout
  }
  
  const respondToCheck = async (stillOnTrip) => {
    try {
      if (responseTimeout.value) {
        clearTimeout(responseTimeout.value)
      }
      
      const response = await driverAPI.respondToTripTimeout(tripId.value, stillOnTrip)
      
      if (response.success) {
        if (stillOnTrip) {
          window.$notification?.success('Trip Continuing', {
            message: 'Your trip is continuing normally'
          })
          timeoutCheckShown.value = false
          // Reset the 30-minute timer
          tripStartTime.value = Date.now()
        } else {
          window.$notification?.info('Trip Cancelled', {
            message: 'The trip has been cancelled'
          })
          // Navigate to appropriate screen
        }
      }
    } catch (error) {
      console.error('Failed to respond to timeout check:', error)
    }
  }
  
  const stopTracking = () => {
    if (checkInterval.value) {
      clearInterval(checkInterval.value)
    }
    if (responseTimeout.value) {
      clearTimeout(responseTimeout.value)
    }
    tripStartTime.value = null
    timeoutCheckShown.value = false
  }
  
  onUnmounted(() => {
    stopTracking()
  })
  
  return {
    tripDurationMinutes,
    startTracking,
    stopTracking,
    respondToCheck
  }
}
```

### 2. Add API Method

**Location:** `~/taxini-app/frontend/src/services/api.js`

```javascript
export const driverAPI = {
  // ... existing methods
  
  // Respond to trip timeout check
  respondToTripTimeout: (tripId, stillOnTrip) =>
    apiClient.post('/drivers/trip-timeout-check', {
      trip_id: tripId,
      still_on_trip: stillOnTrip
    })
}

export const riderAPI = {
  // ... existing methods
  
  // Respond to trip timeout check
  respondToTripTimeout: (tripId, stillOnTrip) =>
    apiClient.post('/riders/trip-timeout-check', {
      trip_id: tripId,
      still_on_trip: stillOnTrip
    })
}
```

### 3. Integrate into Dashboards

**DriverDashboard.vue:**
```javascript
import { useTripTimeout } from '@/composables/shared/useTripTimeout'

// In setup()
const { tripDurationMinutes, startTracking, stopTracking } = useTripTimeout(
  computed(() => currentTrip.value?.id),
  'driver'
)

// When trip starts
watch(() => currentTrip.value?.status, (newStatus) => {
  if (newStatus === 'started' && currentTrip.value?.started_at) {
    startTracking(currentTrip.value.started_at)
  } else if (newStatus === 'completed' || newStatus === 'cancelled') {
    stopTracking()
  }
})
```

**RiderDashboard.vue:**
```javascript
// Same integration as driver
```

## Testing Checklist

### Cancellation Feature
- [ ] Driver cancels trip after accepting → Rider sees cancellation immediately
- [ ] Driver cancels trip during ride → Rider gets notification
- [ ] Driver status returns to 'online' after cancellation
- [ ] Trip status changes to 'cancelled' in database
- [ ] Cancellation reason is recorded

### Timeout Feature (After frontend implementation)
- [ ] Trip reaches 30 minutes → Both users get prompt
- [ ] User responds "Yes" → Trip continues, timer resets
- [ ] User responds "No" → Trip cancels immediately
- [ ] No response within 1 minute → Trip auto-cancels
- [ ] Both users notified of timeout cancellation

## Database Migration Needed (Optional)

Add `last_status_check` field to track when users last confirmed trip status:

```sql
ALTER TABLE trips ADD COLUMN last_status_check TIMESTAMP;
```

This allows tracking multiple 30-minute intervals for very long trips.

## Notes

- Timeout check runs every 30 minutes (can trigger multiple times for long trips)
- 1-minute response window for user action
- Automatic cancellation ensures no "zombie" trips in the system
- Both driver and rider can cancel at any time
- Cancellation is immediate and synced via polling
