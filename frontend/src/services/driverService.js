import { driverAPI } from './api'

const driverService = {
  /**
   * Get driver earnings for a specific period
   * @param {string} period - 'week' or 'month'
   * @returns {Promise} - Promise resolving to earnings data
   */
  async getEarnings(period = 'week') {
    try {
      const response = await driverAPI.getEarnings(period)
      return {
        success: true,
        data: response
      }
    } catch (error) {
      console.error('Failed to fetch earnings:', error)
      return {
        success: false,
        error: error.message,
        data: null
      }
    }
  },

  /**
   * Get driver trip history
   * @param {number} limit - Number of trips per page
   * @param {number} offset - Pagination offset
   * @param {string} status - Filter by trip status (optional)
   * @returns {Promise} - Promise resolving to trip history data
   */
  async getTripHistory(limit = 20, offset = 0, status = null) {
    try {
      const response = await driverAPI.getTripHistory(limit, offset, status)
      return {
        success: true,
        trips: response.trips || [],
        total: response.total || 0
      }
    } catch (error) {
      console.error('Failed to fetch driver trip history:', error)
      return {
        success: false,
        trips: [],
        error: error.message
      }
    }
  },

  /**
   * Get driver profile
   * @returns {Promise} - Promise resolving to driver profile
   */
  async getProfile() {
    try {
      const response = await driverAPI.getDriverProfile()
      return {
        success: true,
        driver: response
      }
    } catch (error) {
      console.error('Failed to fetch driver profile:', error)
      return {
        success: false,
        error: error.message
      }
    }
  },

  /**
   * Update driver status (online/offline)
   * @param {string} status - 'online' or 'offline'
   * @returns {Promise} - Promise resolving to status update result
   */
  async updateStatus(status) {
    try {
      const response = await driverAPI.updateStatus(status)
      return {
        success: true,
        message: response.message
      }
    } catch (error) {
      console.error('Failed to update driver status:', error)
      return {
        success: false,
        error: error.message
      }
    }
  },

  /**
   * Get driver current status
   * @returns {Promise} - Promise resolving to driver status
   */
  async getStatus() {
    try {
      const response = await driverAPI.getStatus()
      return {
        success: true,
        status: response.status
      }
    } catch (error) {
      console.error('Failed to fetch driver status:', error)
      return {
        success: false,
        error: error.message
      }
    }
  },

  /**
   * Start GPS streaming
   * @returns {Promise} - Promise resolving to streaming start result
   */
  async startStreaming() {
    try {
      const response = await driverAPI.startStreaming()
      return {
        success: true,
        message: response.message
      }
    } catch (error) {
      console.error('Failed to start GPS streaming:', error)
      return {
        success: false,
        error: error.message
      }
    }
  },

  /**
   * Stop GPS streaming
   * @returns {Promise} - Promise resolving to streaming stop result
   */
  async stopStreaming() {
    try {
      const response = await driverAPI.stopStreaming()
      return {
        success: true,
        message: response.message
      }
    } catch (error) {
      console.error('Failed to stop GPS streaming:', error)
      return {
        success: false,
        error: error.message
      }
    }
  },

  /**
   * Accept trip
   * @param {number} tripId - Trip ID
   * @param {string} notes - Optional notes
   * @returns {Promise} - Promise resolving to accept result
   */
  async acceptTrip(tripId, notes = null) {
    try {
      const response = await driverAPI.acceptTrip(tripId, notes)
      return {
        success: true,
        message: response.message
      }
    } catch (error) {
      console.error('Failed to accept trip:', error)
      return {
        success: false,
        error: error.message
      }
    }
  },

  /**
   * Reject trip
   * @param {number} tripId - Trip ID
   * @param {string} notes - Optional notes
   * @returns {Promise} - Promise resolving to reject result
   */
  async rejectTrip(tripId, notes = null) {
    try {
      const response = await driverAPI.rejectTrip(tripId, notes)
      return {
        success: true,
        message: response.message
      }
    } catch (error) {
      console.error('Failed to reject trip:', error)
      return {
        success: false,
        error: error.message
      }
    }
  },

  /**
   * Update trip status
   * @param {number} tripId - Trip ID
   * @param {string} status - New status
   * @param {string} notes - Optional notes
   * @returns {Promise} - Promise resolving to update result
   */
  async updateTripStatus(tripId, status, notes = null) {
    try {
      const response = await driverAPI.updateTripStatus(tripId, status, notes)
      return {
        success: true,
        message: response.message
      }
    } catch (error) {
      console.error('Failed to update trip status:', error)
      return {
        success: false,
        error: error.message
      }
    }
  },

  /**
   * Get active trip
   * @returns {Promise} - Promise resolving to active trip
   */
  async getActiveTrip() {
    try {
      const response = await driverAPI.getActiveTrip()
      return {
        success: true,
        trip: response
      }
    } catch (error) {
      console.error('Failed to fetch active trip:', error)
      return {
        success: false,
        error: error.message
      }
    }
  },

  /**
   * Get pending trip requests
   * @returns {Promise} - Promise resolving to pending trips
   */
  async getPendingTripRequests() {
    try {
      const response = await driverAPI.getPendingTripRequests()
      return {
        success: true,
        trips: response.trips || []
      }
    } catch (error) {
      console.error('Failed to fetch pending trips:', error)
      return {
        success: false,
        trips: [],
        error: error.message
      }
    }
  }
}

export default driverService
