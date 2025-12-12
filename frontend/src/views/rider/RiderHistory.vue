<template>
  <div class="rider-history">
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

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading your trips...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="trips.length === 0" class="empty-state">
      <svg xmlns="http://www.w3.org/2000/svg" class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
      <h3>No trips yet</h3>
      <p>Your trip history will appear here once you complete your first ride.</p>
      <button @click="goBack" class="btn-primary">Request a Ride</button>
    </div>

    <!-- Trip List -->
    <div v-else class="trips-container">
      <!-- Stats Summary -->
      <div class="stats-summary">
        <div class="stat-card">
          <div class="stat-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ trips.length }}</div>
            <div class="stat-label">Total Trips</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ totalSpent.toFixed(2) }} TND</div>
            <div class="stat-label">Total Spent</div>
          </div>
        </div>
      </div>

      <!-- Trip Cards -->
      <div class="trips-list">
        <div v-for="trip in trips" :key="trip.id" class="trip-card" :class="`status-${trip.status}`">
          <!-- Trip Status Badge -->
          <div class="trip-status-badge" :class="`badge-${trip.status}`">
            {{ getStatusText(trip.status) }}
          </div>

          <!-- Trip Details -->
          <div class="trip-info">
            <div class="trip-route">
              <div class="route-point pickup">
                <div class="route-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="route-text">
                  <div class="route-label">Pickup</div>
                  <div class="route-address">{{ trip.pickup_address }}</div>
                </div>
              </div>

              <div class="route-line"></div>

              <div class="route-point destination">
                <div class="route-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="route-text">
                  <div class="route-label">Destination</div>
                  <div class="route-address">{{ trip.destination_address }}</div>
                </div>
              </div>
            </div>

            <!-- Driver Info -->
            <div v-if="trip.driver" class="driver-info">
              <svg xmlns="http://www.w3.org/2000/svg" class="driver-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <span>{{ trip.driver.name }} - Taxi {{ trip.driver.taxi_number }}</span>
            </div>

            <!-- Trip Metadata -->
            <div class="trip-metadata">
              <div class="metadata-item">
                <svg xmlns="http://www.w3.org/2000/svg" class="metadata-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{{ formatDate(trip.requested_at) }}</span>
              </div>

              <div class="metadata-item">
                <svg xmlns="http://www.w3.org/2000/svg" class="metadata-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                </svg>
                <span>{{ trip.estimated_distance_km?.toFixed(1) || '0.0' }} km</span>
              </div>

              <div class="metadata-item cost">
                <svg xmlns="http://www.w3.org/2000/svg" class="metadata-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="cost-value">{{ trip.estimated_cost_tnd?.toFixed(2) || '0.00' }} TND</span>
              </div>
            </div>

            <!-- Rating (if completed) -->
            <div v-if="trip.status === 'completed' && trip.driver_rating" class="trip-rating">
              <span class="rating-label">Your Rating:</span>
              <div class="stars">
                <svg v-for="star in 5" :key="star" 
                     class="star" :class="{ filled: star <= trip.driver_rating }"
                     xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Load More Button -->
      <button v-if="hasMore" @click="loadMore" class="btn-load-more" :disabled="loadingMore">
        <span v-if="loadingMore">Loading...</span>
        <span v-else>Load More</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import riderService from '@/services/riderService'

const router = useRouter()

// State
const trips = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const offset = ref(0)
const limit = 20
const hasMore = ref(true)

// Computed
const totalSpent = computed(() => {
  return trips.value
    .filter(trip => trip.status === 'completed')
    .reduce((sum, trip) => sum + (trip.estimated_cost_tnd || 0), 0)
})

// Methods
const goBack = () => {
  router.push('/rider/dashboard')
}

const loadTrips = async (isLoadMore = false) => {
  try {
    if (isLoadMore) {
      loadingMore.value = true
    } else {
      loading.value = true
    }

    const response = await riderService.getTripHistory(limit, offset.value)
    
    if (response.success) {
      if (isLoadMore) {
        trips.value.push(...response.trips)
      } else {
        trips.value = response.trips
      }

      // Check if there are more trips to load
      hasMore.value = response.trips.length === limit
    }
  } catch (error) {
    console.error('Error loading trip history:', error)
    window.$notification?.error('Failed to load trip history', {
      title: 'Error'
    })
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const loadMore = () => {
  offset.value += limit
  loadTrips(true)
}

const getStatusText = (status) => {
  const statusMap = {
    'completed': 'Completed',
    'cancelled': 'Cancelled',
    'assigned': 'Assigned',
    'requested': 'Requested',
    'started': 'In Progress'
  }
  return statusMap[status] || status
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 60) return `${diffMins} min ago`
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
  
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  })
}

// Lifecycle
onMounted(() => {
  loadTrips()
})
</script>

<style scoped>
.rider-history {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a1f1a 0%, #051510 100%);
  padding-bottom: 2rem;
}

/* Header */
.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  background: rgba(26, 77, 58, 0.3);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 208, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 10;
}

.btn-back {
  background: none;
  border: none;
  color: #ffd000;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  transition: background-color 0.2s;
}

.btn-back:hover {
  background: rgba(255, 208, 0, 0.1);
}

.btn-back svg {
  width: 1.5rem;
  height: 1.5rem;
}

.header-title {
  color: white;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.header-spacer {
  width: 2.5rem;
}

/* Loading State */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  color: white;
}

.spinner {
  width: 3rem;
  height: 3rem;
  border: 3px solid rgba(255, 208, 0, 0.2);
  border-top-color: #ffd000;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 2rem;
  text-align: center;
}

.empty-icon {
  width: 5rem;
  height: 5rem;
  color: rgba(255, 208, 0, 0.3);
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: white;
  font-size: 1.5rem;
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 2rem 0;
}

.btn-primary {
  background: #ffd000;
  color: #0a1f1a;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.btn-primary:hover {
  transform: translateY(-2px);
}

/* Stats Summary */
.stats-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  padding: 1.5rem;
}

.stat-card {
  background: rgba(26, 77, 58, 0.3);
  border: 1px solid rgba(255, 208, 0, 0.2);
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  width: 3rem;
  height: 3rem;
  background: rgba(255, 208, 0, 0.1);
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon svg {
  width: 1.5rem;
  height: 1.5rem;
  color: #ffd000;
}

.stat-content {
  flex: 1;
}

.stat-value {
  color: white;
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.stat-label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.875rem;
}

/* Trips List */
.trips-container {
  padding: 0 1.5rem 1.5rem;
}

.trips-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1rem;
}

.trip-card {
  background: rgba(26, 77, 58, 0.3);
  border: 1px solid rgba(255, 208, 0, 0.2);
  border-radius: 1rem;
  padding: 1.5rem;
  position: relative;
  transition: transform 0.2s, box-shadow 0.2s;
}

.trip-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.trip-status-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  padding: 0.375rem 0.875rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge-completed {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.badge-cancelled {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.badge-requested, .badge-assigned, .badge-started {
  background: rgba(255, 208, 0, 0.2);
  color: #ffd000;
  border: 1px solid rgba(255, 208, 0, 0.3);
}

/* Trip Route */
.trip-route {
  margin-bottom: 1rem;
}

.route-point {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.route-icon {
  width: 2rem;
  height: 2rem;
  background: rgba(255, 208, 0, 0.1);
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.route-icon svg {
  width: 1.25rem;
  height: 1.25rem;
  color: #ffd000;
}

.route-text {
  flex: 1;
}

.route-label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.25rem;
}

.route-address {
  color: white;
  font-size: 0.9375rem;
  line-height: 1.4;
}

.route-line {
  width: 2px;
  height: 1rem;
  background: linear-gradient(180deg, rgba(255, 208, 0, 0.5) 0%, rgba(255, 208, 0, 0.1) 100%);
  margin-left: 0.96rem;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}

/* Driver Info */
.driver-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: rgba(255, 208, 0, 0.05);
  border-radius: 0.5rem;
  margin-bottom: 1rem;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.875rem;
}

.driver-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: #ffd000;
  flex-shrink: 0;
}

/* Trip Metadata */
.trip-metadata {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.metadata-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.875rem;
}

.metadata-icon {
  width: 1rem;
  height: 1rem;
  color: rgba(255, 208, 0, 0.7);
}

.metadata-item.cost {
  margin-left: auto;
}

.cost-value {
  color: #ffd000;
  font-weight: 700;
  font-size: 1.125rem;
}

/* Rating */
.trip-rating {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.rating-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.875rem;
}

.stars {
  display: flex;
  gap: 0.25rem;
}

.star {
  width: 1.25rem;
  height: 1.25rem;
  color: rgba(255, 208, 0, 0.3);
  transition: color 0.2s;
}

.star.filled {
  color: #ffd000;
}

/* Load More Button */
.btn-load-more {
  width: 100%;
  padding: 1rem;
  background: rgba(26, 77, 58, 0.5);
  border: 1px solid rgba(255, 208, 0, 0.3);
  border-radius: 0.75rem;
  color: #ffd000;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-load-more:hover:not(:disabled) {
  background: rgba(26, 77, 58, 0.7);
  transform: translateY(-2px);
}

.btn-load-more:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 640px) {
  .stats-summary {
    grid-template-columns: 1fr;
  }

  .trip-status-badge {
    position: static;
    width: fit-content;
    margin-bottom: 1rem;
  }

  .trip-metadata {
    flex-direction: column;
    gap: 0.75rem;
  }

  .metadata-item.cost {
    margin-left: 0;
  }
}
</style>
