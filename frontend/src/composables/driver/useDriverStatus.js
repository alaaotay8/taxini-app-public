import { ref } from 'vue'

export function useDriverStatus() {
  // State
  const isOnline = ref(false)
  const loading = ref(false)
  const loadingMessage = ref('')
  const todayEarnings = ref(0)
  const todayTrips = ref(0)
  const onlineHours = ref(0)
  
  // Intervals
  let locationUpdateInterval = null
  let onlineTimeInterval = null

  // Send location update to backend (debounced for performance)
  let lastLocationUpdate = 0
  const LOCATION_UPDATE_THROTTLE = 3000 // 3 seconds minimum between updates
  
  const sendLocationUpdate = async (lat, lng) => {
    if (!isOnline.value) return
    
    // Throttle location updates to reduce API calls
    const now = Date.now()
    if (now - lastLocationUpdate < LOCATION_UPDATE_THROTTLE) {
      return // Skip this update
    }
    lastLocationUpdate = now

    try {
      // Import locationAPI
      const { locationAPI } = await import('@/services/api')
      const authStore = (await import('@/stores/auth')).useAuthStore()
      
      if (authStore.user && authStore.user.id) {
        await locationAPI.updateLocation(authStore.user.id, lat, lng, 'driver')
        console.log('📍 Location updated:', { lat, lng })
      }
    } catch (error) {
      console.error('❌ Failed to update location:', error)
    }
  }

  // Start location updates every 4-5 seconds (optimized interval)
  const startLocationUpdates = (driverLocation) => {
    // Clear any existing interval
    if (locationUpdateInterval) {
      clearInterval(locationUpdateInterval)
    }
    
    locationUpdateInterval = setInterval(() => {
      if (isOnline.value && driverLocation.value?.lat && driverLocation.value?.lng) {
        sendLocationUpdate(driverLocation.value.lat, driverLocation.value.lng)
      }
    }, 5000) // 5 seconds (reduced frequency for better performance)
  }

  // Stop location updates
  const stopLocationUpdates = () => {
    if (locationUpdateInterval) {
      clearInterval(locationUpdateInterval)
      locationUpdateInterval = null
    }
  }

  // Toggle online/offline status
  const toggleOnlineStatus = async (currentTrip, startPollingTrips, stopPollingTrips) => {
    if (currentTrip.value) return // Can't toggle during trip

    loading.value = true
    loadingMessage.value = isOnline.value ? 'Going offline...' : 'Going online...'

    try {
      // Import driverAPI
      const { driverAPI } = await import('@/services/api')
      
      // Call backend API to update driver status
      const newStatus = isOnline.value ? 'offline' : 'online'
      await driverAPI.updateStatus(newStatus)
      
      console.log(`✅ Driver status updated to: ${newStatus}`)
      
      isOnline.value = !isOnline.value
      
      if (isOnline.value) {
        startPollingTrips(isOnline)
        startOnlineTimer()
      } else {
        stopPollingTrips()
        stopOnlineTimer()
      }
    } catch (error) {
      console.error('❌ Failed to toggle status:', error)
      console.error('Error details:', {
        message: error.message,
        response: error.response,
        status: error.response?.status,
        data: error.response?.data
      })
      
      // Show detailed error to user
      const errorMessage = error.message || 'Failed to update status. Please try again.'
      alert(errorMessage)
    } finally {
      loading.value = false
    }
  }

  // Start online hours timer
  const startOnlineTimer = () => {
    if (onlineTimeInterval) return
    
    onlineTimeInterval = setInterval(() => {
      onlineHours.value += 1/3600 // Increment by 1 second converted to hours
    }, 1000)
  }

  // Stop online hours timer
  const stopOnlineTimer = () => {
    if (onlineTimeInterval) {
      clearInterval(onlineTimeInterval)
      onlineTimeInterval = null
    }
  }

  // Update earnings and trips count
  const updateStats = (earnings, trips) => {
    todayEarnings.value = earnings
    todayTrips.value = trips
  }

  // Cleanup
  const cleanupStatus = () => {
    stopLocationUpdates()
    stopOnlineTimer()
  }

  return {
    // State
    isOnline,
    loading,
    loadingMessage,
    todayEarnings,
    todayTrips,
    onlineHours,
    
    // Methods
    sendLocationUpdate,
    startLocationUpdates,
    stopLocationUpdates,
    toggleOnlineStatus,
    startOnlineTimer,
    stopOnlineTimer,
    updateStats,
    cleanupStatus
  }
}
