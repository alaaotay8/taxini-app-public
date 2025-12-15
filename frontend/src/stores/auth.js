/**
 * Authentication Store
 * 
 * Manages user authentication state using HttpOnly cookies for security.
 * Supports OTP-based authentication for riders/drivers and email/password for admins.
 * 
 * Authentication Flow:
 * 1. User enters phone number → sendOTP() → Backend sends OTP via SMS
 * 2. User enters OTP → verifyOTP() → Backend validates and sets HttpOnly cookie
 * 3. Cookie is automatically sent with all API requests
 * 4. On app load, getCurrentUser() checks if valid session exists
 * 5. On logout, cookie is cleared by backend
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authService from '@/services/authService'

export const useAuthStore = defineStore('auth', () => {
  // ============================================================================
  // STATE
  // ============================================================================
  
  /** Current authenticated user object (null if not logged in) */
  const user = ref(null)
  
  /** Phone number stored in localStorage for convenience (not for auth) */
  const phoneNumber = ref(localStorage.getItem('taxini_phone') || null)
  
  /** Loading state for async operations */
  const loading = ref(false)
  
  /** Error message from last failed operation */
  const error = ref(null)

  // ============================================================================
  // COMPUTED PROPERTIES
  // ============================================================================
  
  /** Check if user is authenticated (has valid session) */
  const isAuthenticated = computed(() => !!user.value)
  
  /** Get current user's role (rider, driver, or admin) */
  const userRole = computed(() => user.value?.role || null)
  
  /** Check if current user is a rider */
  const isRider = computed(() => userRole.value === 'rider')
  
  /** Check if current user is a driver */
  const isDriver = computed(() => userRole.value === 'driver')
  
  /** Check if current user is an admin */
  const isAdmin = computed(() => userRole.value === 'admin')

  // ============================================================================
  // ACTIONS
  // ============================================================================
  
  /**
   * Send OTP code to phone number
   * 
   * Step 1 of authentication: Backend sends 6-digit OTP via SMS.
   * In development mode, OTP is always 123456.
   * 
   * @param {string} phone - Phone number in format +216XXXXXXXX
   * @returns {Promise} Response from backend
   */
  const sendOTP = async (phone) => {
    loading.value = true
    error.value = null
    try {
      const response = await authService.sendOTP(phone)
      phoneNumber.value = phone
      localStorage.setItem('taxini_phone', phone)
      return response
    } catch (err) {
      error.value = err.message || 'Failed to send OTP'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Verify OTP code and authenticate user
   * 
   * Step 2 of authentication: Backend validates OTP and sets HttpOnly cookie.
   * Cookie contains JWT token and is automatically sent with all requests.
   * 
   * @param {string} phone - Phone number that received OTP
   * @param {string} otpCode - 6-digit OTP code entered by user
   * @returns {Promise} Response with user data
   */
  const verifyOTP = async (phone, otpCode) => {
    loading.value = true
    error.value = null
    try {
      const response = await authService.verifyOTP(phone, otpCode)
      user.value = response.user
      return response
    } catch (err) {
      error.value = err.message || 'Invalid OTP code'
      throw err
    } finally {
      loading.value = false
    }
  }

  const createProfile = async (profileData) => {
    loading.value = true
    error.value = null
    try {
      const response = await authService.createProfile(profileData)
      user.value = response.user
      return response
    } catch (err) {
      error.value = err.message || 'Failed to create profile'
      throw err
    } finally {
      loading.value = false
    }
  }

  const signup = async (signupData) => {
    loading.value = true
    error.value = null
    try {
      const response = await authService.register(signupData)
      user.value = response.user
      localStorage.setItem('taxini_phone', response.user.phone)
      return response
    } catch (err) {
      error.value = err.message || 'Failed to register'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Get current user from session
   * 
   * Called on app startup to restore session from HttpOnly cookie.
   * If cookie is valid, user data is returned and user is logged in.
   * If cookie is invalid/expired, 401 error triggers logout.
   * 
   * @returns {Promise} Response with user data
   */
  const getCurrentUser = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await authService.getCurrentUser()
      user.value = response.user
      return response
    } catch (err) {
      error.value = err.message
      if (err.response?.status === 401) {
        logout()
      }
      throw err
    } finally {
      loading.value = false
    }
  }

  const adminLogin = async (email, password) => {
    loading.value = true
    error.value = null
    try {
      const response = await authService.adminLogin(email, password)
      user.value = response.user
      return response
    } catch (err) {
      error.value = err.message || 'Invalid credentials'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Logout user and clear session
   * 
   * Calls backend to clear HttpOnly cookie and clears local state.
   * Always clears local state even if backend call fails.
   * 
   * @returns {Promise<void>}
   */
  const logout = async () => {
    try {
      await authService.logout()
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      user.value = null
      phoneNumber.value = null
      localStorage.removeItem('taxini_phone')
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    user,
    phoneNumber,
    loading,
    error,
    isAuthenticated,
    userRole,
    isRider,
    isDriver,
    isAdmin,
    sendOTP,
    verifyOTP,
    createProfile,
    signup,
    getCurrentUser,
    adminLogin,
    logout,
    clearError
  }
})
