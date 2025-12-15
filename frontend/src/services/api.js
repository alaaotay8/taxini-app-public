/**
 * API Service
 * 
 * Centralized API client using Axios for all backend communication.
 * Handles authentication via HttpOnly cookies and API key validation.
 * 
 * Features:
 * - Automatic cookie handling (HttpOnly JWT tokens)
 * - API key authentication via X-API-Key header
 * - Request/response interceptors for error handling
 * - 15-second timeout for all requests
 * - Automatic error message extraction
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

// Validate API key is configured
const API_KEY = import.meta.env.VITE_API_KEY
if (!API_KEY) {
  console.error('⚠️ VITE_API_KEY is not configured! API requests will fail.')
}

/**
 * Axios instance configured for Taxini API
 * - withCredentials: true enables HttpOnly cookie handling
 * - X-API-Key header required by backend for all requests
 * - validateStatus: Accept all responses < 500 (handle 4xx in interceptor)
 */
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
  },
  decompress: true,
  validateStatus: (status) => status < 500
})

// Request interceptor (currently pass-through, can add logging if needed)
apiClient.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
)

/**
 * Response interceptor
 * Extracts data from successful responses and handles errors uniformly.
 * 
 * Error handling:
 * - 401: Authentication required (let app handle redirect)
 * - 4xx: Extract error message from response
 * - Network errors: Return generic network error message
 */
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) {
      if (error.response.status === 401) {
        return Promise.reject(error)
      }
      const message = error.response.data?.detail || error.response.data?.message || 'An error occurred'
      return Promise.reject(new Error(message))
    } else if (error.request) {
      return Promise.reject(new Error('Network error. Please check your connection.'))
    } else {
      return Promise.reject(new Error(error.message || 'An error occurred'))
    }
  }
)

// =============================================================================
// LOCATION API - Real-time location tracking and driver discovery
// =============================================================================

export const locationAPI = {
  /**
   * Get nearby online drivers within radius
   * @param {number} latitude - Rider's current latitude
   * @param {number} longitude - Rider's current longitude
   * @returns {Promise} List of nearby drivers with distance
   */
  getNearbyDrivers: (latitude, longitude) => 
    apiClient.get('/locations/drivers', { params: { latitude, longitude } }),

  /**
   * Update user's current location (for real-time tracking)
   * @param {string} userId - User ID
   * @param {number} latitude - Current latitude
   * @param {number} longitude - Current longitude
   * @param {string} role - User role (driver/rider)
   * @returns {Promise} Update confirmation
   */
  updateLocation: (userId, latitude, longitude, role = 'driver') =>
    apiClient.post(`/locations/update/${userId}`, { latitude, longitude, role }),

  /**
   * Get user's last known location
   * @param {string} userId - User ID to lookup
   * @returns {Promise} Location data
   */
  getUserLocation: (userId) => 
    apiClient.get(`/locations/user/${userId}`)
}

// =============================================================================
// RIDER API - Trip creation and management for riders
// =============================================================================

export const riderAPI = {
  /**
   * Command a course - Legacy endpoint for finding nearest driver
   * @deprecated Use createTrip with driverId instead
   */
  commandCourse: (riderLat, riderLng, destinationLat, destinationLng) =>
    apiClient.post('/riders/command-course', {
      rider_lat: riderLat,
      rider_lng: riderLng,
      destination_lat: destinationLat,
      destination_lng: destinationLng
    }),

  /**
   * Create a new trip request
   * @param {number} pickupLat - Pickup location latitude
   * @param {number} pickupLng - Pickup location longitude
   * @param {number} destLat - Destination latitude
   * @param {number} destLng - Destination longitude
   * @param {string} pickupAddress - Human-readable pickup address
   * @param {string} destAddress - Human-readable destination address
   * @param {string} notes - Optional rider notes for driver
   * @param {string} driverId - Selected driver ID (null for auto-assignment)
   * @returns {Promise} Created trip data
   */
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
      driver_id: driverId
    }),

  /**
   * Get rider's current active trip (if any)
   * @returns {Promise} Active trip data or null
   */
  getActiveTrip: () => apiClient.get('/riders/active-trip'),

  /**
   * Get rider's trip history with pagination
   * @param {number} limit - Number of trips to return
   * @param {number} offset - Number of trips to skip
   * @returns {Promise} List of past trips
   */
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
  rateTrip: (tripId, rating, comment = null) => {
    const params = { rating }
    if (comment) {
      params.comment = comment
    }
    return apiClient.post(`/riders/trips/${tripId}/rate`, null, { params })
  }
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

// =============================================================================
// USER API (Profile Management)
// =============================================================================

export const userAPI = {
  // Update user profile
  updateProfile: (profileData) =>
    apiClient.post('/users/update-profile', profileData)
}

export default apiClient
