import { ref } from 'vue'

export function useDriverUI() {
  // State
  const showMenu = ref(false)
  const showBottomSheet = ref(true)
  const unreadNotifications = ref(0)
  
  // Touch gesture state
  let touchStartY = 0
  let touchStartTime = 0
  let isDragging = false
  const SWIPE_THRESHOLD = 50
  const SWIPE_VELOCITY_THRESHOLD = 0.5

  // Handle map click to hide menu only (keep bottom sheet visible)
  const handleMapClick = (event) => {
    if (event.target.classList.contains('mapboxgl-canvas') || 
        event.target.classList.contains('map-container')) {
      // Only hide menu on map click, keep bottom sheet visible for better UX
      if (showMenu.value) {
        showMenu.value = false
      }
    }
  }

  // Bottom sheet touch gestures
  const handleBottomSheetTouchStart = (event) => {
    isDragging = false
    touchStartY = event.touches[0].clientY
    touchStartTime = Date.now()
  }

  const handleBottomSheetTouchMove = (event) => {
    isDragging = true
  }

  const handleBottomSheetTouchEnd = (event) => {
    if (!isDragging) return
    
    const touchEndY = event.changedTouches[0].clientY
    const touchEndTime = Date.now()
    const deltaY = touchEndY - touchStartY
    const deltaTime = touchEndTime - touchStartTime
    const velocity = Math.abs(deltaY) / deltaTime

    // Swipe down to hide
    if (deltaY > SWIPE_THRESHOLD && velocity > SWIPE_VELOCITY_THRESHOLD) {
      showBottomSheet.value = false
    }
    // Swipe up to show (when hidden)
    else if (deltaY < -SWIPE_THRESHOLD && velocity > SWIPE_VELOCITY_THRESHOLD && !showBottomSheet.value) {
      showBottomSheet.value = true
    }
    
    isDragging = false
  }

  const toggleBottomSheet = () => {
    showBottomSheet.value = !showBottomSheet.value
  }

  // Menu control
  const toggleMenu = () => {
    showMenu.value = !showMenu.value
  }

  // Navigation methods
  const showNotifications = (router) => {
    router.push('/driver/notifications')
  }

  const goToHistory = (router) => {
    showMenu.value = false
    router.push('/driver/history')
  }

  const goToEarnings = (router) => {
    showMenu.value = false
    router.push('/driver/earnings')
  }

  const goToSupport = (router) => {
    showMenu.value = false
    router.push('/driver/support')
  }

  const goToProfile = (router) => {
    showMenu.value = false
    router.push('/driver/profile')
  }

  const logout = async (router, authStore) => {
    // Set driver to offline before logging out
    try {
      const { driverAPI } = await import('@/services/api')
      await driverAPI.updateStatus('offline')
      console.log('✅ Driver set to offline on logout')
    } catch (error) {
      console.error('❌ Failed to set driver offline on logout:', error)
    }
    
    authStore.logout()
    router.push('/login')
  }

  return {
    // State
    showMenu,
    showBottomSheet,
    unreadNotifications,
    
    // Methods
    handleMapClick,
    handleBottomSheetTouchStart,
    handleBottomSheetTouchMove,
    handleBottomSheetTouchEnd,
    toggleBottomSheet,
    toggleMenu,
    showNotifications,
    goToHistory,
    goToEarnings,
    goToSupport,
    goToProfile,
    logout
  }
}
