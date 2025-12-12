/**
 * Centralized Notification Store
 * Manages persistent notifications that appear in the notification panel
 * Works alongside NotificationManager for toast/alerts
 */
import { ref, computed } from 'vue'

// Shared notification state across components
const notifications = ref([])
let nextId = 1

// Helper to format relative time
const getRelativeTime = (timestamp) => {
  const now = Date.now()
  const diff = now - timestamp
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (seconds < 60) return 'Just now'
  if (minutes < 60) return `${minutes} min ago`
  if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`
  return `${days} day${days > 1 ? 's' : ''} ago`
}

export function useNotificationStore() {
  const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)

  /**
   * Add a notification to the panel
   * @param {Object} options - Notification options
   * @param {string} options.type - Type: 'trip', 'cancelled', 'earnings', 'info', 'warning', 'error', 'success'
   * @param {string} options.title - Notification title
   * @param {string} options.message - Notification message
   * @param {boolean} options.read - Whether notification is read (default: false)
   * @param {boolean} options.showToast - Whether to also show a toast (default: true)
   * @param {Object} options.data - Additional data to store with notification
   */
  const addNotification = (options) => {
    const {
      type = 'info',
      title,
      message,
      read = false,
      showToast = true,
      data = null
    } = options

    // Create notification
    const notification = {
      id: nextId++,
      type,
      title,
      message,
      time: getRelativeTime(Date.now()),
      timestamp: Date.now(),
      read,
      data
    }

    // Add to beginning of array (newest first)
    notifications.value.unshift(notification)

    // Keep only last 50 notifications
    if (notifications.value.length > 50) {
      notifications.value = notifications.value.slice(0, 50)
    }

    // Show toast notification if requested
    if (showToast && typeof window !== 'undefined' && window.$notification) {
      const toastType = type === 'cancelled' || type === 'error' ? 'error' : 
                       type === 'warning' ? 'warning' :
                       type === 'success' || type === 'trip' || type === 'earnings' ? 'success' : 'info'
      
      window.$notification.toast(title, toastType, {
        duration: 4000
      })
    }

    return notification
  }

  /**
   * Mark notification as read
   */
  const markAsRead = (notificationId) => {
    const notification = notifications.value.find(n => n.id === notificationId)
    if (notification) {
      notification.read = true
    }
  }

  /**
   * Mark all notifications as read
   */
  const markAllAsRead = () => {
    notifications.value.forEach(n => n.read = true)
  }

  /**
   * Clear all notifications
   */
  const clearAll = () => {
    notifications.value = []
  }

  /**
   * Remove a specific notification
   */
  const removeNotification = (notificationId) => {
    const index = notifications.value.findIndex(n => n.id === notificationId)
    if (index !== -1) {
      notifications.value.splice(index, 1)
    }
  }

  /**
   * Update notification times (call periodically)
   */
  const updateTimes = () => {
    notifications.value.forEach(n => {
      n.time = getRelativeTime(n.timestamp)
    })
  }

  // Update times every minute
  setInterval(updateTimes, 60000)

  // Predefined notification helpers for common scenarios
  const notifyTripCompleted = (amount, currency = 'TND', role = 'driver') => {
    const message = role === 'driver' 
      ? `You earned ${amount} ${currency} from your last trip`
      : `You paid ${amount} ${currency} for your last trip`
    
    return addNotification({
      type: 'trip',
      title: 'Trip Completed',
      message,
      data: { amount, currency, role }
    })
  }

  const notifyTripCancelled = (destination, cancelledBy = 'rider', role = 'driver') => {
    const message = role === 'driver'
      ? `${cancelledBy === 'rider' ? 'Rider' : 'You'} cancelled the trip${destination ? ` to ${destination}` : ''}`
      : `${cancelledBy === 'driver' ? 'Driver' : 'You'} cancelled the trip${destination ? ` to ${destination}` : ''}`
    
    return addNotification({
      type: 'cancelled',
      title: 'Trip Cancelled',
      message,
      data: { destination, cancelledBy, role }
    })
  }

  const notifyTripRequested = (pickup, destination, tripId = null) => {
    // Check if same trip notification already exists (within last 60 seconds)
    const sixtySecondsAgo = Date.now() - 60000
    
    // Primary: Check by trip ID if provided
    if (tripId) {
      const existingById = notifications.value.find(n => 
        n.type === 'trip' && 
        n.timestamp > sixtySecondsAgo &&
        n.data?.tripId === tripId
      )
      
      if (existingById) {
        console.log('🚫 Duplicate trip notification prevented (by ID):', tripId)
        return existingById
      }
    }
    
    // Secondary: Check by pickup/destination text
    const existingByLocation = notifications.value.find(n => 
      n.type === 'trip' && 
      n.timestamp > sixtySecondsAgo &&
      n.data?.pickup === pickup && 
      n.data?.destination === destination
    )
    
    if (existingByLocation) {
      console.log('🚫 Duplicate trip notification prevented (by location):', pickup, destination)
      return existingByLocation
    }
    
    console.log('✅ Adding new trip notification:', { tripId, pickup, destination })
    return addNotification({
      type: 'trip',
      title: 'New Trip Request',
      message: `From ${pickup} to ${destination}`,
      data: { pickup, destination, tripId }
    })
  }

  const notifyTripAccepted = (driverName) => {
    return addNotification({
      type: 'success',
      title: 'Trip Accepted',
      message: `${driverName} is on the way to pick you up!`,
      data: { driverName }
    })
  }

  const notifyDriverArrived = () => {
    return addNotification({
      type: 'info',
      title: 'Driver Arrived',
      message: 'Your driver has arrived at the pickup location',
      showToast: true
    })
  }

  const notifyTripStarted = () => {
    return addNotification({
      type: 'info',
      title: 'Trip Started',
      message: 'Your trip has begun. Safe travels!',
      showToast: true
    })
  }

  const notifyEarningsUpdate = (amount, currency = 'TND', period = 'today') => {
    return addNotification({
      type: 'earnings',
      title: 'Earnings Update',
      message: `You've earned ${amount} ${currency} ${period}! Keep it up!`,
      data: { amount, currency, period }
    })
  }

  const notifyNoDriversAvailable = () => {
    return addNotification({
      type: 'warning',
      title: 'No Drivers Available',
      message: 'No drivers are currently available in your area. Please try again later.',
      showToast: true
    })
  }

  const notifyDriverDeclined = (driverName) => {
    return addNotification({
      type: 'warning',
      title: 'Driver Declined',
      message: `${driverName} declined your trip request. Searching for another driver...`,
      showToast: true
    })
  }

  return {
    // State
    notifications,
    unreadCount,
    
    // Methods
    addNotification,
    markAsRead,
    markAllAsRead,
    clearAll,
    removeNotification,
    updateTimes,
    
    // Helpers
    notifyTripCompleted,
    notifyTripCancelled,
    notifyTripRequested,
    notifyTripAccepted,
    notifyDriverArrived,
    notifyTripStarted,
    notifyEarningsUpdate,
    notifyNoDriversAvailable,
    notifyDriverDeclined
  }
}
