/**
 * Notification Service
 * Handles fetching, marking as read, and deleting notifications
 */

import api from './api'

const notificationService = {
  /**
   * Fetch user notifications
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Maximum number of notifications to return
   * @param {number} params.offset - Number of notifications to skip
   * @param {boolean} params.unread_only - If true, only return unread notifications
   * @returns {Promise<Object>} Notifications data
   */
  async getNotifications({ limit = 50, offset = 0, unread_only = false } = {}) {
    try {
      const response = await api.get('/notifications/', {
        params: { limit, offset, unread_only }
      })
      // Response interceptor already unwraps response.data, so response IS the data
      if (!response || response.success === false) {
        return { success: false, notifications: [], total: 0 }
      }
      return response
    } catch (error) {
      // Silently fail for auth errors
      if (error?.response?.status === 401) {
        return { success: false, notifications: [], total: 0 }
      }
      console.error('Failed to fetch notifications:', error)
      // Return safe default instead of throwing
      return { success: false, notifications: [], total: 0 }
    }
  },

  /**
   * Get unread notification count
   * @returns {Promise<number>} Count of unread notifications
   */
  async getUnreadCount() {
    try {
      const response = await api.get('/notifications/', {
        params: { limit: 1, unread_only: true }
      })
      // Response interceptor already unwraps response.data
      if (!response || response.success === false) {
        return 0
      }
      return response.total || 0
    } catch (error) {
      // Silently fail for auth errors (user not logged in yet)
      if (error?.response?.status !== 401) {
        console.error('Failed to fetch unread count:', error)
      }
      return 0
    }
  },

  /**
   * Mark a notification as read
   * @param {string} notificationId - Notification ID
   * @returns {Promise<Object>} Success response
   */
  async markAsRead(notificationId) {
    try {
      const response = await api.put(`/notifications/${notificationId}/read`)
      return response
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
      throw error
    }
  },

  /**
   * Mark all notifications as read
   * @returns {Promise<Object>} Success response with count
   */
  async markAllAsRead() {
    try {
      const response = await api.put('/notifications/mark-all-read')
      return response
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error)
      throw error
    }
  },

  /**
   * Delete a notification
   * @param {string} notificationId - Notification ID
   * @returns {Promise<Object>} Success response
   */
  async deleteNotification(notificationId) {
    try {
      const response = await api.delete(`/notifications/${notificationId}`)
      return response
    } catch (error) {
      console.error('Failed to delete notification:', error)
      throw error
    }
  },

  /**
   * Format notification time for display
   * @param {string} timestamp - ISO timestamp
   * @returns {string} Formatted time string
   */
  formatNotificationTime(timestamp) {
    if (!timestamp) return ''
    
    const now = new Date()
    const notifTime = new Date(timestamp)
    const diffMs = now - notifTime
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} min ago`
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
    
    return notifTime.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: notifTime.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    })
  },

  /**
   * Get notification icon based on type
   * @param {string} type - Notification type
   * @returns {string} Icon name
   */
  getNotificationIcon(type) {
    const icons = {
      'trip_request': '🚕',
      'trip_accepted': '✅',
      'trip_rejected': '❌',
      'trip_cancelled': '🚫',
      'trip_started': '🏁',
      'trip_completed': '🎉',
      'driver_arrived': '📍',
      'payment_received': '💰',
      'rating_received': '⭐',
      'system_message': '📢'
    }
    return icons[type] || '🔔'
  },

  /**
   * Get notification color based on type
   * @param {string} type - Notification type
   * @returns {string} Color class
   */
  getNotificationColor(type) {
    const colors = {
      'trip_request': 'text-blue-400',
      'trip_accepted': 'text-green-400',
      'trip_rejected': 'text-red-400',
      'trip_cancelled': 'text-orange-400',
      'trip_started': 'text-purple-400',
      'trip_completed': 'text-green-400',
      'driver_arrived': 'text-blue-400',
      'payment_received': 'text-green-400',
      'rating_received': 'text-yellow-400',
      'system_message': 'text-gray-400'
    }
    return colors[type] || 'text-gray-400'
  }
}

export default notificationService
