<template>
  <div class="phone-screen bg-taxini-dark flex flex-col items-center justify-center min-h-screen">
    <!-- Content Container -->
    <div class="w-full max-w-md px-8">
      <!-- Header with Logo -->
      <div class="text-center mb-8">
        <img src="/src/assets/logo.png" alt="Taxini" class="w-32 h-32 mx-auto object-contain" />
      </div>

      <div class="space-y-6 animate-slide-up">
        <div class="mb-6">
          <h2 class="text-2xl font-semibold text-white mb-2">Welcome to Taxini</h2>
          <p class="text-taxini-text-gray text-sm">Enter your phone number to get started</p>
        </div>

        <!-- Step 1: Phone Number Input -->
        <div v-if="step === 1" class="space-y-4">
          <!-- Phone Input -->
          <div class="space-y-2">
            <label class="block text-xs font-medium text-taxini-text-gray uppercase tracking-wider">
              Phone Number
            </label>
            <input
              v-model="phoneNumber"
              type="tel"
              placeholder="+216 12 345 678"
              class="input-field-dark"
              @keyup.enter="handleSendOTP"
            />
            <p class="text-xs text-taxini-text-gray">
              Format: +216 (country code) followed by your number
            </p>
          </div>

          <!-- Error Message -->
          <transition name="fade">
            <div v-if="error" class="bg-red-500 bg-opacity-10 border border-red-500 text-red-500 px-4 py-3 rounded-xl text-sm">
              {{ error }}
            </div>
          </transition>

          <!-- Send OTP Button -->
          <button
            @click="handleSendOTP"
            :disabled="loading || !phoneNumber"
            class="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
          >
            <span v-if="loading">Sending OTP...</span>
            <span v-else>Send OTP Code</span>
          </button>
        </div>

        <!-- Step 2: OTP Verification -->
        <div v-if="step === 2" class="space-y-4">
          <!-- OTP Input -->
          <div class="space-y-2">
            <label class="block text-xs font-medium text-taxini-text-gray uppercase tracking-wider">
              Enter OTP Code
            </label>
            <input
              v-model="otpCode"
              type="text"
              maxlength="6"
              placeholder="000000"
              class="input-field-dark text-center text-2xl tracking-widest"
              @keyup.enter="handleVerifyOTP"
            />
            <p class="text-xs text-taxini-text-gray text-center">
              OTP code sent to {{ phoneNumber }}
            </p>
          </div>

          <!-- Error Message -->
          <transition name="fade">
            <div v-if="error" class="bg-red-500 bg-opacity-10 border border-red-500 text-red-500 px-4 py-3 rounded-xl text-sm">
              {{ error }}
            </div>
          </transition>

          <!-- Verify Button -->
          <button
            @click="handleVerifyOTP"
            :disabled="loading || otpCode.length !== 6"
            class="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
          >
            <span v-if="loading">Verifying...</span>
            <span v-else>Verify & Sign In</span>
          </button>

          <!-- Resend OTP -->
          <div class="text-center">
            <button
              @click="handleResendOTP"
              :disabled="resendCooldown > 0"
              class="text-sm text-taxini-yellow hover:underline disabled:text-gray-500 disabled:no-underline"
            >
              <span v-if="resendCooldown > 0">Resend in {{ resendCooldown }}s</span>
              <span v-else>Resend OTP Code</span>
            </button>
          </div>

          <!-- Back Button -->
          <button
            @click="step = 1; error = ''"
            class="w-full mt-2 px-4 py-3 text-sm font-medium text-white text-opacity-70 border border-white border-opacity-20 rounded-xl hover:text-opacity-100 hover:bg-white hover:bg-opacity-5 hover:border-opacity-30 transition-all duration-200 flex items-center justify-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
            </svg>
            <span>Change phone number</span>
          </button>
        </div>

        <!-- Sign Up Link -->
        <div class="text-center pt-4">
          <span class="text-taxini-text-gray text-sm">Don't have an account? </span>
          <router-link to="/signup" class="text-taxini-yellow font-medium hover:underline text-sm">
            Sign up
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const step = ref(1) // 1 = phone input, 2 = OTP verification
const phoneNumber = ref('')
const otpCode = ref('')
const loading = ref(false)
const error = ref('')
const resendCooldown = ref(0)

let cooldownInterval = null

const handleSendOTP = async () => {
  error.value = ''
  
  if (!phoneNumber.value) {
    error.value = 'Please enter your phone number'
    return
  }

  // Basic phone validation
  if (!phoneNumber.value.startsWith('+')) {
    error.value = 'Phone number must start with + and country code (e.g., +216)'
    return
  }

  loading.value = true

  try {
    await authStore.sendOTP(phoneNumber.value)
    step.value = 2
    startResendCooldown()
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Failed to send OTP. Please try again.'
  } finally {
    loading.value = false
  }
}

const handleVerifyOTP = async () => {
  error.value = ''
  
  if (otpCode.value.length !== 6) {
    error.value = 'Please enter the 6-digit OTP code'
    return
  }

  // In development mode, accept 123456 as valid OTP
  if (otpCode.value !== '123456') {
    error.value = 'Invalid OTP code. In development mode, use: 123456'
    return
  }

  loading.value = true

  try {
    const response = await authStore.verifyOTP(phoneNumber.value, otpCode.value)
    
    // Redirect based on role from response
    const user = response.user
    if (user) {
      if (user.role === 'rider') {
        router.push('/rider')
      } else if (user.role === 'driver') {
        router.push('/driver')
      } else if (user.role === 'admin') {
        router.push('/admin')
      } else {
        router.push('/dashboard')
      }
    }
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Invalid OTP code. Please try again.'
  } finally {
    loading.value = false
  }
}

const handleResendOTP = async () => {
  if (resendCooldown.value > 0) return
  
  error.value = ''
  loading.value = true

  try {
    await authStore.sendOTP(phoneNumber.value)
    otpCode.value = ''
    startResendCooldown()
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Failed to resend OTP'
  } finally {
    loading.value = false
  }
}

const startResendCooldown = () => {
  resendCooldown.value = 60 // 60 seconds
  cooldownInterval = setInterval(() => {
    resendCooldown.value--
    if (resendCooldown.value <= 0) {
      clearInterval(cooldownInterval)
    }
  }, 1000)
}

// Cleanup interval on unmount
onUnmounted(() => {
  if (cooldownInterval) {
    clearInterval(cooldownInterval)
  }
})
</script>
