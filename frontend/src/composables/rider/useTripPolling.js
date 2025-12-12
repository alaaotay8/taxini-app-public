/**
 * Trip status polling composable
 * Handles real-time trip status updates by polling the backend
 */
import { ref, onUnmounted } from 'vue'
import { riderAPI } from '@/services/api'

export const useTripPolling = () => {
  const activeTrip = ref(null)
  const pollInterval = ref(null)
  const isPolling = ref(false)

  /**
   * Start polling for trip status updates
   * @param {Function} callback - Called with updated trip data or null if no active trip
   * @param {Number} intervalMs - Polling interval in milliseconds (default: 3000)
   */
  const startPolling = (callback, intervalMs = 3000) => {
    // Don't start if already polling
    if (isPolling.value) {
      console.warn('⚠️ Polling already active')
      return
    }

    console.log(`▶️ Starting trip status polling (every ${intervalMs}ms)`)
    isPolling.value = true

    // Poll immediately on start
    pollOnce(callback)

    // Then poll at intervals
    pollInterval.value = setInterval(() => {
      pollOnce(callback)
    }, intervalMs)
  }

  /**
   * Poll once for trip status
   * @param {Function} callback - Called with trip data or null
   */
  const pollOnce = async (callback) => {
    try {
      const response = await riderAPI.getActiveTrip()
      
      if (response.has_active_trip && response.trip) {
        const oldStatus = activeTrip.value?.status
        const newStatus = response.trip.status
        
        // Log status changes
        if (oldStatus && oldStatus !== newStatus) {
          console.log(`🔄 Trip status changed: ${oldStatus} → ${newStatus}`)
        }
        
        activeTrip.value = response.trip
        
        // Call callback with trip data
        if (callback) callback(response.trip)
        
        // Auto-stop polling if trip is completed or cancelled
        if (newStatus === 'completed' || newStatus === 'cancelled') {
          console.log(`⏹️ Trip ${newStatus}, stopping polling`)
          stopPolling()
          if (callback) callback(null)
        }
      } else {
        // No active trip found
        if (activeTrip.value) {
          console.log('ℹ️ No active trip found (was active before)')
        }
        activeTrip.value = null
        
        // Stop polling if no active trip
        stopPolling()
        if (callback) callback(null)
      }
    } catch (error) {
      console.error('❌ Polling error:', error)
      // Don't stop polling on errors, keep trying
    }
  }

  /**
   * Stop polling for trip updates
   */
  const stopPolling = () => {
    if (pollInterval.value) {
      clearInterval(pollInterval.value)
      pollInterval.value = null
      isPolling.value = false
      console.log('⏹️ Trip status polling stopped')
    }
  }

  /**
   * Check if currently polling
   */
  const getIsPolling = () => isPolling.value

  // Cleanup on unmount
  onUnmounted(() => {
    stopPolling()
  })

  return {
    activeTrip,
    isPolling,
    startPolling,
    stopPolling,
    pollOnce,
    getIsPolling
  }
}
