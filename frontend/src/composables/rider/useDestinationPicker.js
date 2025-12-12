/**
 * Destination picker composable
 * Handles destination selection from map
 */
import { ref } from 'vue'

export function useDestinationPicker() {
  // State
  const destination = ref('')
  const isPickingDestination = ref(false)
  const tempDestinationCoords = ref(null)
  const showDestinationConfirmation = ref(false)
  const showDestinationSuggestions = ref(false)

  const destinationSuggestions = ref([
    { name: 'Tunis Carthage Airport', address: 'Tunis, Tunisia' },
    { name: 'La Marsa Beach', address: 'La Marsa, Tunisia' },
    { name: 'Medina of Tunis', address: 'Tunis, Tunisia' },
    { name: 'Carthage Ruins', address: 'Carthage, Tunisia' },
    { name: 'Sidi Bou Said', address: 'Sidi Bou Said, Tunisia' }
  ])

  /**
   * Enable destination picking mode
   */
  const enableDestinationPicker = (map, hideBottomSheet) => {
    if (hideBottomSheet) hideBottomSheet()
    isPickingDestination.value = true
    showDestinationSuggestions.value = false

    if (map) {
      map.getCanvas().style.cursor = 'crosshair'
    }
  }

  /**
   * Handle map click for destination selection
   */
  const onMapClickForDestination = (e, map, setMarkerCallback) => {
    if (!isPickingDestination.value && !showDestinationConfirmation.value) return

    const { lng, lat } = e.lngLat
    tempDestinationCoords.value = { lng, lat }

    // Set destination marker
    if (setMarkerCallback) {
      setMarkerCallback(lng, lat)
    }

    // Update destination text
    destination.value = `${lat.toFixed(4)}, ${lng.toFixed(4)}`

    // Keep cursor as crosshair
    if (map) {
      map.getCanvas().style.cursor = 'crosshair'
    }
    
    showDestinationConfirmation.value = true
  }

  /**
   * Confirm selected destination
   */
  const confirmDestination = (map, showBottomSheet) => {
    showDestinationConfirmation.value = false
    isPickingDestination.value = false

    if (map) {
      map.off('click', onMapClickForDestination)
      map.getCanvas().style.cursor = ''
    }

    if (showBottomSheet) showBottomSheet()

    console.log('Destination confirmed:', tempDestinationCoords.value)
  }

  /**
   * Cancel destination selection
   */
  const cancelDestination = (map, removeMarkerCallback, showBottomSheet) => {
    // Remove marker
    if (removeMarkerCallback) {
      removeMarkerCallback()
    }

    destination.value = ''
    tempDestinationCoords.value = null
    showDestinationConfirmation.value = false
    isPickingDestination.value = false

    if (map) {
      map.off('click', onMapClickForDestination)
      map.getCanvas().style.cursor = ''
    }

    if (showBottomSheet) showBottomSheet()
  }

  /**
   * Select destination from suggestions
   */
  const selectDestination = (suggestion) => {
    destination.value = suggestion.name
    showDestinationSuggestions.value = false
  }

  return {
    // State
    destination,
    isPickingDestination,
    tempDestinationCoords,
    showDestinationConfirmation,
    showDestinationSuggestions,
    destinationSuggestions,

    // Methods
    enableDestinationPicker,
    onMapClickForDestination,
    confirmDestination,
    cancelDestination,
    selectDestination
  }
}
