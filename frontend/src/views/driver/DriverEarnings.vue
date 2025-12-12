<template>
  <div class="driver-earnings">
    <!-- Header -->
    <div class="earnings-header">
      <button @click="goBack" class="btn-back">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <h1 class="header-title">Earnings</h1>
      <div class="header-spacer"></div>
    </div>

    <!-- Content -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading earnings...</p>
    </div>

    <div v-else-if="error" class="error-container">
      <svg xmlns="http://www.w3.org/2000/svg" class="error-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
      <h3>Failed to load earnings</h3>
      <p>{{ error }}</p>
      <button @click="fetchEarnings" class="btn-retry">Try Again</button>
    </div>

    <div v-else class="earnings-content">
      <!-- Today's Stats Card -->
      <div class="stats-card today-stats">
        <div class="stats-header">
          <h2 class="stats-title">Today's Earnings</h2>
          <span class="stats-date">{{ todayDate }}</span>
        </div>
        
        <div class="main-earning">
          <div class="earning-amount">{{ todayEarnings.toFixed(2) }} TND</div>
          <div class="earning-subtitle">Total earned today</div>
        </div>

        <div class="quick-stats">
          <div class="quick-stat-item">
            <div class="stat-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2" />
              </svg>
            </div>
            <div class="stat-value">{{ todayTrips }}</div>
            <div class="stat-label">Trips</div>
          </div>
          <div class="quick-stat-item">
            <div class="stat-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="stat-value">{{ todayHours.toFixed(1) }}h</div>
            <div class="stat-label">Online</div>
          </div>
          <div class="quick-stat-item">
            <div class="stat-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
            </div>
            <div class="stat-value">{{ avgRating.toFixed(1) }}</div>
            <div class="stat-label">Rating</div>
          </div>
        </div>
      </div>

      <!-- Period Selector -->
      <div class="period-selector">
        <button 
          v-for="period in periods" 
          :key="period.value"
          @click="selectedPeriod = period.value"
          class="period-btn"
          :class="{ active: selectedPeriod === period.value }"
        >
          {{ period.label }}
        </button>
      </div>

      <!-- Earnings Chart -->
      <div class="chart-card">
        <h3 class="card-title">Earnings Trend</h3>
        <div class="chart-container">
          <div class="chart-bars">
            <div v-for="(day, index) in chartData" :key="index" class="chart-bar-wrapper">
              <div class="chart-bar">
                <div class="bar-fill" :style="{ height: day.percentage + '%' }">
                  <span class="bar-value">{{ day.value }}</span>
                </div>
              </div>
              <span class="bar-label">{{ day.label }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Detailed Breakdown -->
      <div class="breakdown-card">
        <h3 class="card-title">{{ selectedPeriod === 'week' ? 'Weekly' : 'Monthly' }} Breakdown</h3>
        
        <div class="breakdown-item">
          <div class="breakdown-icon total">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="breakdown-info">
            <div class="breakdown-label">Total Fare Collected</div>
            <div class="breakdown-value">{{ totalFare.toFixed(2) }} TND</div>
          </div>
        </div>

        <div class="breakdown-item">
          <div class="breakdown-icon commission">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div class="breakdown-info">
            <div class="breakdown-label">Platform Commission ({{ commissionRate }}%)</div>
            <div class="breakdown-value negative">-{{ commission.toFixed(2) }} TND</div>
          </div>
        </div>

        <div class="breakdown-divider"></div>

        <div class="breakdown-item total">
          <div class="breakdown-icon net">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="breakdown-info">
            <div class="breakdown-label">Net Earnings (Take-home)</div>
            <div class="breakdown-value highlight">{{ netEarnings.toFixed(2) }} TND</div>
          </div>
        </div>
      </div>

      <!-- Peak Hours Analysis -->
      <div class="peak-hours-card">
        <h3 class="card-title">Peak Hours Analysis</h3>
        
        <div class="peak-hour-item" :class="{ best: bestPeriod === 'morning' }">
          <div class="peak-hour-time">
            <div class="time-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
              </svg>
            </div>
            <span class="time-label">Morning (6AM - 12PM)</span>
            <span v-if="bestPeriod === 'morning'" class="best-badge">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z" />
              </svg>
              Best
            </span>
          </div>
          <div class="peak-hour-stats">
            <div class="peak-stat">
              <span class="peak-trips">{{ peakHours.morning.trips }} trips</span>
              <span class="peak-earnings">{{ peakHours.morning.earnings }} TND</span>
            </div>
          </div>
        </div>

        <div class="peak-hour-item" :class="{ best: bestPeriod === 'afternoon' }">
          <div class="peak-hour-time">
            <div class="time-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <span class="time-label">Afternoon (12PM - 6PM)</span>
            <span v-if="bestPeriod === 'afternoon'" class="best-badge">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z" />
              </svg>
              Best
            </span>
          </div>
          <div class="peak-hour-stats">
            <div class="peak-stat">
              <span class="peak-trips">{{ peakHours.afternoon.trips }} trips</span>
              <span class="peak-earnings">{{ peakHours.afternoon.earnings }} TND</span>
            </div>
          </div>
        </div>

        <div class="peak-hour-item" :class="{ best: bestPeriod === 'evening' }">
          <div class="peak-hour-time">
            <div class="time-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            </div>
            <span class="time-label">Evening (6PM - 12AM)</span>
            <span v-if="bestPeriod === 'evening'" class="best-badge">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z" />
              </svg>
              Best
            </span>
          </div>
          <div class="peak-hour-stats">
            <div class="peak-stat">
              <span class="peak-trips">{{ peakHours.evening.trips }} trips</span>
              <span class="peak-earnings">{{ peakHours.evening.earnings }} TND</span>
            </div>
          </div>
        </div>

        <div class="peak-hour-item" :class="{ best: bestPeriod === 'night' }">
          <div class="peak-hour-time">
            <div class="time-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
            </div>
            <span class="time-label">Night (12AM - 6AM)</span>
            <span v-if="bestPeriod === 'night'" class="best-badge">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z" />
              </svg>
              Best
            </span>
          </div>
          <div class="peak-hour-stats">
            <div class="peak-stat">
              <span class="peak-trips">{{ peakHours.night.trips }} trips</span>
              <span class="peak-earnings">{{ peakHours.night.earnings }} TND</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import driverService from '@/services/driverService'

const router = useRouter()

const todayDate = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })

// Loading state
const loading = ref(true)
const error = ref(null)

// Today's Stats (computed from backend data)
const todayEarnings = ref(0)
const todayTrips = ref(0)
const todayHours = ref(0)
const avgRating = ref(0)

// Period Selection
const selectedPeriod = ref('week')
const periods = [
  { label: 'Week', value: 'week' },
  { label: 'Month', value: 'month' }
]

// Backend data
const earningsData = ref(null)

// Fetch earnings data from backend
const fetchEarnings = async () => {
  loading.value = true
  error.value = null
  
  try {
    const result = await driverService.getEarnings(selectedPeriod.value)
    
    if (result.success && result.data) {
      earningsData.value = result.data
      
      // Update stats from backend data
      avgRating.value = result.data.avg_rating || 0
      
      // If we have peak hours data, calculate today's stats
      if (result.data.peak_hours) {
        const allHours = Object.values(result.data.peak_hours)
        todayTrips.value = allHours.reduce((sum, h) => sum + (h.trips || 0), 0)
        todayEarnings.value = allHours.reduce((sum, h) => sum + (h.earnings || 0), 0)
        todayHours.value = allHours.reduce((sum, h) => sum + (h.hours || 0), 0)
      }
    } else {
      error.value = result.error || 'Failed to load earnings data'
    }
  } catch (err) {
    console.error('Error fetching earnings:', err)
    error.value = err.message || 'An error occurred while loading earnings'
  } finally {
    loading.value = false
  }
}

// Watch period changes
watch(selectedPeriod, () => {
  fetchEarnings()
})

// Chart Data (from backend)
const chartData = computed(() => {
  if (!earningsData.value?.peak_hours) {
    return []
  }
  
  const hours = earningsData.value.peak_hours
  const values = [
    { label: 'Morning', value: hours.morning?.earnings || 0, period: 'morning' },
    { label: 'Afternoon', value: hours.afternoon?.earnings || 0, period: 'afternoon' },
    { label: 'Evening', value: hours.evening?.earnings || 0, period: 'evening' },
    { label: 'Night', value: hours.night?.earnings || 0, period: 'night' }
  ]
  
  // Calculate percentages based on max value
  const maxValue = Math.max(...values.map(v => v.value), 1)
  return values.map(v => ({
    ...v,
    percentage: (v.value / maxValue) * 100
  }))
})

// Breakdown Data (from backend)
const totalFare = computed(() => earningsData.value?.total_fare || 0)
const commission = computed(() => earningsData.value?.commission || 0)
const netEarnings = computed(() => earningsData.value?.net_earnings || 0)
const commissionRate = computed(() => earningsData.value?.commission_rate || 20)

// Peak Hours Data (from backend)
const peakHours = computed(() => {
  if (!earningsData.value?.peak_hours) {
    return {
      morning: { trips: 0, earnings: '0.00', hours: 0 },
      afternoon: { trips: 0, earnings: '0.00', hours: 0 },
      evening: { trips: 0, earnings: '0.00', hours: 0 },
      night: { trips: 0, earnings: '0.00', hours: 0 }
    }
  }
  
  const hours = earningsData.value.peak_hours
  return {
    morning: {
      trips: hours.morning?.trips || 0,
      earnings: (hours.morning?.earnings || 0).toFixed(2),
      hours: hours.morning?.hours || 0
    },
    afternoon: {
      trips: hours.afternoon?.trips || 0,
      earnings: (hours.afternoon?.earnings || 0).toFixed(2),
      hours: hours.afternoon?.hours || 0
    },
    evening: {
      trips: hours.evening?.trips || 0,
      earnings: (hours.evening?.earnings || 0).toFixed(2),
      hours: hours.evening?.hours || 0
    },
    night: {
      trips: hours.night?.trips || 0,
      earnings: (hours.night?.earnings || 0).toFixed(2),
      hours: hours.night?.hours || 0
    }
  }
})

// Find best earning period
const bestPeriod = computed(() => {
  if (!earningsData.value?.peak_hours) return 'evening'
  
  const hours = earningsData.value.peak_hours
  let maxEarnings = 0
  let best = 'evening'
  
  Object.entries(hours).forEach(([period, data]) => {
    if (data.earnings > maxEarnings) {
      maxEarnings = data.earnings
      best = period
    }
  })
  
  return best
})

const goBack = () => {
  router.back()
}

// Fetch data on mount
onMounted(() => {
  fetchEarnings()
})
</script>

<style scoped src="./DriverEarnings.css"></style>
