/**
 * Trip management composable
 * Handles trip state, driver selection, and API calls
 */
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { locationAPI, riderAPI } from '@/services/api'
import { useNotificationStore } from '@/services/notificationStore'

export function useTripManagement(userLocation = null, destination = null) {
  const authStore = useAuthStore()
  
  // Notification store
  const {
    notifyTripCompleted,
    notifyTripCancelled,
    notifyTripAccepted,
    notifyDriverArrived,
    notifyTripStarted,
    notifyNoDriversAvailable,
    notifyDriverDeclined
  } = useNotificationStore()

  // Trip state management
  const tripState = ref('search') // search, select-driver, driver-found, requested, active, completed
  const tripStatus = ref('Assigned') // Assigned, Accepted, Started
  const selectedDriver = ref(null)
  const estimatedCost = ref(0)
  const rating = ref(0)
  const review = ref('')
  const activeTrip = ref(null) // Store active trip data from backend

  // Nearby drivers data - starts empty, populated by fetchNearbyDrivers()
  const nearbyDrivers = ref([])
  const loadingDrivers = ref(false)
  const driversError = ref(null)
  
  // Driver fetch caching to prevent redundant API calls
  let lastDriverFetch = 0
  const DRIVER_FETCH_COOLDOWN = 3000 // 3 seconds minimum between fetches

  /**
   * Calculate distance between two coordinates using Haversine formula
   */
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

  /**
   * Map backend trip status to frontend trip state
   * Backend: requested, assigned, accepted, started, completed, cancelled
   * Frontend: search, select-driver, driver-found, requested, driver-approaching, active, completed
   */
  const mapBackendStatusToFrontendState = (backendStatus) => {
    const statusMap = {
      'requested': 'requested',         // Trip created, waiting for driver assignment
      'assigned': 'requested',          // Driver assigned, awaiting acceptance (show waiting view)
      'accepted': 'driver-approaching', // Driver accepted, approaching rider (rider must confirm)
      'started': 'active',              // Driver started the trip (trip in progress)
      'completed': 'completed',         // Trip finished
      'cancelled': 'search'             // Trip cancelled, reset to search
    }
    
    const mappedState = statusMap[backendStatus] || 'search'
    console.log(`🔄 Status mapping: backend "${backendStatus}" → frontend "${mappedState}"`)
    return mappedState
  }

  /**
   * Map backend trip status to user-friendly display text
   */
  const mapBackendStatusToDisplayText = (backendStatus) => {
    const displayMap = {
      'requested': 'Finding Driver...',
      'assigned': 'Driver Assigned',
      'accepted': 'Driver Approaching',
      'started': 'Trip Started',
      'completed': 'Completed',
      'cancelled': 'Cancelled'
    }
    return displayMap[backendStatus] || 'Unknown'
  }

  const tripSummary = ref({
    distance: 12.5,
    duration: 25,
    baseFare: 2.5,
    distanceFee: 15.0,
    totalCost: 17.5
  })

  /**
   * Fetch nearby drivers from backend API
   * Maps backend structure to frontend expected format
   */
  const fetchNearbyDrivers = async (userLatitude, userLongitude, options = {}) => {
    if (!userLatitude || !userLongitude) {
      console.warn('Cannot fetch drivers without user location')
      return { drivers: [], updated: false }
    }
    
    // Check cooldown to prevent rapid successive calls (unless forced)
    const now = Date.now()
    if (!options.force && (now - lastDriverFetch) < DRIVER_FETCH_COOLDOWN) {
      if (!options.silent) {
        console.log('⏳ Driver fetch on cooldown, skipping...')
      }
      return { drivers: nearbyDrivers.value, updated: false }
    }
    
    lastDriverFetch = now

    // Only show loading spinner if NOT background polling (silent mode)
    if (!options.silent) {
      loadingDrivers.value = true
    }
    driversError.value = null

    try {
      if (!options.silent) {
        console.log(`🔍 Fetching nearby drivers for location: ${userLatitude}, ${userLongitude}`)
      }
      
      const response = await locationAPI.getNearbyDrivers(userLatitude, userLongitude)
      
      if (response.success && response.drivers) {
        console.log(`✅ Found ${response.total} drivers:`, response.drivers)
        
        // Map backend structure to frontend format
        const mappedDrivers = response.drivers.map(driver => {
          // Calculate distance if backend doesn't provide it or provides 0
          let distanceKm = driver.distance_km
          
          if (!distanceKm || distanceKm === 0) {
            console.warn(`⚠️ Backend distance is 0 for driver ${driver.name}, calculating manually`)
            distanceKm = calculateDistance(
              userLatitude,
              userLongitude,
              driver.latitude,
              driver.longitude
            )
            console.log(`📏 Calculated distance: ${distanceKm.toFixed(2)} km`)
          }
          
          // Calculate ETA: 2 minutes per km, minimum 1 minute
          const eta = Math.max(1, Math.ceil(distanceKm * 2))
          
          // Calculate approach fee: 0.50 TND per km
          const approachFee = parseFloat((distanceKm * 0.5).toFixed(3))
          
          console.log(`🚗 ${driver.name}: ${distanceKm.toFixed(2)} km, ${eta} min, ${approachFee.toFixed(3)} TND`)
          
          return {
            id: driver.user_id,           // ✅ Use user_id as driver identifier
            user_id: driver.user_id,      // ✅ Keep for hash comparison
            name: driver.name,             // ✅ Driver name from backend
            distance: distanceKm,          // ✅ Distance in km (calculated if needed)
            distance_km: distanceKm,       // ✅ Keep for hash comparison
            eta: eta,                      // ✅ 2 min per km, minimum 1 min
            approachFee: approachFee,      // ✅ 0.50 TND per km
            rating: driver.rating || 0,    // ✅ Driver rating from backend
            taxiNumber: driver.taxi_number || 'N/A',
            coords: { 
              lng: driver.longitude, 
              lat: driver.latitude 
            }
          }
        })
        
        // Only update nearbyDrivers if not using smart polling
        if (!options.skipUpdate) {
          nearbyDrivers.value = mappedDrivers
        }
        
        if (!options.silent) {
          console.log('📊 Mapped drivers:', mappedDrivers)
        }
        return { drivers: mappedDrivers, updated: true }
      } else {
        if (!options.silent) {
          console.warn('⚠️ No drivers found:', response.message)
        }
        if (!options.skipUpdate) {
          nearbyDrivers.value = []
        }
        driversError.value = response.message || 'No drivers available'
        return { drivers: [], updated: true }
      }
    } catch (error) {
      if (!options.silent) {
        console.error('❌ Error fetching nearby drivers:', error)
      }
      if (!options.skipUpdate) {
        nearbyDrivers.value = []
      }
      driversError.value = error.message || 'Failed to fetch drivers'
      return { drivers: [], updated: false }
    } finally {
      // Only clear loading if not silent mode
      if (!options.silent) {
        loadingDrivers.value = false
      }
    }
  }

  /**
   * Select a driver for the trip
   */
  const selectDriverForTrip = (driver) => {
    selectedDriver.value = driver
    console.log('Selected driver:', driver.name)
  }

  /**
   * Select driver for booking (from available drivers list)
   * Cost calculation according to documentation:
   * - FA (Frais d'Approche) = driver.approachFee (already calculated: distance × 0.500 TND/km)
   * - CC_estimé = 5.00 TND + (trip_distance × 2.50 TND/km)
   * - Total Estimé = FA + CC_estimé
   */
  const selectDriverForBooking = (driver) => {
    console.log('Driver selected:', driver.name)
    selectedDriver.value = driver
    
    // Validate location data
    if (!userLocation?.value?.lat || !userLocation?.value?.lng || 
        !destination?.value?.lat || !destination?.value?.lng) {
      console.warn('⚠️ Missing location coordinates, showing approach fee only')
      estimatedCost.value = {
        approachFee: driver.approachFee,
        meterEstimate: 0,
        totalEstimate: driver.approachFee,
        tripDistance: 0,
        approachDistance: driver.distance
      }
      return
    }
    
    // Calculate trip distance (pickup to destination)
    const tripDistance = calculateDistance(
      userLocation.value.lat,
      userLocation.value.lng,
      destination.value.lat,
      destination.value.lng
    )
    
    // FA (Frais d'Approche) - already calculated in driver.approachFee
    // Formula: driver_distance_to_pickup × 0.500 TND/km
    const approachFee = driver.approachFee
    
    // CC_estimé (Coût de la Course estimé) - Meter-based estimate
    // Formula: 5.00 TND (base) + (trip_distance × 2.50 TND/km)
    const baseFare = 5.0  // TND base fare
    const ratePerKm = 2.5  // TND per km
    const meterEstimate = baseFare + (tripDistance * ratePerKm)
    
    // Total Estimé = FA + CC_estimé
    const totalEstimate = approachFee + meterEstimate
    
    estimatedCost.value = {
      approachFee: parseFloat(approachFee.toFixed(3)),
      meterEstimate: parseFloat(meterEstimate.toFixed(3)),
      totalEstimate: parseFloat(totalEstimate.toFixed(3)),
      tripDistance: parseFloat(tripDistance.toFixed(2)),
      approachDistance: driver.distance
    }
    
    console.log('💰 Cost breakdown (Documentation formula):', {
      approachDistance: driver.distance.toFixed(2) + ' km',
      approachFee: approachFee.toFixed(3) + ' TND (FA)',
      tripDistance: tripDistance.toFixed(2) + ' km',
      meterEstimate: meterEstimate.toFixed(3) + ' TND (CC_estimé)',
      totalEstimate: totalEstimate.toFixed(3) + ' TND'
    })
  }

  /**
   * Select and confirm driver with double-click
   * Uses same cost calculation as selectDriverForBooking
   */
  const selectAndConfirmDriver = (driver, confirmCallback) => {
    console.log('Double-click detected on driver:', driver.name)
    selectedDriver.value = driver
    
    // Validate location data
    if (!userLocation?.value?.lat || !userLocation?.value?.lng || 
        !destination?.value?.lat || !destination?.value?.lng) {
      console.warn('⚠️ Missing location coordinates, showing approach fee only')
      estimatedCost.value = {
        approachFee: driver.approachFee,
        meterEstimate: 0,
        totalEstimate: driver.approachFee,
        tripDistance: 0,
        approachDistance: driver.distance
      }
      setTimeout(() => {
        console.log('Confirming driver selection...')
        if (confirmCallback) confirmCallback()
      }, 0)
      return
    }
    
    // Calculate trip distance (pickup to destination)
    const tripDistance = calculateDistance(
      userLocation.value.lat,
      userLocation.value.lng,
      destination.value.lat,
      destination.value.lng
    )
    
    // Cost calculation per documentation
    const approachFee = driver.approachFee
    const baseFare = 5.0
    const ratePerKm = 2.5
    const meterEstimate = baseFare + (tripDistance * ratePerKm)
    const totalEstimate = approachFee + meterEstimate
    
    estimatedCost.value = {
      approachFee: parseFloat(approachFee.toFixed(3)),
      meterEstimate: parseFloat(meterEstimate.toFixed(3)),
      totalEstimate: parseFloat(totalEstimate.toFixed(3)),
      tripDistance: parseFloat(tripDistance.toFixed(2)),
      approachDistance: driver.distance
    }
    
    setTimeout(() => {
      console.log('Confirming driver selection...')
      if (confirmCallback) confirmCallback()
    }, 0)
  }

  /**
   * Find available drivers
   */
  const findDriver = (showBottomSheetCallback) => {
    tripState.value = 'select-driver'
    if (showBottomSheetCallback) showBottomSheetCallback(true)
  }

  /**
   * Cancel driver selection
   */
  const cancelDriverSelection = () => {
    tripState.value = 'search'
    selectedDriver.value = null
  }

  /**
   * Check for active trip on load
   * Syncs frontend state with backend trip status
   */
  const checkActiveTrip = async () => {
    try {
      console.log('🔍 Checking for active trip...')
      const response = await riderAPI.getActiveTrip()

      if (response.has_active_trip && response.trip) {
        console.log('✅ Active trip found:', response.trip)
        activeTrip.value = response.trip
        
        // Map backend status to frontend state
        tripState.value = mapBackendStatusToFrontendState(response.trip.status)
        tripStatus.value = mapBackendStatusToDisplayText(response.trip.status)
        
        // If trip has driver info, set selected driver
        if (response.trip.driver) {
          selectedDriver.value = {
            id: response.trip.driver_id,
            name: response.trip.driver.name,
            taxiNumber: response.trip.driver.taxi_number,
            phone: response.trip.driver.phone_number,
            status: response.trip.driver.status
          }
        }
        
        // Store trip data to restore UI state
        if (typeof window !== 'undefined') {
          window.restoreTripState = {
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
            driver: response.trip.driver,
            estimatedCost: response.trip.estimated_cost_tnd
          }
        }
        
        return true
      } else {
        console.log('ℹ️ No active trip found')
        activeTrip.value = null
        if (typeof window !== 'undefined') {
          delete window.restoreTripState
        }
        return false
      }
    } catch (error) {
      console.error('❌ Error checking active trip:', error)
      return false
    }
  }

  /**
   * Create trip request via API with proper status mapping
   * 
   * @param {Object} pickupLocation - { lat, lng }
   * @param {Object} destinationCoords - { lat, lng }
   * @param {String} destinationAddress - Optional destination address
   * @param {Object} options - Optional { pickupAddress, riderNotes, tripType }
   */
  const requestRide = async (pickupLocation, destinationCoords, destinationAddress = null, options = {}) => {
    // Validate required fields
    if (!pickupLocation || !pickupLocation.lat || !pickupLocation.lng) {
      console.error('❌ Missing pickup location')
      return { success: false, error: 'Pickup location is required' }
    }

    if (!destinationCoords || !destinationCoords.lat || !destinationCoords.lng) {
      console.error('❌ Missing destination coordinates')
      return { success: false, error: 'Destination is required' }
    }

    try {
      // Set temporary state while creating trip
      tripState.value = 'requested'
      tripStatus.value = 'Creating Trip...'

      // Build trip request with all fields
      const tripRequest = {
        pickup_latitude: pickupLocation.lat,
        pickup_longitude: pickupLocation.lng,
        destination_latitude: destinationCoords.lat,
        destination_longitude: destinationCoords.lng,
        // Optional fields with fallbacks
        pickup_address: options.pickupAddress || 
                       `${pickupLocation.lat.toFixed(4)}, ${pickupLocation.lng.toFixed(4)}`,
        destination_address: destinationAddress || 
                           `${destinationCoords.lat.toFixed(4)}, ${destinationCoords.lng.toFixed(4)}`,
        rider_notes: options.riderNotes || null,
        trip_type: options.tripType || 'regular'  // regular, express, scheduled
      }

      console.log('📤 Creating trip request:', {
        ...tripRequest,
        pickup: `${tripRequest.pickup_latitude}, ${tripRequest.pickup_longitude}`,
        destination: `${tripRequest.destination_latitude}, ${tripRequest.destination_longitude}`,
        type: tripRequest.trip_type,
        driver_id: selectedDriver.value?.id || 'auto-assign'
      })

      const response = await riderAPI.createTrip(
        tripRequest.pickup_latitude,
        tripRequest.pickup_longitude,
        tripRequest.destination_latitude,
        tripRequest.destination_longitude,
        tripRequest.pickup_address,
        tripRequest.destination_address,
        tripRequest.rider_notes,
        selectedDriver.value?.id  // Pass selected driver ID to backend
      )

      console.log('📥 Backend response:', JSON.stringify(response, null, 2))
      
      if (response.success && response.trip) {
        console.log('✅ Trip created successfully:', response.trip)
        console.log('📊 Trip status from backend:', response.trip.status)
        
        // Store active trip with addresses
        activeTrip.value = {
          ...response.trip,
          // Ensure addresses from backend or request are available
          pickup_address: response.trip.pickup_address || trip_request.pickup_address || 'Pickup location',
          destination_address: response.trip.destination_address || trip_request.destination_address || 'Destination'
        }
        
        console.log('📍 Trip addresses:', {
          pickup: activeTrip.value.pickup_address,
          destination: activeTrip.value.destination_address
        })
        
        // Map backend status to frontend state
        const newState = mapBackendStatusToFrontendState(response.trip.status)
        const newStatusText = mapBackendStatusToDisplayText(response.trip.status)
        
        console.log(`🔄 Mapping: "${response.trip.status}" -> state: "${newState}", text: "${newStatusText}"`)
        
        tripState.value = newState
        tripStatus.value = newStatusText
        
        // No driver is assigned yet - trip is waiting for driver acceptance
        // Clear selected driver and show waiting state
        console.log('⏳ Trip created, waiting for driver to accept...')
        selectedDriver.value = null
        
        return { success: true, trip: response.trip }
      } else {
        console.error('❌ Failed to create trip - Backend response:', {
          success: response.success,
          message: response.message,
          error: response.error,
          fullResponse: response
        })
        console.error('❌ Response keys:', Object.keys(response))
        console.error('❌ Response type:', typeof response)
        console.error('❌ Full response stringified:', JSON.stringify(response, null, 2))
        
        // If there's an active trip, return it in the error response
        if (response.active_trip) {
          console.log('ℹ️ User has existing active trip:', response.active_trip)
          // Set the active trip so UI can display it
          activeTrip.value = response.active_trip
          tripState.value = mapBackendStatusToFrontendState(response.active_trip.status)
          tripStatus.value = mapBackendStatusToDisplayText(response.active_trip.status)
          
          return { 
            success: false, 
            error: response.message || 'You have an active trip',
            hasActiveTrip: true,
            activeTrip: response.active_trip
          }
        }
        
        tripState.value = 'select-driver'
        tripStatus.value = 'Assigned'
        return { success: false, error: response.message || 'Failed to create trip' }
      }
    } catch (error) {
      console.error('❌ Error creating trip - Full error object:', error)
      console.error('❌ Error message:', error.message)
      console.error('❌ Error response:', error.response?.data)
      
      tripState.value = 'select-driver'
      tripStatus.value = 'Assigned'
      
      // Extract meaningful error message
      const errorMsg = error.response?.data?.detail || 
                      error.response?.data?.message || 
                      error.message || 
                      'Failed to create trip'
      
      return { success: false, error: errorMsg }
    }
  }

  /**
   * Poll for trip status updates
   * Call this periodically when trip is active to sync with backend
   */
  const refreshTripStatus = async () => {
    if (!activeTrip.value) {
      console.log('⏭️ refreshTripStatus: No active trip, skipping')
      return
    }

    console.log(`🔄 refreshTripStatus: Checking trip ${activeTrip.value.id} status...`)
    
    try {
      const response = await riderAPI.getActiveTrip()
      
      if (response.has_active_trip && response.trip) {
        const oldStatus = activeTrip.value.status
        const newStatus = response.trip.status
        
        console.log(`📊 Trip status: ${oldStatus} → ${newStatus}`)
        
        if (oldStatus !== newStatus) {
          console.log(`🔄 Trip status changed: ${oldStatus} → ${newStatus}`)
          
          // Handle cancellation
          if (newStatus === 'cancelled') {
            console.log('🚫 Trip was cancelled')
            const reason = response.trip.cancellation_reason || 'No reason provided'
            console.log(`Cancellation reason: ${reason}`)
            
            // Add to notification panel
            if (reason.includes('Driver declined')) {
              notifyDriverDeclined(response.trip.driver?.name || 'Driver')
            } else if (reason.includes('No available drivers')) {
              notifyNoDriversAvailable()
            } else {
              notifyTripCancelled(
                response.trip.destination_address,
                reason.includes('You') || reason.includes('Rider') ? 'rider' : 'driver',
                'rider'
              )
            }
            
            // Show notification to user with more specific message
            if (typeof window !== 'undefined' && window.displayToast) {
              if (reason.includes('Driver declined')) {
                window.displayToast(`Driver declined your trip request. You can select another driver.`, 'warning')
              } else if (reason.includes('No available drivers')) {
                window.displayToast(`No available drivers found. Please try again.`, 'warning')
              } else {
                window.displayToast(`Trip cancelled: ${reason}`, 'error')
              }
            }
            
            // Reset state and trigger driver list refresh
            activeTrip.value = null
            tripState.value = 'select-driver' // Go back to driver selection
            selectedDriver.value = null
            
            // Clear all routes and markers from map
            if (typeof window !== 'undefined') {
              if (window.clearAllRoutesAndMarkers) {
                console.log('🗺️ Clearing all routes and markers from map')
                window.clearAllRoutesAndMarkers()
              }
              
              // Trigger driver list refresh if callback exists
              if (window.refreshDriverList) {
                console.log('🔄 Triggering driver list refresh after cancellation')
                window.refreshDriverList()
              }
            }
            return
          }
          
          activeTrip.value = response.trip
          tripState.value = mapBackendStatusToFrontendState(newStatus)
          tripStatus.value = mapBackendStatusToDisplayText(newStatus)
          
          // Update driver info when trip transitions from requested to assigned
          if (response.trip.driver && !selectedDriver.value) {
            console.log('✅ Driver accepted trip:', response.trip.driver.name)
            selectedDriver.value = {
              id: response.trip.driver_id,
              name: response.trip.driver.name,
              taxiNumber: response.trip.driver.taxi_number,
              status: response.trip.driver.status
            }
            
            // Add notification
            notifyTripAccepted(response.trip.driver.name)
          }
          
          // Notify when driver arrives
          if (newStatus === 'accepted' && oldStatus === 'assigned') {
            notifyDriverArrived()
          }
          
          // Notify when trip starts
          if (newStatus === 'started' && oldStatus !== 'started') {
            notifyTripStarted()
          }
          
          // Notify when trip completes
          if (newStatus === 'completed' && oldStatus !== 'completed') {
            notifyTripCompleted(
              response.trip.estimated_cost_tnd?.toFixed(2) || '0.00',
              'TND',
              'rider'
            )
          }
          
          // Detect driver reassignment
          if (response.trip.driver && selectedDriver.value && 
              response.trip.driver_id !== selectedDriver.value.id) {
            console.log('🔄 Driver was reassigned')
            console.log(`Old driver: ${selectedDriver.value.name}`)
            console.log(`New driver: ${response.trip.driver.name}`)
            
            const oldDriverName = selectedDriver.value.name
            
            selectedDriver.value = {
              id: response.trip.driver_id,
              name: response.trip.driver.name,
              taxiNumber: response.trip.driver.taxi_number,
              status: response.trip.driver.status
            }
            
            if (typeof window !== 'undefined' && window.displayToast) {
              window.displayToast(`Previous driver declined. New driver assigned: ${response.trip.driver.name}`, 'info')
            }
          }
        }
      } else {
        // Trip no longer active (might be cancelled)
        console.log('ℹ️ Trip is no longer active')
        if (activeTrip.value && activeTrip.value.status !== 'cancelled') {
          console.log('⚠️ Trip disappeared unexpectedly')
        }
        activeTrip.value = null
        tripState.value = 'search'
        selectedDriver.value = null
      }
    } catch (error) {
      // Silently handle network errors during trip transitions
      // Only log as error if there's an active trip in a stable state
      if (activeTrip.value && 
          activeTrip.value.status !== 'cancelled' && 
          activeTrip.value.status !== 'completed' &&
          !error.message.includes('Network error')) {
        console.error('❌ Error refreshing trip status:', error)
      }
      // Suppress network errors - they're expected during transitions
    }
  }

  /**
   * Confirm trip completion by rider
   */
  const confirmCompletion = async () => {
    if (!activeTrip.value) {
      console.warn('No active trip to confirm completion')
      return { success: false, error: 'No active trip' }
    }

    try {
      console.log(`✅ Confirming completion for trip ${activeTrip.value.id}`)
      
      const response = await riderAPI.confirmCompletion(activeTrip.value.id)
      
      if (response && response.success) {
        // Update local trip data
        if (activeTrip.value) {
          activeTrip.value.rider_confirmed_completion = true
          activeTrip.value.rider_confirmed_completion_at = new Date().toISOString()
        }
        
        console.log('✅ Trip completion confirmed successfully')
        return { success: true }
      } else {
        throw new Error(response?.message || 'Failed to confirm completion')
      }
    } catch (error) {
      console.error('❌ Error confirming completion:', error)
      return { success: false, error: error.message }
    }
  }

  /**
   * Confirm pickup - rider confirms driver has arrived
   */
  const confirmPickup = async () => {
    if (!activeTrip.value) {
      console.error('No active trip to confirm')
      throw new Error('No active trip')
    }

    try {
      console.log('✅ Confirming pickup for trip:', activeTrip.value.id)
      const response = await riderAPI.confirmPickup(activeTrip.value.id)
      
      if (response.success) {
        console.log('✅ Pickup confirmed successfully - Waiting for driver to start trip')
        // Update local trip data - status stays "accepted" until driver starts
        if (activeTrip.value && response.trip) {
          activeTrip.value.rider_confirmed_pickup = true
          activeTrip.value.rider_confirmed_at = response.trip.rider_confirmed_at
          // Status remains "accepted" - driver must manually start trip
          console.log('⏳ Trip status: accepted (waiting for driver to start)')
        }
        return response
      } else {
        throw new Error(response.message || 'Failed to confirm pickup')
      }
    } catch (error) {
      console.error('❌ Failed to confirm pickup:', error)
      throw error
    }
  }

  /**
   * Cancel active trip
   */
  const cancelTrip = async (reason = null) => {
    if (!activeTrip.value) {
      console.warn('No active trip to cancel')
      return { success: false, error: 'No active trip' }
    }

    try {
      console.log(`🚫 Cancelling trip ${activeTrip.value.id}`, reason ? `Reason: ${reason}` : '')
      
      // Call backend API to cancel trip
      const response = await riderAPI.cancelTrip(activeTrip.value.id, reason)
      
      if (response && response.success) {
        // Reset state after successful cancellation
        activeTrip.value = null
        tripState.value = 'search'
        tripStatus.value = 'Assigned'
        selectedDriver.value = null
        
        console.log('✅ Trip cancelled successfully')
        return { success: true }
      } else {
        throw new Error(response?.message || 'Failed to cancel trip')
      }
    } catch (error) {
      console.error('❌ Error cancelling trip:', error)
      return { success: false, error: error.message }
    }
  }

  /**
   * Complete trip with rating
   * Submit rating after trip completion
   */
  const completeTripRating = async (ratingValue, reviewText) => {
    if (!activeTrip.value) {
      console.warn('No active trip to rate')
      return { success: false, error: 'No active trip' }
    }

    if (!ratingValue || ratingValue < 1 || ratingValue > 5) {
      return { success: false, error: 'Please provide a rating between 1 and 5 stars' }
    }

    try {
      console.log(`⭐ Submitting rating for trip ${activeTrip.value.id}:`, ratingValue, 'stars')
      if (reviewText) {
        console.log('📝 Review:', reviewText)
      }
      
      // Call backend API to rate trip
      const response = await riderAPI.rateTrip(
        activeTrip.value.id,
        ratingValue,
        reviewText || null
      )
      
      if (response && response.success) {
        // Reset state after successful rating
        activeTrip.value = null
        tripState.value = 'search'
        rating.value = 0
        review.value = ''
        selectedDriver.value = null
        
        console.log('✅ Rating submitted successfully')
        return { success: true }
      } else {
        throw new Error(response?.message || 'Failed to submit rating')
      }
    } catch (error) {
      console.error('❌ Error submitting rating:', error)
      return { success: false, error: error.message }
    }
  }

  return {
    // State
    tripState,
    tripStatus,
    selectedDriver,
    estimatedCost,
    rating,
    review,
    activeTrip,
    nearbyDrivers,
    loadingDrivers,
    driversError,
    tripSummary,

    // Methods
    fetchNearbyDrivers,
    checkActiveTrip,
    mapBackendStatusToFrontendState,
    mapBackendStatusToDisplayText,
    refreshTripStatus,
    selectDriverForTrip,
    selectDriverForBooking,
    selectAndConfirmDriver,
    findDriver,
    cancelDriverSelection,
    requestRide,
    confirmPickup,
    cancelTrip,
    confirmCompletion,
    completeTripRating
  }
}
