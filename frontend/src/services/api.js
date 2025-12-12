import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

// Cache token to avoid repeated localStorage reads
let cachedToken = localStorage.getItem('taxini_token')

// Update cached token when it changes
const updateCachedToken = (token) => {
  cachedToken = token
  if (token) {
    localStorage.setItem('taxini_token', token)
  } else {
    localStorage.removeItem('taxini_token')
  }
}

// Validate API key is configured
const API_KEY = import.meta.env.VITE_API_KEY
if (!API_KEY) {
  console.error('⚠️ VITE_API_KEY is not configured! API requests will fail.')
}

// Create axios instance with performance optimizations
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000, // 15 second timeout
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
    // Note: Accept-Encoding is automatically handled by the browser
  },
  // Enable HTTP compression (browser handles this automatically)
  decompress: true,
  // Validate status to handle all error codes
  validateStatus: (status) => status < 500 // Reject only if server error
})

// Request interceptor - Add auth token (using cached value)
apiClient.interceptors.request.use(
  (config) => {
    if (cachedToken) {
      config.headers.Authorization = `Bearer ${cachedToken}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) {
      // Handle 401 Unauthorized (token expired)
      if (error.response.status === 401) {
        console.error('🔒 Token expired or invalid - logging out')
        // Clear auth data
        updateCachedToken(null)
        localStorage.removeItem('taxini_user')
        // Redirect to login
        window.location.href = '/login'
        return Promise.reject(new Error('Session expired. Please login again.'))
      }
      
      // Server responded with error
      const message = error.response.data?.detail || error.response.data?.message || 'An error occurred'
      return Promise.reject(new Error(message))
    } else if (error.request) {
      // Request made but no response
      return Promise.reject(new Error('Network error. Please check your connection.'))
    } else {
      // Something else happened
      return Promise.reject(new Error(error.message || 'An error occurred'))
    }
  }
)

// =============================================================================
// LOCATION API
// =============================================================================

export const locationAPI = {
  // Get nearby drivers
  getNearbyDrivers: (latitude, longitude) => 
    apiClient.get('/locations/drivers', { params: { latitude, longitude } }),

  // Update user location
  updateLocation: (userId, latitude, longitude, role = 'driver') =>
    apiClient.post(`/locations/update/${userId}`, { latitude, longitude, role }),

  // Get user location
  getUserLocation: (userId) => 
    apiClient.get(`/locations/user/${userId}`)
}

// =============================================================================
// RIDER API
// =============================================================================

export const riderAPI = {
  // Command a course - find nearest driver
  commandCourse: (riderLat, riderLng, destinationLat, destinationLng) =>
    apiClient.post('/riders/command-course', {
      rider_lat: riderLat,
      rider_lng: riderLng,
      destination_lat: destinationLat,
      destination_lng: destinationLng
    }),

  // Create a trip
  createTrip: (pickupLat, pickupLng, destLat, destLng, pickupAddress = null, destAddress = null, notes = null, driverId = null) =>
    apiClient.post('/riders/create-trip', {
      pickup_latitude: pickupLat,
      pickup_longitude: pickupLng,
      destination_latitude: destLat,
      destination_longitude: destLng,
      pickup_address: pickupAddress,
      destination_address: destAddress,
      rider_notes: notes,
      trip_type: 'regular',
      driver_id: driverId  // Selected driver ID from user
    }),

  // Get active trip
  getActiveTrip: () => apiClient.get('/riders/active-trip'),

  // Get trip history
  getTripHistory: (limit = 10, offset = 0) =>
    apiClient.get('/riders/trip-history', { params: { limit, offset } }),

  // Confirm pickup - rider confirms driver has arrived
  confirmPickup: (tripId) =>
    apiClient.post(`/riders/trips/${tripId}/confirm-pickup`),

  // Cancel trip
  cancelTrip: (tripId, reason = null) =>
    apiClient.post(`/riders/trips/${tripId}/cancel`, { reason }),

  // Confirm trip completion
  confirmCompletion: (tripId) =>
    apiClient.post(`/riders/trips/${tripId}/confirm-completion`),

  // Rate trip
  rateTrip: (tripId, rating, comment = null) =>
    apiClient.post(`/riders/trips/${tripId}/rate`, null, { params: { rating, comment } })
}

// =============================================================================
// DRIVER API
// =============================================================================

export const driverAPI = {
  // Get driver profile (includes account_status)
  getDriverProfile: () => apiClient.get('/drivers/me'),

  // Update driver status
  updateStatus: (status) => apiClient.put('/drivers/status', { status }),

  // Get driver status
  getStatus: () => apiClient.get('/drivers/status'),

  // Start GPS streaming
  startStreaming: () => apiClient.post('/drivers/streaming/start'),

  // Stop GPS streaming
  stopStreaming: () => apiClient.post('/drivers/streaming/stop'),

  // Accept trip
  acceptTrip: (tripId, notes = null) =>
    apiClient.post('/drivers/trip-action', { action: 'accept', trip_id: tripId, notes }),

  // Reject trip
  rejectTrip: (tripId, notes = null) =>
    apiClient.post('/drivers/trip-action', { action: 'reject', trip_id: tripId, notes }),

  // Update trip status
  updateTripStatus: (tripId, status, notes = null) =>
    apiClient.put('/drivers/trip-status', { trip_id: tripId, status, notes }),

  // Get active trip
  getActiveTrip: () => apiClient.get('/drivers/active-trip'),

  // Get pending trip requests assigned to this driver
  getPendingTripRequests: () => apiClient.get('/drivers/pending-requests'),

  // Get trip history
  getTripHistory: (limit = 10, offset = 0, status = null) =>
    apiClient.get('/drivers/trip-history', { params: { limit, offset, ...(status && { status }) } }),

  // Get driver earnings
  getEarnings: (period = 'week') =>
    apiClient.get('/drivers/earnings', { params: { period } })
}

// =============================================================================
// TICKETS API (Support System)
// =============================================================================

export const ticketAPI = {
  // Create a new support ticket
  createTicket: (ticketData) => 
    apiClient.post('/tickets', ticketData),
  
  // Get user's tickets
  getTickets: (params = {}) => 
    apiClient.get('/tickets', { params }),
  
  // Get specific ticket by ID
  getTicket: (ticketId) => 
    apiClient.get(`/tickets/${ticketId}`),
  
  // Update ticket (e.g., close ticket, add comment)
  updateTicket: (ticketId, updateData) => 
    apiClient.patch(`/tickets/${ticketId}`, updateData)
}

// Export token cache updater for auth store
export { updateCachedToken }

export default apiClient
