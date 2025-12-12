/**
 * UI state management composable
 * Handles UI visibility and interactions
 */
import { ref } from 'vue'

export function useUIState() {
  // UI state
  const showSideMenu = ref(false)
  const showBottomSheet = ref(true)

  // Touch gesture tracking
  let touchStartY = 0
  let touchStartTime = 0
  let isDragging = false
  const SWIPE_THRESHOLD = 50
  const SWIPE_VELOCITY_THRESHOLD = 0.5

  /**
   * Handle map click to hide bottom sheet, drivers list, and trip details
   */
  const handleMapClick = (event, showTripDetails = null) => {
    if (event.target.classList.contains('mapboxgl-canvas') ||
        event.target.classList.contains('map-container')) {
      if (showBottomSheet.value) {
        showBottomSheet.value = false
      }
      if (showSideMenu.value) {
        showSideMenu.value = false
      }
      // Hide trip details if provided and currently showing
      if (showTripDetails && showTripDetails.value) {
        showTripDetails.value = false
      }
    }
  }

  /**
   * Handle bottom sheet touch start
   */
  const handleBottomSheetTouchStart = (event) => {
    isDragging = false
    touchStartY = event.touches[0].clientY
    touchStartTime = Date.now()
  }

  /**
   * Handle bottom sheet touch move
   */
  const handleBottomSheetTouchMove = (event) => {
    isDragging = true
  }

  /**
   * Handle bottom sheet touch end
   */
  const handleBottomSheetTouchEnd = (event) => {
    if (!isDragging) return

    const touchEndY = event.changedTouches[0].clientY
    const touchEndTime = Date.now()
    const deltaY = touchEndY - touchStartY
    const deltaTime = touchEndTime - touchStartTime
    const velocity = Math.abs(deltaY) / deltaTime

    if (deltaY > SWIPE_THRESHOLD && velocity > SWIPE_VELOCITY_THRESHOLD) {
      showBottomSheet.value = false
    } else if (deltaY < -SWIPE_THRESHOLD && velocity > SWIPE_VELOCITY_THRESHOLD && !showBottomSheet.value) {
      showBottomSheet.value = true
    }

    isDragging = false
  }

  /**
   * Toggle bottom sheet visibility
   */
  const toggleBottomSheet = () => {
    showBottomSheet.value = !showBottomSheet.value
  }

  return {
    // State
    showSideMenu,
    showBottomSheet,

    // Methods
    handleMapClick,
    handleBottomSheetTouchStart,
    handleBottomSheetTouchMove,
    handleBottomSheetTouchEnd,
    toggleBottomSheet
  }
}
