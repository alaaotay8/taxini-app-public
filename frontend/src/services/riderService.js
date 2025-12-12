import { riderAPI } from './api'

const riderService = {
  /**
   * Get rider's trip history
   * @param {number} limit - Number of trips per page
   * @param {number} offset - Pagination offset
   * @returns {Promise} - Promise resolving to trip history data
   */
  async getTripHistory(limit = 20, offset = 0) {
    try {
      const response = await riderAPI.getTripHistory(limit, offset)
      return {
        success: true,
        trips: response.trips || [],
        total: response.total || 0
      }
    } catch (error) {
      console.error('Failed to fetch rider trip history:', error)
      return {
        success: false,
        trips: [],
        error: error.message
      }
    }
  },

  /**
   * Create a new trip
   * @param {object} tripData - Trip details
   * @returns {Promise} - Promise resolving to created trip
   */
  async createTrip(tripData) {
    try {
      const response = await riderAPI.createTrip(
        tripData.pickupLat,
        tripData.pickupLng,
        tripData.destLat,
        tripData.destLng,
        tripData.pickupAddress,
        tripData.destAddress,
        tripData.notes,
        tripData.driverId
      )
      return {
        success: true,
        trip: response
      }
    } catch (error) {
      console.error('Failed to create trip:', error)
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
      const response = await riderAPI.getActiveTrip()
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
   * Cancel trip
   * @param {number} tripId - Trip ID
   * @param {string} reason - Cancellation reason
   * @returns {Promise} - Promise resolving to cancellation result
   */
  async cancelTrip(tripId, reason = null) {
    try {
      const response = await riderAPI.cancelTrip(tripId, reason)
      return {
        success: true,
        message: response.message
      }
    } catch (error) {
      console.error('Failed to cancel trip:', error)
      return {
        success: false,
        error: error.message
      }
    }
  },

  /**
   * Confirm pickup
   * @param {number} tripId - Trip ID
   * @returns {Promise} - Promise resolving to confirmation result
   */
  async confirmPickup(tripId) {
    try {
      const response = await riderAPI.confirmPickup(tripId)
      return {
        success: true,
        message: response.message
      }
    } catch (error) {
      console.error('Failed to confirm pickup:', error)
      return {
        success: false,
        error: error.message
      }
    }
  },

  /**
   * Confirm trip completion
   * @param {number} tripId - Trip ID
   * @returns {Promise} - Promise resolving to confirmation result
   */
  async confirmCompletion(tripId) {
    try {
      const response = await riderAPI.confirmCompletion(tripId)
      return {
        success: true,
        message: response.message
      }
    } catch (error) {
      console.error('Failed to confirm completion:', error)
      return {
        success: false,
        error: error.message
      }
    }
  },

  /**
   * Rate trip
   * @param {number} tripId - Trip ID
   * @param {number} rating - Rating (1-5)
   * @param {string} comment - Optional comment
   * @returns {Promise} - Promise resolving to rating result
   */
  async rateTrip(tripId, rating, comment = null) {
    try {
      const response = await riderAPI.rateTrip(tripId, rating, comment)
      return {
        success: true,
        message: response.message
      }
    } catch (error) {
      console.error('Failed to rate trip:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }
}

export default riderService
