<template>
  <div class="driver-trip-history">
    <!-- Header -->
    <div class="history-header">
      <button @click="goBack" class="btn-back">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <h1 class="header-title">Trip History</h1>
      <div class="header-spacer"></div>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filter-group">
        <label class="filter-label">Date Range</label>
        <select v-model="selectedDateRange" class="filter-select">
          <option value="today">Today</option>
          <option value="week">This Week</option>
          <option value="month">This Month</option>
          <option value="all">All Time</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label class="filter-label">Status</label>
        <select v-model="selectedStatus" class="filter-select">
          <option value="all">All</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>
    </div>

    <!-- Content -->
    <div class="history-content">
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading trips...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredTrips.length === 0" class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <h3 class="empty-title">No trips found</h3>
        <p class="empty-subtitle">You haven't completed any trips yet</p>
      </div>

      <!-- Trip Cards -->
      <div v-else class="trips-list">
        <div 
          v-for="trip in paginatedTrips" 
          :key="trip.id"
          class="trip-card"
          @click="viewTripDetails(trip)"
        >
          <!-- Date & Time -->
          <div class="trip-header">
            <div class="trip-date">
              <svg xmlns="http://www.w3.org/2000/svg" class="date-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>{{ formatDate(trip.date) }}</span>
            </div>
            <div class="status-badge" :class="trip.status">
              {{ trip.status }}
            </div>
          </div>

          <!-- Route -->
          <div class="trip-route">
            <div class="route-point pickup">
              <svg xmlns="http://www.w3.org/2000/svg" class="route-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <div class="route-address">{{ trip.pickup }}</div>
            </div>
            <svg xmlns="http://www.w3.org/2000/svg" class="route-arrow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
            <div class="route-point destination">
              <svg xmlns="http://www.w3.org/2000/svg" class="route-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
              <div class="route-address">{{ trip.destination }}</div>
            </div>
          </div>

          <!-- Details -->
          <div class="trip-details">
            <div class="detail-item">
              <svg xmlns="http://www.w3.org/2000/svg" class="detail-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <span>{{ trip.rider_name }}</span>
            </div>
            <div class="detail-item">
              <svg xmlns="http://www.w3.org/2000/svg" class="detail-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
              <span>{{ trip.distance }} km</span>
            </div>
            <div class="detail-item">
              <svg xmlns="http://www.w3.org/2000/svg" class="detail-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{{ trip.duration }}</span>
            </div>
          </div>

          <!-- Earnings -->
          <div class="trip-earnings">
            <span class="earnings-label">Earned:</span>
            <span class="earnings-amount">{{ trip.earnings.toFixed(2) }} TND</span>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="filteredTrips.length > tripsPerPage" class="pagination">
        <button 
          @click="currentPage--" 
          :disabled="currentPage === 1"
          class="pagination-btn"
        >
          Previous
        </button>
        <span class="pagination-info">
          Page {{ currentPage }} of {{ totalPages }}
        </span>
        <button 
          @click="currentPage++" 
          :disabled="currentPage === totalPages"
          class="pagination-btn"
        >
          Next
        </button>
      </div>
    </div>

    <!-- Trip Details Modal -->
    <transition name="modal-fade">
      <div v-if="selectedTrip" class="trip-modal" @click="selectedTrip = null">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h2 class="modal-title">Trip Details</h2>
            <button @click="selectedTrip = null" class="btn-close">✕</button>
          </div>

          <div class="modal-body">
            <div class="detail-section">
              <h3 class="section-title">Trip Information</h3>
              <div class="detail-row">
                <span class="detail-label">Trip ID:</span>
                <span class="detail-value">{{ selectedTrip.id }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Date & Time:</span>
                <span class="detail-value">{{ formatFullDate(selectedTrip.date) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Status:</span>
                <span class="status-badge" :class="selectedTrip.status">{{ selectedTrip.status }}</span>
              </div>
            </div>

            <div class="detail-section">
              <h3 class="section-title">Route</h3>
              <div class="detail-row">
                <span class="detail-label">Pickup:</span>
                <span class="detail-value">{{ selectedTrip.pickup }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Destination:</span>
                <span class="detail-value">{{ selectedTrip.destination }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Distance:</span>
                <span class="detail-value">{{ selectedTrip.distance }} km</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Duration:</span>
                <span class="detail-value">{{ selectedTrip.duration }}</span>
              </div>
            </div>

            <div class="detail-section">
              <h3 class="section-title">Passenger</h3>
              <div class="detail-row">
                <span class="detail-label">Name:</span>
                <span class="detail-value">{{ selectedTrip.rider_name }}</span>
              </div>
            </div>

            <div class="detail-section">
              <h3 class="section-title">Earnings</h3>
              <div class="detail-row">
                <span class="detail-label">Total Fare:</span>
                <span class="detail-value">{{ selectedTrip.earnings.toFixed(2) }} TND</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Commission (20%):</span>
                <span class="detail-value negative">-{{ (selectedTrip.earnings * 0.2).toFixed(2) }} TND</span>
              </div>
              <div class="detail-row total">
                <span class="detail-label">Your Earnings:</span>
                <span class="detail-value highlight">{{ (selectedTrip.earnings * 0.8).toFixed(2) }} TND</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()

// State
const loading = ref(false)
const selectedDateRange = ref('all')
const selectedStatus = ref('all')
const selectedTrip = ref(null)
const currentPage = ref(1)
const tripsPerPage = 10
const allTrips = ref([])

// Fetch trips from API
const fetchTrips = async () => {
  loading.value = true
  try {
    const statusFilter = selectedStatus.value !== 'all' ? selectedStatus.value : null
    const params = {
      limit: 50, // Backend max is 50
      offset: 0
    }
    if (statusFilter) {
      params.status = statusFilter
    }
    
    const response = await api.get('/drivers/trip-history', { params })
    
    console.log('Trip history response:', response)
    
    // Note: axios interceptor already extracts response.data, so response IS the data
    if (response && response.success && response.trips && response.trips.length > 0) {
      console.log('Trips array:', response.trips)
      console.log('Trips length:', response.trips.length)
      console.log('First trip:', response.trips[0])
      
      // Transform API data to match component format
      allTrips.value = response.trips.map(trip => {
        // Use the most recent timestamp available
        const tripDate = trip.completed_at || trip.cancelled_at || trip.started_at || trip.accepted_at || trip.assigned_at || trip.requested_at
        
        return {
          id: trip.id,
          date: tripDate,
          pickup: trip.pickup_address || 'Unknown Location',
          destination: trip.destination_address || 'Unknown Location',
          rider_name: trip.rider_name || 'Unknown',
          earnings: trip.estimated_cost_tnd || 0,
          status: trip.status,
          distance: trip.estimated_distance_km || 0,
          duration: calculateDuration(trip.started_at, trip.completed_at),
          // Additional fields for modal
          requested_at: trip.requested_at,
          assigned_at: trip.assigned_at,
          accepted_at: trip.accepted_at,
          started_at: trip.started_at,
          completed_at: trip.completed_at,
          cancelled_at: trip.cancelled_at,
          rider_notes: trip.rider_notes,
          driver_notes: trip.driver_notes,
          rider_rating: trip.rider_rating,
          driver_rating: trip.driver_rating
        }
      })
      console.log('Transformed trips:', allTrips.value.length)
      if (allTrips.value.length > 0) {
        console.log('First transformed trip:', allTrips.value[0])
      }
    } else {
      console.warn('No trips in response:', response)
      allTrips.value = []
    }
  } catch (error) {
    console.error('Failed to fetch trip history:', error)
    if (error.response) {
      console.error('Error response:', error.response.status, error.response.data)
    }
    allTrips.value = []
  } finally {
    loading.value = false
  }
}

// Calculate trip duration
const calculateDuration = (startedAt, completedAt) => {
  if (!startedAt || !completedAt) return 'N/A'
  const start = new Date(startedAt)
  const end = new Date(completedAt)
  const durationMs = end - start
  const minutes = Math.floor(durationMs / 60000)
  return `${minutes}m`
}

// Watch for status changes to refetch
watch(selectedStatus, () => {
  currentPage.value = 1
  fetchTrips()
})

// Load trips on mount
onMounted(() => {
  fetchTrips()
})

// Computed
const filteredTrips = computed(() => {
  let trips = allTrips.value
  console.log('filteredTrips - starting with:', trips.length, 'trips')
  console.log('selectedStatus:', selectedStatus.value)
  console.log('selectedDateRange:', selectedDateRange.value)

  // Filter by status
  if (selectedStatus.value !== 'all') {
    trips = trips.filter(t => t.status === selectedStatus.value)
    console.log('After status filter:', trips.length)
  }

  // Filter by date range
  const now = new Date()
  if (selectedDateRange.value === 'today') {
    trips = trips.filter(t => {
      const tripDate = new Date(t.date)
      return tripDate.toDateString() === now.toDateString()
    })
    console.log('After today filter:', trips.length)
  } else if (selectedDateRange.value === 'week') {
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    trips = trips.filter(t => new Date(t.date) >= weekAgo)
    console.log('After week filter:', trips.length)
  } else if (selectedDateRange.value === 'month') {
    const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
    trips = trips.filter(t => new Date(t.date) >= monthAgo)
    console.log('After month filter:', trips.length)
  }

  console.log('Final filtered trips:', trips.length)
  return trips.sort((a, b) => new Date(b.date) - new Date(a.date))
})

const totalPages = computed(() => Math.ceil(filteredTrips.value.length / tripsPerPage))

const paginatedTrips = computed(() => {
  const start = (currentPage.value - 1) * tripsPerPage
  const end = start + tripsPerPage
  return filteredTrips.value.slice(start, end)
})

// Methods
const goBack = () => {
  router.back()
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatFullDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', { 
    weekday: 'long',
    year: 'numeric',
    month: 'long', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const viewTripDetails = (trip) => {
  selectedTrip.value = trip
}
</script>

<style scoped src="./DriverTripHistory.css"></style>
