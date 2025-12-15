/**
 * Driver Trip Management Composable
 * 
 * Handles all driver-side trip operations including:
 * - Polling for new trip requests
 * - Accepting/declining trip requests
 * - Managing active trip state (accepted, started, completed)
 * - Trip completion and rating workflow
 * 
 * @module useDriverTrip
 */

import { ref } from 'vue'
import { driverAPI } from '@/services/api'
import { useNotificationStore } from '@/services/notificationStore'
import { formatLocation } from '@/services/locationFormatter'

export function useDriverTrip() {
  // Notification store for UI alerts
  const { notifyTripRequested, notifyTripCompleted, notifyTripCancelled } = useNotificationStore()
  
  // ============================================================================
  // STATE MANAGEMENT
  // ============================================================================
  
  // Trip request state - incoming trip waiting for driver action
  const incomingRequest = ref(null)
  
  // Current active trip - trip driver has accepted/is executing
  const currentTrip = ref(null)
  
  // Trip request countdown timer (30s to accept or decline)
  const countdown = ref(30)
  const countdownOffset = ref(0)
  
  // Trip metrics during execution
  const tripDuration = ref(0)           // Seconds since trip started
  const distanceTraveled = ref(0)       // Kilometers traveled during trip
  const approachDistance = ref(0)       // Kilometers from driver to pickup location
  
  // Trip completion UI state
  const showCompletedModal = ref(false)
  const completedTrip = ref(null)
  const riderRating = ref(5)
  
  // Loading states
  const isAcceptingTrip = ref(false)    // Prevents double-accept clicks
  
  // ============================================================================
  // POLLING & INTERVALS
  // ============================================================================
  
  let countdownInterval = null          // 1-second timer for trip accept countdown
  let tripTimer = null                  // 1-second timer for trip duration
  let tripPollingInterval = null        // Adaptive polling for new trip requests
  let consecutiveEmptyChecks = 0        // Track consecutive polls with no trips (for backoff)
  
  // Adaptive polling configuration
  const MAX_POLL_INTERVAL = 15000       // Max 15 seconds between polls (when quiet)
  const MIN_POLL_INTERVAL = 5000        // Min 5 seconds between polls (when active)

  /**
   * Start polling for new trip requests with adaptive interval.
   * Uses exponential backoff when no trips are available to reduce server load.
   * 
   * @param {Object} isOnline - Ref containing driver's online status
   */
  const startPollingTrips = (isOnline) => {
    if (tripPollingInterval) return
    
    consecutiveEmptyChecks = 0
    const pollInterval = MIN_POLL_INTERVAL

    const adaptivePoll = async () => {
      const hasRequest = await checkForTripRequests(isOnline)
      
      if (!hasRequest) {
        consecutiveEmptyChecks++
        // Exponential backoff: increase interval when no trips available
        const nextInterval = Math.min(
          MIN_POLL_INTERVAL * Math.pow(1.5, Math.min(consecutiveEmptyChecks, 3)),
          MAX_POLL_INTERVAL
        )
        
        if (tripPollingInterval) {
          clearInterval(tripPollingInterval)
        }
        
        tripPollingInterval = setInterval(adaptivePoll, nextInterval)
      } else {
        consecutiveEmptyChecks = 0
        // Reset to fast polling when trip found
        if (tripPollingInterval) {
          clearInterval(tripPollingInterval)
        }
        tripPollingInterval = setInterval(adaptivePoll, MIN_POLL_INTERVAL)
      }
    }

    tripPollingInterval = setInterval(adaptivePoll, pollInterval)
    adaptivePoll() // Initial check
  }

  const stopPollingTrips = () => {
    if (tripPollingInterval) {
      clearInterval(tripPollingInterval)
      tripPollingInterval = null
    }
    consecutiveEmptyChecks = 0
  }

  // Check for trip requests
  const checkForTripRequests = async (isOnline) => {
    // Skip check if not online, on trip, or processing acceptance
    if (!isOnline.value || currentTrip.value || isAcceptingTrip.value) {
      return
    }

    try {
      const response = await driverAPI.getPendingTripRequests()
      
      if (response.success) {
        if (!response.has_request) {
          // Clear any stale incoming request
          if (incomingRequest.value) {
            incomingRequest.value = null
            stopCountdown()
          }
          return false
        }
        
        if (!response.trip_request) {
          console.warn('⚠️ Trip request missing in response')
          return false
        }
        
        // Check if this is the same request we already have
        if (incomingRequest.value?.id === response.trip_request.id) {
          console.log('⏭️ Same trip request, skipping notification')
          return false
        }
        
        console.log('🔔 New trip request:', response.trip_request.id)
        
        // Add to notification panel ONCE for new trips
        notifyTripRequested(
          response.trip_request.pickup_address || 'Pickup location',
          response.trip_request.destination_address || 'Destination'
        )
        console.log('📦 Raw backend data:', response.trip_request)
        
        // Use backend-provided formatted addresses (backend already geocodes)
        const formattedPickup = response.trip_request.pickup_address || 'Pickup Location'
        const formattedDestination = response.trip_request.destination_address || 'Destination'
        
        console.log('📍 Formatted addresses:', { 
          pickup: formattedPickup,
          destination: formattedDestination,
          hasPickup: !!response.trip_request.pickup_address,
          hasDestination: !!response.trip_request.destination_address
        })
        
        // Store with proper field mapping
        incomingRequest.value = {
          id: response.trip_request.id,
          rider_name: response.trip_request.rider_name || 'Rider',
          rider_phone: response.trip_request.rider_phone || 'N/A',
          rider_rating: response.trip_request.rider_rating,
          rider_trips: response.trip_request.rider_trips || 0,
          pickup_location_name: formattedPickup,
          destination_location_name: formattedDestination,
          pickup_latitude: response.trip_request.pickup_latitude,
          pickup_longitude: response.trip_request.pickup_longitude,
          pickup_lat: response.trip_request.pickup_latitude,
          pickup_lng: response.trip_request.pickup_longitude,
          destination_latitude: response.trip_request.destination_latitude,
          destination_longitude: response.trip_request.destination_longitude,
          destination_lat: response.trip_request.destination_latitude,
          destination_lng: response.trip_request.destination_longitude,
          estimated_distance_km: response.trip_request.estimated_distance || 0,
          estimated_cost_tnd: response.trip_request.estimated_cost || 0,
          distance_from_driver: response.trip_request.distance_from_driver || 0
        }
        
        console.log('✅ Trip request stored:', incomingRequest.value)
        
        // Add to notification panel (only for new trips) with trip ID for duplicate prevention
        notifyTripRequested(
          formattedPickup,
          formattedDestination,
          response.trip_request.id  // Pass trip ID for better duplicate detection
        )
        
        // Start 60-second countdown timer
        startCountdown(() => {
          console.log('⏰ Trip request timeout - auto declining')
          declineTrip() // Auto decline if no response
        })
        
        showTripRequestNotification()
        return true
      }
    } catch (error) {
      // Silently handle network errors - expected when offline or no trips available
      if (!error.message.includes('Network error')) {
        console.error('❌ Failed to check trip requests:', error.message)
      }
    }
    return false
  }

  // Start countdown timer (60 seconds)
  const startCountdown = (onTimeout) => {
    countdown.value = 60
    countdownOffset.value = 0
    
    const circumference = 2 * Math.PI * 35 // radius = 35
    
    countdownInterval = setInterval(() => {
      countdown.value -= 1
      countdownOffset.value = circumference * (1 - countdown.value / 60)
      
      if (countdown.value <= 0) {
        clearInterval(countdownInterval)
        if (onTimeout) onTimeout()
      }
    }, 1000)
  }

  // Stop countdown
  const stopCountdown = () => {
    if (countdownInterval) {
      clearInterval(countdownInterval)
      countdownInterval = null
    }
  }

  // Show trip request notification
  const showTripRequestNotification = () => {
    try {
      const audio = new Audio('/notification.mp3')
      audio.play().catch(e => console.log('Could not play sound:', e))
      
      if (navigator.vibrate) {
        navigator.vibrate([200, 100, 200])
      }
    } catch (e) {
      console.log('Notification error:', e)
    }
  }

  // Accept trip with retry logic
  const acceptTrip = async (driverLocation, calculateDistance, drawRoute) => {
    if (isAcceptingTrip.value) {
      console.warn('⚠️ Already accepting a trip, ignoring duplicate request')
      return
    }

    if (!incomingRequest.value?.id) {
      console.error('❌ No trip request to accept')
      return
    }

    isAcceptingTrip.value = true
    stopCountdown()

    const tripId = incomingRequest.value.id
    const maxRetries = 2
    let lastError = null

    // Try accepting with retries
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.log(`🔄 Accepting trip ${tripId} (attempt ${attempt}/${maxRetries})`)
        
        // Call backend API to accept the trip
        const { driverAPI } = await import('@/services/api')
        await driverAPI.acceptTrip(tripId, 'Driver accepted the trip')
        
        console.log('✅ Trip accepted successfully:', tripId)
        
        // Format pickup and destination addresses
        let formattedPickup = incomingRequest.value.pickup_location_name || 'Pickup Location'
        let formattedDestination = incomingRequest.value.destination_location_name || 'Destination'

        if (incomingRequest.value.pickup_lat && incomingRequest.value.pickup_lng) {
          formattedPickup = await formatLocation(
            incomingRequest.value.pickup_lng,
            incomingRequest.value.pickup_lat
          )
        }

        if (incomingRequest.value.destination_lat && incomingRequest.value.destination_lng) {
          formattedDestination = await formatLocation(
            incomingRequest.value.destination_lng,
            incomingRequest.value.destination_lat
          )
        }
        
        // Set current trip
        currentTrip.value = {
          ...incomingRequest.value,
          status: 'accepted',
          acceptedAt: Date.now(),
          rider_confirmed_pickup: false,
          pickup_location_name: formattedPickup,
          destination_location_name: formattedDestination
        }
        
        // Clear incoming request
        incomingRequest.value = null
        
        // Calculate initial approach distance
        approachDistance.value = calculateDistance(
          driverLocation.value.lat,
          driverLocation.value.lng,
          currentTrip.value.pickup_lat,
          currentTrip.value.pickup_lng
        )
        
        // Draw route to pickup
        await drawRoute(
          { lng: driverLocation.value.lng, lat: driverLocation.value.lat },
          { lng: currentTrip.value.pickup_lng, lat: currentTrip.value.pickup_lat }
        )
        
        // Start monitoring for trip cancellations
        startTripMonitoring()

        // Show success notification
        if (typeof window !== 'undefined' && window.$notification) {
          window.$notification.success(
            `Heading to pickup location (${(approachDistance.value / 1000).toFixed(1)}km away)`,
            { title: 'Trip Accepted', priority: 'high' }
          )
        }

        isAcceptingTrip.value = false
        return // Success!
        
      } catch (error) {
        lastError = error
        // Only log non-network errors
        if (!error.message.includes('Network error')) {
          console.error(`❌ Accept attempt ${attempt} failed:`, error.message)
        }
        
        // Wait before retry (exponential backoff)
        if (attempt < maxRetries) {
          const delay = Math.pow(2, attempt) * 500 // 1s, 2s
          await new Promise(resolve => setTimeout(resolve, delay))
        }
      }
    }

    // All retries failed
    isAcceptingTrip.value = false
    
    // Show error notification
    if (typeof window !== 'undefined' && window.$notification) {
      window.$notification.error(
        'Could not accept the trip. Please check your connection and try again.',
        { title: 'Connection Error', priority: 'high' }
      )
    }
    
    // Restore countdown so driver can try again
    if (incomingRequest.value?.id === tripId) {
      startCountdown(() => {
        console.log('⏰ Trip request timeout - auto declining')
        declineTrip()
      })
    }
    
    throw new Error(lastError?.response?.data?.detail || lastError?.message || 'Failed to accept trip. Please try again.')
  }

  // Decline trip with duplicate prevention
  let decliningInProgress = false
  
  const declineTrip = async (clearMapMarkers) => {
    if (decliningInProgress) {
      console.warn('⚠️ Decline already in progress, ignoring duplicate call')
      return
    }
    
    if (!incomingRequest.value?.id) {
      console.warn('⚠️ No trip to decline')
      stopCountdown()
      incomingRequest.value = null
      if (clearMapMarkers) clearMapMarkers()
      return
    }
    
    decliningInProgress = true
    stopCountdown()
    
    try {
      const tripId = incomingRequest.value.id
      console.log('⏳ Declining trip:', tripId)
      
      // Clear request immediately to prevent duplicate attempts
      const requestToDecline = incomingRequest.value
      incomingRequest.value = null
      
      // Call backend API to reject the trip
      const { driverAPI } = await import('@/services/api')
      await driverAPI.rejectTrip(tripId, 'Driver declined the trip')
      
      console.log('✅ Trip declined successfully:', tripId)
      
      // Show success notification ONCE
      if (typeof window !== 'undefined' && window.$notification) {
        window.$notification.info(
          'The rider has been notified and can select another driver.',
          { title: 'Trip Declined' }
        )
      }
    } catch (error) {
      console.error('❌ Failed to decline trip:', error)
      // Show error notification ONCE
      if (typeof window !== 'undefined' && window.$notification) {
        window.$notification.error(
          'Could not decline trip. Please try again.',
          { title: 'Decline Failed' }
        )
      }
      // Keep request cleared even if API call fails
    } finally {
      decliningInProgress = false
      incomingRequest.value = null
      if (clearMapMarkers) clearMapMarkers()
      console.log('🧹 Incoming request cleared after decline')
    }
  }

  // Start trip (when arrived at pickup)
  const startTrip = async (driverLocation, removePickupMarker, drawRoute) => {
    try {
      // Call backend API to start the trip
      const { driverAPI } = await import('@/services/api')
      await driverAPI.updateTripStatus(currentTrip.value.id, 'started', 'Driver has picked up rider')
      
      console.log('🚗 Trip started:', currentTrip.value.id)
      
      // Show success notification
      if (typeof window !== 'undefined' && window.$notification) {
        window.$notification.success(
          'Heading to destination. Drive safely!',
          { title: 'Trip Started', priority: 'high' }
        )
      }
      
      currentTrip.value.status = 'started'
      currentTrip.value.startedAt = Date.now()
      tripDuration.value = 0
      distanceTraveled.value = 0
      
      // Start trip timer
      tripTimer = setInterval(() => {
        tripDuration.value += 1
      }, 1000)
      
      // Remove pickup marker
      if (removePickupMarker) removePickupMarker()
      
      // Draw route to destination
      await drawRoute(
        { lng: driverLocation.value.lng, lat: driverLocation.value.lat },
        { lng: currentTrip.value.destination_lng, lat: currentTrip.value.destination_lat }
      )
    } catch (error) {
      console.error('Failed to start trip:', error)
      // Check if error is about rider confirmation
      if (error.message && error.message.includes('Rider has not confirmed pickup')) {
        // Show notification and start polling for rider confirmation
        if (typeof window !== 'undefined' && window.showWaitingForConfirmation) {
          window.showWaitingForConfirmation()
        }
        throw new Error('WAITING_FOR_CONFIRMATION')
      }
      throw error
    }
  }

  // Complete trip
  const completeTrip = async (clearMapMarkers, updateStats) => {
    if (tripTimer) {
      clearInterval(tripTimer)
      tripTimer = null
    }

    try {
      // Call backend API to complete the trip
      const { driverAPI } = await import('@/services/api')
      await driverAPI.updateTripStatus(currentTrip.value.id, 'completed', 'Trip completed successfully')
      
      console.log('✅ Trip completed:', currentTrip.value.id)
      
      const fare = currentTrip.value.estimated_cost_tnd
      const netEarnings = fare * 0.8 // After 20% commission
      
      // Add to notification panel (this will also show the toast notification)
      notifyTripCompleted(netEarnings.toFixed(2), 'TND', 'driver')
      
      completedTrip.value = {
        ...currentTrip.value,
        duration: tripDuration.value,
        actualDistance: distanceTraveled.value,
        netEarnings
      }
      
      currentTrip.value = null
      tripDuration.value = 0
      distanceTraveled.value = 0
      
      if (clearMapMarkers) clearMapMarkers()
      
      // Show completed modal
      showCompletedModal.value = true
      riderRating.value = 5
      
      return netEarnings
    } catch (error) {
      console.error('Failed to complete trip:', error)
      throw error
    }
  }

  // Close completed modal and submit rating
  const closeCompletedModal = async () => {
    try {
      // Rating submission will be implemented when backend endpoint is ready
      console.log('Trip rated:', riderRating.value)
      
      showCompletedModal.value = false
      completedTrip.value = null
    } catch (error) {
      console.error('Failed to submit rating:', error)
    }
  }

  // Monitor current trip for cancellations and updates
  let tripStatusInterval = null
  
  const startTripMonitoring = () => {
    if (tripStatusInterval) return
    
    console.log('🔍 Starting trip status monitoring...')
    
    tripStatusInterval = setInterval(async () => {
      if (!currentTrip.value) {
        console.log('⏹️ No current trip, stopping monitoring')
        stopTripMonitoring()
        return
      }
      
      try {
        const response = await driverAPI.getActiveTrip()
        console.log('📊 Trip status check:', {
          has_active_trip: response.has_active_trip,
          trip_exists: !!response.trip,
          trip_status: response.trip?.status,
          current_trip_id: currentTrip.value?.id
        })
        
        // Check if has_active_trip is false - trip was cancelled or completed
        if (!response.has_active_trip || !response.trip) {
          console.log('🚫 Trip no longer active - cancelled by rider')
          if (currentTrip.value) {
            // Show cancellation alert using custom dialog
            if (typeof window !== 'undefined' && window.showCancellationAlert) {
              window.showCancellationAlert('Trip was cancelled by the rider')
            }
            currentTrip.value = null
            stopTripMonitoring()
          }
          return
        }
        
        // Double-check if trip status is cancelled
        if (response.trip.status === 'cancelled') {
          console.log('🚫 Trip status is cancelled')
          // Show cancellation alert using custom dialog
          if (typeof window !== 'undefined' && window.showCancellationAlert) {
            window.showCancellationAlert('Trip was cancelled by the rider')
          }
          currentTrip.value = null
          stopTripMonitoring()
          return
        }
        
        // Sync rider_confirmed_pickup from backend
        if (currentTrip.value && response.trip.rider_confirmed_pickup && !currentTrip.value.rider_confirmed_pickup) {
          console.log('✅ Rider confirmed pickup - updating local state')
          currentTrip.value.rider_confirmed_pickup = true
          currentTrip.value.rider_confirmed_at = response.trip.rider_confirmed_at
        }
      } catch (error) {
        console.error('❌ Error monitoring trip status:', error)
        // Don't stop monitoring on error, just log it
      }
    }, 3000) // Check every 3 seconds
  }

  const stopTripMonitoring = () => {
    if (tripStatusInterval) {
      console.log('⏹️ Stopping trip status monitoring')
      clearInterval(tripStatusInterval)
      tripStatusInterval = null
    }
  }

  // Cleanup
  const cleanupTrip = () => {
    stopCountdown()
    stopPollingTrips()
    stopTripMonitoring()
    if (tripTimer) {
      clearInterval(tripTimer)
      tripTimer = null
    }
  }

  // Utility functions
  const getInitials = (name) => {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const openNavigation = (lat, lng) => {
    const url = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`
    window.open(url, '_blank')
  }

  // Check for active trip on mount and start monitoring
  const initializeActiveTrip = async () => {
    try {
      console.log('🔍 Checking for active trip on mount...')
      const response = await driverAPI.getActiveTrip()
      
      if (response.has_active_trip && response.trip) {
        console.log('✅ Found active trip:', response.trip)
        
        // Format pickup and destination addresses
        let formattedPickup = response.trip.pickup_address || 'Pickup Location'
        let formattedDestination = response.trip.destination_address || 'Destination'

        if (response.trip.pickup_latitude && response.trip.pickup_longitude) {
          formattedPickup = await formatLocation(
            response.trip.pickup_longitude,
            response.trip.pickup_latitude
          )
        }

        if (response.trip.destination_latitude && response.trip.destination_longitude) {
          formattedDestination = await formatLocation(
            response.trip.destination_longitude,
            response.trip.destination_latitude
          )
        }
        
        currentTrip.value = {
          ...response.trip,
          pickup_location_name: formattedPickup,
          destination_location_name: formattedDestination
        }
        
        // Store trip data for UI restoration
        if (typeof window !== 'undefined') {
          window.restoreDriverTripState = {
            pickup: {
              lat: response.trip.pickup_latitude,
              lng: response.trip.pickup_longitude,
              address: response.trip.pickup_address
            },
            destination: {
              lat: response.trip.destination_latitude,
              lng: response.trip.destination_longitude,
              address: response.trip.destination_address
            },
            rider: {
              name: response.trip.rider_name,
              phone: response.trip.rider_phone
            },
            status: response.trip.status
          }
        }
        
        // Start monitoring for cancellations
        startTripMonitoring()
        
        return true
      } else {
        console.log('ℹ️ No active trip found')
        if (typeof window !== 'undefined') {
          delete window.restoreDriverTripState
        }
        return false
      }
    } catch (error) {
      // Handle authentication errors gracefully
      if (error.message && (error.message.includes('User not found') || error.message.includes('Driver not found'))) {
        console.warn('⚠️ Driver authentication issue - may need to re-login')
      } else {
        console.error('❌ Error checking for active trip:', error)
      }
      
      // Clean up any stale data
      if (typeof window !== 'undefined') {
        delete window.restoreDriverTripState
      }
      
      return false
    }
  }

  return {
    // State
    incomingRequest,
    currentTrip,
    countdown,
    countdownOffset,
    tripDuration,
    distanceTraveled,
    approachDistance,
    showCompletedModal,
    completedTrip,
    riderRating,
    isAcceptingTrip,
    
    // Methods
    initializeActiveTrip,
    startPollingTrips,
    stopPollingTrips,
    checkForTripRequests,
    startCountdown,
    stopCountdown,
    showTripRequestNotification,
    acceptTrip,
    declineTrip,
    startTrip,
    completeTrip,
    closeCompletedModal,
    cleanupTrip,
    startTripMonitoring,
    stopTripMonitoring,
    getInitials,
    formatDuration,
    openNavigation
  }
}
