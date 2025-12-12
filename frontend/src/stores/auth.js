import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authService from '@/services/authService'
import { updateCachedToken } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('taxini_token') || null)
  const phoneNumber = ref(localStorage.getItem('taxini_phone') || null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || null)
  const isRider = computed(() => userRole.value === 'rider')
  const isDriver = computed(() => userRole.value === 'driver')
  const isAdmin = computed(() => userRole.value === 'admin')

  // Actions
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

  const verifyOTP = async (phone, otpCode) => {
    loading.value = true
    error.value = null
    try {
      const response = await authService.verifyOTP(phone, otpCode)
      // Handle both response formats (with session object or direct access_token)
      const accessToken = response.session?.access_token || response.access_token
      token.value = accessToken
      user.value = response.user
      updateCachedToken(accessToken) // Update cache instead of direct localStorage
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
      token.value = response.session.access_token
      user.value = response.user
      updateCachedToken(response.session.access_token)
      localStorage.setItem('taxini_phone', response.user.phone)
      return response
    } catch (err) {
      error.value = err.message || 'Failed to register'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getCurrentUser = async () => {
    if (!token.value) return null
    loading.value = true
    error.value = null
    try {
      const response = await authService.getCurrentUser()
      user.value = response.user
      return response
    } catch (err) {
      error.value = err.message
      // If token is invalid, logout
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
      // Handle both response formats (with session object or direct access_token)
      const accessToken = response.session?.access_token || response.access_token
      token.value = accessToken
      user.value = response.user
      updateCachedToken(accessToken)
      return response
    } catch (err) {
      error.value = err.message || 'Invalid credentials'
      throw err
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    phoneNumber.value = null
    updateCachedToken(null)
    localStorage.removeItem('taxini_phone')
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    user,
    token,
    phoneNumber,
    loading,
    error,
    // Getters
    isAuthenticated,
    userRole,
    isRider,
    isDriver,
    isAdmin,
    // Actions
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
