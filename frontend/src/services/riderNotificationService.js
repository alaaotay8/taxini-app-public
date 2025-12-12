/**
 * Rider Notification Service
 * Handles real-time notifications for riders via Supabase channels
 */

import { supabase } from './supabaseClient'

class RiderNotificationService {
  constructor() {
    this.channel = null
    this.riderId = null
    this.isConnected = false
    this.messageHandlers = []
  }

  /**
   * Subscribe to rider's notification channel
   * @param {string} riderId - Rider's user ID
   * @param {function} onMessage - Callback for incoming messages
   */
  async subscribe(riderId, onMessage) {
    if (this.isConnected && this.riderId === riderId) {
      console.log('📱 Already subscribed to rider notifications')
      return
    }

    // Unsubscribe from previous channel if exists
    await this.unsubscribe()

    this.riderId = riderId
    const channelName = `rider_notifications:${riderId}`

    console.log(`📱 Subscribing to rider notification channel: ${channelName}`)

    try {
      this.channel = supabase.channel(channelName)

      // Listen for all broadcast messages
      this.channel
        .on('broadcast', { event: 'notification' }, (payload) => {
          console.log('📬 Received rider notification:', payload)
          this.handleNotification(payload.payload)
        })
        .subscribe((status) => {
          console.log(`📱 Rider notification channel status: ${status}`)
          if (status === 'SUBSCRIBED') {
            this.isConnected = true
            console.log('✅ Successfully subscribed to rider notifications')
          } else if (status === 'CLOSED') {
            this.isConnected = false
            console.log('❌ Rider notification channel closed')
          } else if (status === 'CHANNEL_ERROR') {
            this.isConnected = false
            console.error('❌ Rider notification channel error')
          }
        })

      // Store message handler
      if (onMessage) {
        this.messageHandlers.push(onMessage)
      }

      return true
    } catch (error) {
      console.error('Failed to subscribe to rider notifications:', error)
      return false
    }
  }

  /**
   * Handle incoming notification
   * @param {object} notification - Notification payload
   */
  handleNotification(notification) {
    console.log('📨 Processing rider notification:', notification)

    // Call all registered handlers
    this.messageHandlers.forEach(handler => {
      try {
        handler(notification)
      } catch (error) {
        console.error('Error in notification handler:', error)
      }
    })

    // Show toast notification based on type
    if (typeof window !== 'undefined' && window.$notification) {
      const { type, title, message, priority } = notification

      switch (type) {
        case 'trip_accepted':
          window.$notification.success(
            message || 'Your trip has been accepted!',
            { title: title || 'Driver Found', priority: 'high', sound: true }
          )
          break

        case 'trip_cancelled':
        case 'trip_declined':
          window.$notification.warning(
            message || 'Your trip was cancelled',
            { title: title || 'Trip Cancelled', priority: 'high', sound: true }
          )
          break

        case 'trip_reassigning':
          window.$notification.info(
            message || 'Looking for another driver...',
            { title: title || 'Searching', priority: 'normal', sound: false }
          )
          break

        case 'driver_arrived':
          window.$notification.success(
            message || 'Your driver has arrived!',
            { title: title || 'Driver Arrived', priority: 'high', sound: true }
          )
          break

        case 'trip_started':
          window.$notification.info(
            message || 'Your trip has started',
            { title: title || 'Trip Started', priority: 'normal', sound: true }
          )
          break

        case 'trip_completed':
          window.$notification.success(
            message || 'You have arrived at your destination',
            { title: title || 'Trip Completed', priority: 'high', sound: true }
          )
          break

        case 'no_drivers_available':
          window.$notification.error(
            message || 'No drivers available. Please try again.',
            { title: title || 'No Drivers', priority: 'high', sound: true }
          )
          break

        default:
          window.$notification.info(
            message || 'You have a new notification',
            { title: title || 'Notification', priority: priority || 'normal', sound: false }
          )
      }
    }
  }

  /**
   * Add a message handler
   * @param {function} handler - Handler function
   */
  addHandler(handler) {
    if (typeof handler === 'function') {
      this.messageHandlers.push(handler)
    }
  }

  /**
   * Remove a message handler
   * @param {function} handler - Handler function to remove
   */
  removeHandler(handler) {
    const index = this.messageHandlers.indexOf(handler)
    if (index > -1) {
      this.messageHandlers.splice(index, 1)
    }
  }

  /**
   * Unsubscribe from notification channel
   */
  async unsubscribe() {
    if (this.channel) {
      console.log('📱 Unsubscribing from rider notifications')
      await supabase.removeChannel(this.channel)
      this.channel = null
      this.isConnected = false
      this.riderId = null
      this.messageHandlers = []
    }
  }

  /**
   * Check if connected
   */
  get connected() {
    return this.isConnected
  }
}

// Export singleton instance
export const riderNotificationService = new RiderNotificationService()
export default riderNotificationService
