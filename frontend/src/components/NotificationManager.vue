<template>
  <div class="notification-manager">
    <!-- Toast Notifications -->
    <transition-group name="toast-slide" tag="div" class="toast-container">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="toast-notification"
        :class="[`toast-${toast.type}`, { 'toast-priority': toast.priority === 'high' }]"
        @click="removeToast(toast.id)"
      >
        <div class="toast-content">
          <div class="toast-icon">
            <!-- Success -->
            <svg v-if="toast.type === 'success'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <!-- Error -->
            <svg v-else-if="toast.type === 'error'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <!-- Warning -->
            <svg v-else-if="toast.type === 'warning'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <!-- Info -->
            <svg v-else-if="toast.type === 'info'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="toast-message">
            <div v-if="toast.title" class="toast-title">{{ toast.title }}</div>
            <div class="toast-text">{{ toast.message }}</div>
          </div>
          <button class="toast-close" @click.stop="removeToast(toast.id)">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="toast-progress" :style="{ animationDuration: `${toast.duration}ms` }"></div>
      </div>
    </transition-group>

    <!-- Alert Modal -->
    <transition name="modal-fade">
      <div v-if="alert" class="modal-overlay" @click="closeAlert">
        <div class="modal-content" :class="`modal-${alert.type}`" @click.stop>
          <div class="modal-header">
            <div class="modal-icon">
              <svg v-if="alert.type === 'success'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <svg v-else-if="alert.type === 'error'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <svg v-else-if="alert.type === 'warning'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3>{{ alert.title }}</h3>
            <button class="modal-close" @click="closeAlert">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <p>{{ alert.message }}</p>
          </div>
          <div class="modal-footer">
            <button v-if="alert.cancelText" class="btn-secondary" @click="handleAlertCancel">
              {{ alert.cancelText }}
            </button>
            <button class="btn-primary" :class="`btn-${alert.type}`" @click="handleAlertConfirm">
              {{ alert.confirmText || 'OK' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const toasts = ref([])
const alert = ref(null)
let toastIdCounter = 0

// Audio context for beep sounds (created on first use)
let audioContext = null

// Toast Management
const showToast = (message, type = 'info', options = {}) => {
  const toast = {
    id: ++toastIdCounter,
    message,
    type,
    title: options.title,
    duration: options.duration || 4000,
    priority: options.priority || 'normal',
    sound: options.sound !== false
  }
  
  toasts.value.push(toast)
  
  // Play sound
  if (toast.sound) {
    playSound(type)
  }
  
  // Auto remove
  setTimeout(() => {
    removeToast(toast.id)
  }, toast.duration)
  
  return toast.id
}

const removeToast = (id) => {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index !== -1) {
    toasts.value.splice(index, 1)
  }
}

// Alert Management
const showAlert = (title, message, type = 'info', options = {}) => {
  return new Promise((resolve) => {
    alert.value = {
      title,
      message,
      type,
      confirmText: options.confirmText,
      cancelText: options.cancelText,
      onConfirm: () => resolve(true),
      onCancel: () => resolve(false)
    }
    
    if (options.sound !== false) {
      playSound(type)
    }
  })
}

const closeAlert = () => {
  if (alert.value && alert.value.onCancel) {
    alert.value.onCancel()
  }
  alert.value = null
}

const handleAlertConfirm = () => {
  if (alert.value && alert.value.onConfirm) {
    alert.value.onConfirm()
  }
  alert.value = null
}

const handleAlertCancel = () => {
  closeAlert()
}

// Sound Management - Simple beep using Web Audio API
const playSound = (type) => {
  try {
    // Initialize audio context on first use
    if (!audioContext) {
      audioContext = new (window.AudioContext || window.webkitAudioContext)()
    }
    
    // Create oscillator for beep sound
    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()
    
    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)
    
    // Set frequency based on notification type
    const frequencies = {
      success: 800,  // Higher pitch for success
      error: 400,    // Lower pitch for errors
      warning: 600,  // Medium pitch for warnings
      info: 700      // Medium-high for info
    }
    
    oscillator.frequency.value = frequencies[type] || 700
    oscillator.type = 'sine'
    
    // Set volume envelope
    const now = audioContext.currentTime
    gainNode.gain.setValueAtTime(0, now)
    gainNode.gain.linearRampToValueAtTime(0.15, now + 0.01)
    gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.15)
    
    // Play beep
    oscillator.start(now)
    oscillator.stop(now + 0.15)
  } catch (error) {
    // Silently fail if audio can't play (browser restrictions or unsupported)
    console.debug('Notification sound not available:', error.message)
  }
}

// Global API
onMounted(() => {
  // Expose globally for easy access
  if (typeof window !== 'undefined') {
    window.$notification = {
      toast: showToast,
      success: (message, options) => showToast(message, 'success', options),
      error: (message, options) => showToast(message, 'error', options),
      warning: (message, options) => showToast(message, 'warning', options),
      info: (message, options) => showToast(message, 'info', options),
      alert: showAlert,
      confirm: (title, message, options) => showAlert(title, message, 'warning', {
        cancelText: 'Cancel',
        confirmText: 'Confirm',
        ...options
      })
    }
    
    // Backward compatibility
    window.displayToast = (message, type) => showToast(message, type)
    window.showNotification = (title, message, type) => showToast(message, type, { title })
  }
})

onUnmounted(() => {
  if (typeof window !== 'undefined') {
    delete window.$notification
    delete window.displayToast
    delete window.showNotification
  }
})
</script>

<style scoped>
.notification-manager {
  position: relative;
  z-index: 10000;
}

/* Toast Container */
.toast-container {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 10001;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 420px;
  width: calc(100% - 40px);
}

/* Toast Notification */
.toast-notification {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  position: relative;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.toast-notification:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.2);
}

.toast-priority {
  animation: pulse 1s ease-in-out infinite;
}

.toast-content {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  gap: 12px;
}

.toast-icon {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.toast-icon svg {
  width: 22px;
  height: 22px;
}

.toast-message {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 4px;
  color: #1a1a1a;
}

.toast-text {
  font-size: 14px;
  color: #4a5568;
  line-height: 1.5;
}

.toast-close {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  transition: all 0.2s;
}

.toast-close:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #4b5563;
}

.toast-close svg {
  width: 16px;
  height: 16px;
}

.toast-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  width: 100%;
  transform-origin: left;
  animation: progress linear forwards;
}

@keyframes progress {
  from { transform: scaleX(1); }
  to { transform: scaleX(0); }
}

/* Toast Types */
.toast-success .toast-icon {
  background: #dcfce7;
  color: #16a34a;
}

.toast-success .toast-progress {
  background: #16a34a;
}

.toast-error .toast-icon {
  background: #fee2e2;
  color: #dc2626;
}

.toast-error .toast-progress {
  background: #dc2626;
}

.toast-warning .toast-icon {
  background: #fef3c7;
  color: #d97706;
}

.toast-warning .toast-progress {
  background: #d97706;
}

.toast-info .toast-icon {
  background: #dbeafe;
  color: #2563eb;
}

.toast-info .toast-progress {
  background: #2563eb;
}

/* Toast Animations */
.toast-slide-enter-active {
  animation: slideInRight 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.toast-slide-leave-active {
  animation: slideOutRight 0.3s ease;
}

@keyframes slideInRight {
  from {
    transform: translateX(120%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideOutRight {
  from {
    transform: translateX(0) scale(1);
    opacity: 1;
  }
  to {
    transform: translateX(120%) scale(0.9);
    opacity: 0;
  }
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  }
  50% {
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.25), 0 0 20px rgba(59, 130, 246, 0.5);
  }
}

/* Modal Overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10002;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 16px;
  max-width: 480px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.modal-header {
  position: relative;
  padding: 24px 24px 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 16px;
}

.modal-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.modal-icon svg {
  width: 28px;
  height: 28px;
}

.modal-success .modal-icon {
  background: #dcfce7;
  color: #16a34a;
}

.modal-error .modal-icon {
  background: #fee2e2;
  color: #dc2626;
}

.modal-warning .modal-icon {
  background: #fef3c7;
  color: #d97706;
}

.modal-info .modal-icon {
  background: #dbeafe;
  color: #2563eb;
}

.modal-header h3 {
  flex: 1;
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.modal-close {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  transition: all 0.2s;
}

.modal-close:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #4b5563;
}

.modal-close svg {
  width: 20px;
  height: 20px;
}

.modal-body {
  padding: 24px;
}

.modal-body p {
  margin: 0;
  font-size: 15px;
  line-height: 1.6;
  color: #4a5568;
}

.modal-footer {
  padding: 20px 24px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-primary.btn-success {
  background: #16a34a;
}

.btn-primary.btn-success:hover {
  background: #15803d;
}

.btn-primary.btn-error {
  background: #dc2626;
}

.btn-primary.btn-error:hover {
  background: #b91c1c;
}

.btn-primary.btn-warning {
  background: #d97706;
}

.btn-primary.btn-warning:hover {
  background: #b45309;
}

.btn-secondary {
  background: #f3f4f6;
  color: #4b5563;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

/* Modal Animations */
.modal-fade-enter-active {
  animation: modalFadeIn 0.3s ease;
}

.modal-fade-leave-active {
  animation: modalFadeOut 0.2s ease;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes modalFadeOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}

.modal-fade-enter-active .modal-content {
  animation: modalScaleIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-fade-leave-active .modal-content {
  animation: modalScaleOut 0.2s ease;
}

@keyframes modalScaleIn {
  from {
    transform: scale(0.9);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes modalScaleOut {
  from {
    transform: scale(1);
    opacity: 1;
  }
  to {
    transform: scale(0.9);
    opacity: 0;
  }
}

/* Mobile Responsive */
@media (max-width: 640px) {
  .toast-container {
    top: 60px;
    right: 12px;
    width: calc(100% - 24px);
  }
  
  .toast-content {
    padding: 14px;
  }
  
  .modal-content {
    margin: 0 12px;
  }
  
  .modal-header {
    padding: 20px 20px 16px;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  .modal-footer {
    padding: 16px 20px;
    flex-direction: column-reverse;
  }
  
  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
</style>
