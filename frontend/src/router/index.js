import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { isTokenExpired } from '@/utils/security'

// Eager load only critical auth views (small bundle impact)
import Onboarding from '@/views/auth/Onboarding.vue'
import Login from '@/views/auth/Login.vue'
import Signup from '@/views/auth/Signup.vue'
import VerifyOTP from '@/views/auth/VerifyOTP.vue'
import CreateProfile from '@/views/auth/CreateProfile.vue'

// Lazy load dashboards (loaded on demand for faster initial load)
const RiderDashboard = () => import('@/views/rider/RiderDashboard.vue')
const DriverDashboard = () => import('@/views/driver/DriverDashboard.vue')
const AdminDashboard = () => import('@/views/admin/AdminDashboard.vue')

// Lazy load all secondary views (loaded only when needed)
const RiderTripHistory = () => import('@/views/rider/RiderTripHistory.vue')
const RiderProfile = () => import('@/views/rider/RiderProfile.vue')
const RiderSupport = () => import('@/views/rider/RiderSupport.vue')

const DriverTripHistory = () => import('@/views/driver/DriverTripHistory.vue')
const DriverEarnings = () => import('@/views/driver/DriverEarnings.vue')
const DriverProfile = () => import('@/views/driver/DriverProfile.vue')
const DriverSupport = () => import('@/views/driver/DriverSupport.vue')

const AdminLogin = () => import('@/views/admin/AdminLogin.vue')
const AdminDrivers = () => import('@/views/admin/AdminDrivers.vue')
const AdminRiders = () => import('@/views/admin/AdminRiders.vue')
const AdminTrips = () => import('@/views/admin/AdminTrips.vue')
const AdminSettings = () => import('@/views/admin/AdminSettings.vue')
const AdminTickets = () => import('@/views/admin/AdminTickets.vue')
const AdminStatistics = () => import('@/views/admin/AdminStatistics.vue')

const routes = [
  // Public Routes
  {
    path: '/',
    name: 'Onboarding',
    component: Onboarding,
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/signup',
    name: 'Signup',
    component: Signup,
    meta: { requiresAuth: false }
  },
  {
    path: '/verify-otp',
    name: 'VerifyOTP',
    component: VerifyOTP,
    meta: { requiresAuth: false }
  },
  {
    path: '/create-profile',
    name: 'CreateProfile',
    component: CreateProfile,
    meta: { requiresAuth: true }
  },

  // Rider Routes
  {
    path: '/rider',
    name: 'RiderDashboard',
    component: RiderDashboard,
    meta: { requiresAuth: true, role: 'rider' }
  },
  {
    path: '/rider/history',
    name: 'RiderTripHistory',
    component: RiderTripHistory,
    meta: { requiresAuth: true, role: 'rider' }
  },
  {
    path: '/rider/profile',
    name: 'RiderProfile',
    component: RiderProfile,
    meta: { requiresAuth: true, role: 'rider' }
  },
  {
    path: '/rider/support',
    name: 'RiderSupport',
    component: RiderSupport,
    meta: { requiresAuth: true, role: 'rider' }
  },

  // Driver Routes
  {
    path: '/driver',
    name: 'DriverDashboard',
    component: DriverDashboard,
    meta: { requiresAuth: true, role: 'driver' }
  },
  {
    path: '/driver/history',
    name: 'DriverTripHistory',
    component: DriverTripHistory,
    meta: { requiresAuth: true, role: 'driver' }
  },
  {
    path: '/driver/earnings',
    name: 'DriverEarnings',
    component: DriverEarnings,
    meta: { requiresAuth: true, role: 'driver' }
  },
  {
    path: '/driver/profile',
    name: 'DriverProfile',
    component: DriverProfile,
    meta: { requiresAuth: true, role: 'driver' }
  },
  {
    path: '/driver/support',
    name: 'DriverSupport',
    component: DriverSupport,
    meta: { requiresAuth: true, role: 'driver' }
  },

  // Admin Routes
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: AdminLogin,
    meta: { requiresAuth: false }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/drivers',
    name: 'AdminDrivers',
    component: AdminDrivers,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/riders',
    name: 'AdminRiders',
    component: AdminRiders,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/trips',
    name: 'AdminTrips',
    component: AdminTrips,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/settings',
    name: 'AdminSettings',
    component: AdminSettings,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/tickets',
    name: 'AdminTickets',
    component: AdminTickets,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/statistics',
    name: 'AdminStatistics',
    component: AdminStatistics,
    meta: { requiresAuth: true, role: 'admin' }
  },

  // 404 Catch-all
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation Guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth
  const requiredRole = to.meta.role

  // If token exists but no user data, try to fetch user
  if (authStore.token && !authStore.user) {
    try {
      await authStore.getCurrentUser()
    } catch (error) {
      console.warn('Failed to fetch user on navigation:', error.message)
    }
  }

  // Check token expiration (client-side check)
  if (authStore.token && isTokenExpired(authStore.token)) {
    console.warn('🔒 Token expired - logging out')
    authStore.logout()
  }

  if (requiresAuth && !authStore.isAuthenticated) {
    // Redirect to login if not authenticated
    next('/login')
  } else if (requiredRole && authStore.user?.role !== requiredRole) {
    // Prevent privilege escalation - redirect to correct dashboard based on role
    const userRole = authStore.user?.role
    if (userRole === 'rider') {
      next('/rider')
    } else if (userRole === 'driver') {
      next('/driver')
    } else if (userRole === 'admin') {
      next('/admin')
    } else {
      authStore.logout()
      next('/login')
    }
  } else if (!requiresAuth && authStore.isAuthenticated && to.path === '/') {
    // Redirect authenticated users from onboarding to their dashboard
    const userRole = authStore.user?.role
    if (userRole === 'rider') {
      next('/rider')
    } else if (userRole === 'driver') {
      next('/driver')
    } else if (userRole === 'admin') {
      next('/admin')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
