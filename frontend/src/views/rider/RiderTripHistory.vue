<template>
  <div class="rider-trip-history">
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

      <!-- Error State -->
      <div v-else-if="error" class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" class="empty-icon text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 class="empty-title">Failed to load trips</h3>
        <p class="empty-subtitle">{{ error }}</p>
        <button @click="fetchTripHistory" class="btn-retry">Retry</button>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredTrips.length === 0" class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <h3 class="empty-title">No trips found</h3>
        <p class="empty-subtitle">You haven't taken any trips yet</p>
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
              <span>{{ trip.driver_name }}</span>
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

          <!-- Cost -->
          <div class="trip-cost">
            <span class="cost-label">Total Cost:</span>
            <span class="cost-amount">{{ trip.cost.toFixed(2) }} TND</span>
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
              <h3 class="section-title">Driver</h3>
              <div class="detail-row">
                <span class="detail-label">Name:</span>
                <span class="detail-value">{{ selectedTrip.driver_name }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Vehicle:</span>
                <span class="detail-value">{{ selectedTrip.taxi_number }}</span>
              </div>
            </div>

            <div class="detail-section">
              <h3 class="section-title">Payment</h3>
              <div class="detail-row">
                <span class="detail-label">Base Fare:</span>
                <span class="detail-value">{{ selectedTrip.base_fare.toFixed(2) }} TND</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Distance Fee:</span>
                <span class="detail-value">{{ selectedTrip.distance_fee.toFixed(2) }} TND</span>
              </div>
              <div class="detail-row total">
                <span class="detail-label">Total Cost:</span>
                <span class="detail-value highlight">{{ selectedTrip.cost.toFixed(2) }} TND</span>
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
import { riderAPI } from '@/services/api'

const router = useRouter()

// State
const loading = ref(false)
const error = ref(null)
const selectedDateRange = ref('month')
const selectedStatus = ref('all')
const selectedTrip = ref(null)
const currentPage = ref(1)
const tripsPerPage = 10

// Backend data
const allTrips = ref([])
const totalTrips = ref(0)

// Fetch trips from backend
const fetchTripHistory = async () => {
  loading.value = true
  error.value = null
  
  try {
    console.log('📜 Fetching trip history from backend...')
    
    // Calculate offset based on current page
    const offset = (currentPage.value - 1) * tripsPerPage
    
    // Fetch from backend
    const response = await riderAPI.getTripHistory(tripsPerPage, offset)
    
    console.log('✅ Trip history response:', response.data)
    
    if (response.data && response.data.trips) {
      // Map backend response to frontend format
      allTrips.value = response.data.trips.map(trip => ({
        id: trip.id,
        date: new Date(trip.created_at || trip.updated_at),
        pickup: trip.pickup_address || 'Pickup location',
        destination: trip.destination_address || 'Destination',
        driver_name: trip.driver?.name || trip.driver?.full_name || 'Driver',
        taxi_number: trip.driver?.taxi_number || 'N/A',
        cost: trip.estimated_cost || trip.final_cost || 0,
        base_fare: 5.00, // Default base fare (could come from settings)
        distance_fee: (trip.estimated_cost || trip.final_cost || 0) - 5.00,
        status: trip.status,
        distance: trip.distance || 0,
        duration: trip.duration || 'N/A'
      }))
      
      totalTrips.value = response.data.total || allTrips.value.length
    } else {
      allTrips.value = []
      totalTrips.value = 0
    }
    
    console.log(`✅ Loaded ${allTrips.value.length} trips`)
  } catch (err) {
    console.error('❌ Error fetching trip history:', err)
    error.value = err.message || 'Failed to load trip history'
    allTrips.value = []
  } finally {
    loading.value = false
  }
}

// Watch for page changes
watch(currentPage, () => {
  fetchTripHistory()
})

// Watch for filter changes
watch([selectedStatus, selectedDateRange], () => {
  currentPage.value = 1 // Reset to first page
  fetchTripHistory()
})

// Computed
const filteredTrips = computed(() => {
  let trips = allTrips.value

  // Filter by status
  if (selectedStatus.value !== 'all') {
    trips = trips.filter(t => t.status === selectedStatus.value)
  }

  // Filter by date range
  const now = new Date()
  if (selectedDateRange.value === 'today') {
    trips = trips.filter(t => {
      const tripDate = new Date(t.date)
      return tripDate.toDateString() === now.toDateString()
    })
  } else if (selectedDateRange.value === 'week') {
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    trips = trips.filter(t => new Date(t.date) >= weekAgo)
  } else if (selectedDateRange.value === 'month') {
    const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
    trips = trips.filter(t => new Date(t.date) >= monthAgo)
  }

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

// Lifecycle
onMounted(() => {
  fetchTripHistory()
})
</script>

<style scoped src="./RiderTripHistory.css"></style>

