import api from './api'

const authService = {
  // Send OTP to phone number
  sendOTP: async (phoneNumber) => {
    return await api.post('/auth/send-otp', { phone_number: phoneNumber })
  },

  // Verify OTP code
  verifyOTP: async (phoneNumber, otpCode) => {
    return await api.post('/auth/verify-otp', {
      phone_number: phoneNumber,
      otp_code: otpCode
    })
  },

  // Get current user
  getCurrentUser: async () => {
    try {
      return await api.get('/auth/me')
    } catch (error) {
      // Silently handle 401 - it just means no active session
      if (error.response?.status === 401) {
        throw new Error('Not authenticated')
      }
      throw error
    }
  },

  // Register new user
  register: async (userData) => {
    const payload = {
      name: userData.name,
      email: userData.email,
      phone: userData.phone,
      role: userData.role,
      residence_place: userData.residence_place,
      taxi_number: userData.taxi_number
    }
    console.log('📤 Register API payload:', payload)
    const response = await api.post('/auth/register', payload)
    console.log('✅ Register API response:', response)
    return response
  },

  // Create user profile (after OTP verification)
  createProfile: async (profileData) => {
    const formData = new FormData()
    
    // Add required fields
    formData.append('role', profileData.role)
    
    // Add optional fields
    if (profileData.name) formData.append('name', profileData.name)
    if (profileData.email) formData.append('email', profileData.email)
    
    // Rider-specific fields
    if (profileData.role === 'rider' && profileData.residence_place) {
      formData.append('residence_place', profileData.residence_place)
    }
    
    // Driver-specific fields
    if (profileData.role === 'driver') {
      if (profileData.taxi_number) formData.append('taxi_number', profileData.taxi_number)
      if (profileData.account_status) formData.append('account_status', profileData.account_status)
      if (profileData.id_card_file) formData.append('id_card_file', profileData.id_card_file)
      if (profileData.driver_license_file) formData.append('driver_license_file', profileData.driver_license_file)
    }

    return await api.post('/users/create-profile', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // Admin login
  adminLogin: async (email, password) => {
    return await api.post('/admin/login', { email, password })
  },

  // Logout (clears HttpOnly cookie)
  logout: async () => {
    return await api.post('/auth/logout')
  },

  // Reset password
  resetPassword: async (phoneNumber) => {
    return await api.post('/users/reset-password', { phone_number: phoneNumber })
  }
}

export default authService
