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

/**
 * Navigation Guard
 * 
 * Protects routes based on authentication and role requirements.
 * Runs before every route navigation to enforce access control.
 * 
 * Flow:
 * 1. Check if authenticated users are trying to access public auth pages → redirect to dashboard
 * 2. Allow access to public routes (no auth required)
 * 3. Check if user is authenticated for protected routes → redirect to login if not
 * 4. Check if user has correct role for route → redirect to correct dashboard if wrong role
 * 5. Allow access if all checks pass
 */
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth  // Does route require authentication?
  const requiredRole = to.meta.role          // Does route require specific role?

  // STEP 1: Prevent authenticated users from accessing login/signup pages
  // If user is already logged in, redirect them to their dashboard
  if (!requiresAuth && authStore.isAuthenticated && (to.path === '/' || to.path === '/login' || to.path === '/signup')) {
    const userRole = authStore.user?.role
    const targetPath = userRole === 'rider' ? '/rider' : userRole === 'driver' ? '/driver' : userRole === 'admin' ? '/admin' : null
    
    // Only redirect if not already going to the correct dashboard
    if (targetPath && to.path !== targetPath) {
      next(targetPath)
      return
    }
  }

  // STEP 2: Allow access to public routes (no authentication required)
  if (!requiresAuth) {
    next()
    return
  }

  // STEP 3: Check authentication for protected routes
  // If route requires auth but user is not authenticated, redirect to login
  if (!authStore.isAuthenticated) {
    next('/login')
    return
  }

  // STEP 4: Check role-based authorization
  // If route requires specific role but user has different role, redirect to correct dashboard
  if (requiredRole && authStore.user?.role !== requiredRole) {
    const userRole = authStore.user?.role
    
    // Redirect to correct dashboard based on user's actual role
    if (userRole === 'rider') {
      next('/rider')
    } else if (userRole === 'driver') {
      next('/driver')
    } else if (userRole === 'admin') {
      next('/admin')
    } else {
      // Unknown role, logout and redirect to login
      await authStore.logout()
      next('/login')
    }
    return
  }

  // STEP 5: All checks passed, allow access to route
  next()
})

export default router
