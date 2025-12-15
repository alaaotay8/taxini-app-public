<template>
  <transition name="slide">
    <div 
      v-if="isOpen" 
      class="fixed top-0 right-0 w-96 h-full bg-gradient-to-b from-[#0A2F23] to-[#051912] shadow-2xl z-50 flex flex-col"
    >
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-green-800/30">
        <h2 class="text-xl font-bold text-white">Notifications</h2>
        <button 
          @click="close"
          class="p-2 hover:bg-green-800/20 rounded-lg transition-colors"
        >
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Actions -->
      <div v-if="notifications.length > 0" class="flex gap-2 p-4 border-b border-green-800/30">
        <button 
          v-if="unreadCount > 0"
          @click="handleMarkAllRead"
          class="flex-1 px-3 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg transition-colors"
        >
          Mark All Read ({{ unreadCount }})
        </button>
        <button 
          @click="handleClearAll"
          class="flex-1 px-3 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 text-sm rounded-lg transition-colors"
        >
          Clear All
        </button>
      </div>

      <!-- Notifications List -->
      <div class="flex-1 overflow-y-auto">
        <!-- Loading State -->
        <div v-if="isLoading && notifications.length === 0" class="flex items-center justify-center h-64">
          <div class="text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto mb-4"></div>
            <p class="text-gray-400">Loading notifications...</p>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else-if="notifications.length === 0" class="flex items-center justify-center h-64">
          <div class="text-center">
            <div class="text-6xl mb-4">🔔</div>
            <p class="text-gray-400 text-lg">No notifications yet</p>
            <p class="text-gray-500 text-sm mt-2">You'll see updates about your trips here</p>
          </div>
        </div>

        <!-- Notification Items -->
        <div v-else class="divide-y divide-green-800/20">
          <div
            v-for="notification in notifications"
            :key="notification.id"
            class="p-4 hover:bg-green-800/10 transition-colors cursor-pointer relative"
            :class="{ 'bg-green-800/5': !notification.is_read }"
            @click="handleNotificationClick(notification)"
          >
            <!-- Unread Indicator -->
            <div 
              v-if="!notification.is_read" 
              class="absolute top-4 right-4 w-2 h-2 bg-yellow-400 rounded-full"
              title="Unread"
            ></div>

            <!-- Icon and Content -->
            <div class="flex gap-3">
              <!-- Icon -->
              <div 
                class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-xl"
                :class="getNotificationBgColor(notification.notification_type)"
              >
                {{ getNotificationIcon(notification.notification_type) }}
              </div>

              <!-- Content -->
              <div class="flex-1 min-w-0">
                <h3 class="text-white font-semibold text-sm mb-1">
                  {{ notification.title }}
                </h3>
                <p class="text-gray-400 text-sm mb-2 break-words">
                  {{ notification.message }}
                </p>
                <div class="flex items-center justify-between">
                  <span class="text-gray-500 text-xs">
                    {{ formatTime(notification.created_at) }}
                  </span>
                  <button
                    @click.stop="handleDelete(notification.id)"
                    class="text-red-400 hover:text-red-300 text-xs transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>

  <!-- Custom Confirmation Dialog -->
  <transition name="fade">
    <div v-if="showConfirmDialog" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-[60]" @click.self="showConfirmDialog = false">
      <div class="bg-gradient-to-br from-[#0d2621] to-[#0a1f1a] border-2 border-yellow-500/50 rounded-3xl w-[90%] max-w-md shadow-2xl animate-scale-in">
        <!-- Header -->
        <div class="px-6 pt-6 pb-4 border-b border-yellow-500/20 bg-yellow-500/5">
          <h3 class="text-2xl font-bold text-yellow-400 text-center">Confirm Action</h3>
        </div>
        
        <!-- Body -->
        <div class="px-6 py-6">
          <p class="text-gray-200 text-center text-lg leading-relaxed">{{ confirmMessage }}</p>
        </div>
        
        <!-- Footer -->
        <div class="px-6 pb-6 flex gap-3">
          <button
            @click="handleConfirmCancel"
            class="flex-1 px-6 py-3.5 bg-gray-700/30 hover:bg-gray-700/50 border-2 border-gray-600/50 hover:border-gray-500 text-gray-300 hover:text-white font-semibold rounded-xl transition-all duration-300 hover:scale-105"
          >
            Cancel
          </button>
          <button
            @click="handleConfirmOk"
            class="flex-1 px-6 py-3.5 bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-400 hover:to-yellow-500 text-gray-900 font-bold rounded-xl transition-all duration-300 hover:scale-105 shadow-lg shadow-yellow-500/30"
          >
            OK
          </button>
        </div>
      </div>
    </div>
  </transition>

  <!-- Backdrop -->
  <transition name="fade">
    <div 
      v-if="isOpen"
      @click="close"
      class="fixed inset-0 bg-black/50 z-40"
    ></div>
  </transition>
</template>

<script setup>
import { computed, watch, onMounted, ref } from 'vue'
import { useNotificationStore } from '../stores/notificationStore'
import notificationService from '../services/notificationService'

// Props
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['close'])

// Store
const notificationStore = useNotificationStore()

// Computed - Show all notifications (sorted by date, newest first)
const notifications = computed(() => notificationStore.notifications)
const unreadCount = computed(() => notificationStore.unreadCount)
const isLoading = computed(() => notificationStore.isLoading)

// Confirmation dialog state
const showConfirmDialog = ref(false)
const confirmMessage = ref('')
const confirmCallback = ref(null)

// Fetch notifications when panel opens
watch(() => props.isOpen, async (isOpen) => {
  if (isOpen) {
    console.log('📬 Notification panel opened - fetching notifications...')
    await notificationStore.fetchNotifications(true) // Force refresh
    console.log('📬 Notifications fetched:', notifications.value.length)
  }
}, { immediate: true })

// Also fetch on mount
onMounted(async () => {
  if (props.isOpen) {
    await notificationStore.fetchNotifications(true)
  }
})

// Methods
function close() {
  emit('close')
}

async function handleNotificationClick(notification) {
  if (!notification.is_read) {
    try {
      await notificationStore.markAsRead(notification.id)
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
    }
  }
}

async function handleMarkAllRead() {
  try {
    await notificationStore.markAllAsRead()
  } catch (error) {
    console.error('Failed to mark all as read:', error)
  }
}

async function handleClearAll() {
  showConfirm('Are you sure you want to delete all notifications?', async () => {
    try {
      await notificationStore.clearAllNotifications()
    } catch (error) {
      console.error('Failed to clear all notifications:', error)
    }
  })
}

function showConfirm(message, callback) {
  confirmMessage.value = message
  confirmCallback.value = callback
  showConfirmDialog.value = true
}

function handleConfirmOk() {
  showConfirmDialog.value = false
  if (confirmCallback.value) {
    confirmCallback.value()
    confirmCallback.value = null
  }
}

function handleConfirmCancel() {
  showConfirmDialog.value = false
  confirmCallback.value = null
}

async function handleDelete(notificationId) {
  try {
    await notificationStore.deleteNotification(notificationId)
  } catch (error) {
    console.error('Failed to delete notification:', error)
  }
}

function formatTime(timestamp) {
  return notificationService.formatNotificationTime(timestamp)
}

function getNotificationIcon(type) {
  return notificationService.getNotificationIcon(type)
}

function getNotificationBgColor(type) {
  const colors = {
    'trip_request': 'bg-blue-500/20',
    'trip_accepted': 'bg-green-500/20',
    'trip_rejected': 'bg-red-500/20',
    'trip_cancelled': 'bg-orange-500/20',
    'trip_started': 'bg-purple-500/20',
    'trip_completed': 'bg-green-500/20',
    'driver_arrived': 'bg-blue-500/20',
    'payment_received': 'bg-green-500/20',
    'rating_received': 'bg-yellow-500/20',
    'system_message': 'bg-gray-500/20'
  }
  return colors[type] || 'bg-gray-500/20'
}
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease-out;
}

.slide-enter-from {
  transform: translateX(100%);
}

.slide-leave-to {
  transform: translateX(100%);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease-out;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes scale-in {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-scale-in {
  animation: scale-in 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
