/**
 * Notification Store
 * Global state management for notifications
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import notificationService from '../services/notificationService'

export const useNotificationStore = defineStore('notifications', () => {
  // State
  const notifications = ref([])
  const unreadCount = ref(0)
  const isLoading = ref(false)
  const error = ref(null)
  const lastFetchTime = ref(null)

  // Computed
  const unreadNotifications = computed(() => 
    notifications.value.filter(n => !n.is_read)
  )

  const todayNotifications = computed(() => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    return notifications.value.filter(n => {
      const notifDate = new Date(n.created_at)
      notifDate.setHours(0, 0, 0, 0)
      return notifDate.getTime() === today.getTime()
    })
  })

  // Actions
  async function fetchNotifications(forceRefresh = false) {
    // Avoid fetching too frequently (5 second cooldown)
    if (!forceRefresh && lastFetchTime.value && Date.now() - lastFetchTime.value < 5000) {
      return
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await notificationService.getNotifications({
        limit: 50,
        offset: 0,
        unread_only: false
      })

      // Handle response - could be undefined, or have success: false
      if (response && response.success !== false && Array.isArray(response.notifications)) {
        notifications.value = response.notifications
        unreadCount.value = notifications.value.filter(n => !n.is_read).length
        lastFetchTime.value = Date.now()

        console.log('📬 Fetched notifications:', notifications.value.length)
        console.log('🔴 Unread count:', unreadCount.value)
        
        return response
      } else {
        // Auth error or failed response
        notifications.value = []
        unreadCount.value = 0
        return { success: false, notifications: [], total: 0 }
      }
    } catch (err) {
      // Don't throw error, just log it
      console.warn('⚠️ Could not fetch notifications:', err.message)
      error.value = err.message || 'Failed to load notifications'
      notifications.value = []
      unreadCount.value = 0
      return { success: false, notifications: [], total: 0 }
    } finally {
      isLoading.value = false
    }
  }

  async function fetchUnreadCount() {
    try {
      const count = await notificationService.getUnreadCount()
      unreadCount.value = count
      return count
    } catch (err) {
      // Silently fail - keeps existing count
      return unreadCount.value
    }
  }

  async function markAsRead(notificationId) {
    try {
      await notificationService.markAsRead(notificationId)

      // Update local state
      const notification = notifications.value.find(n => n.id === notificationId)
      if (notification && !notification.is_read) {
        notification.is_read = true
        notification.read_at = new Date().toISOString()
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }

      console.log('✅ Marked notification as read:', notificationId)
    } catch (err) {
      console.error('Failed to mark notification as read:', err)
      throw err
    }
  }

  async function markAllAsRead() {
    try {
      const response = await notificationService.markAllAsRead()

      // Update local state
      notifications.value.forEach(n => {
        if (!n.is_read) {
          n.is_read = true
          n.read_at = new Date().toISOString()
        }
      })
      unreadCount.value = 0

      console.log('✅ Marked all notifications as read:', response.count)
      return response
    } catch (err) {
      console.error('Failed to mark all notifications as read:', err)
      throw err
    }
  }

  async function deleteNotification(notificationId) {
    try {
      await notificationService.deleteNotification(notificationId)

      // Remove from local state
      const index = notifications.value.findIndex(n => n.id === notificationId)
      if (index !== -1) {
        const wasUnread = !notifications.value[index].is_read
        notifications.value.splice(index, 1)
        
        if (wasUnread) {
          unreadCount.value = Math.max(0, unreadCount.value - 1)
        }
      }

      console.log('🗑️ Deleted notification:', notificationId)
    } catch (err) {
      console.error('Failed to delete notification:', err)
      throw err
    }
  }

  async function clearAllNotifications() {
    try {
      // Delete all notifications one by one
      const deletePromises = notifications.value.map(n => 
        notificationService.deleteNotification(n.id)
      )
      await Promise.all(deletePromises)

      // Clear local state
      notifications.value = []
      unreadCount.value = 0

      console.log('🗑️ Cleared all notifications')
    } catch (err) {
      console.error('Failed to clear all notifications:', err)
      throw err
    }
  }

  function addNotification(notification) {
    // Add new notification to the beginning of the list
    notifications.value.unshift(notification)
    
    if (!notification.is_read) {
      unreadCount.value++
    }

    console.log('➕ Added new notification:', notification.notification_type)
  }

  function reset() {
    notifications.value = []
    unreadCount.value = 0
    isLoading.value = false
    error.value = null
    lastFetchTime.value = null
  }

  return {
    // State
    notifications,
    unreadCount,
    isLoading,
    error,
    lastFetchTime,

    // Computed
    unreadNotifications,
    todayNotifications,

    // Actions
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    clearAllNotifications,
    addNotification,
    reset
  }
})
