<template>
  <div class="min-h-screen bg-taxini-dark flex items-center justify-center p-4">
    <div class="w-full max-w-2xl bg-taxini-dark-light rounded-3xl shadow-2xl overflow-hidden">
      <!-- Header with Logo -->
      <div class="p-12 pt-16 text-center border-b border-taxini-green/20">
        <img src="/src/assets/logo.png" alt="Taxini" class="w-40 h-40 mx-auto object-contain mb-4" />
      </div>

      <!-- Content -->
      <div class="px-16 py-16">
        <div class="space-y-12 animate-slide-up">
          <div class="text-center">
            <h2 class="text-4xl font-bold text-white mb-3">Verification code</h2>
            <p class="text-taxini-text-gray text-lg">Enter the 5-digit code sent to your phone</p>
          </div>

          <!-- OTP Input Boxes -->
          <div class="flex justify-center gap-5">
            <input
              v-for="(digit, index) in otpDigits"
              :key="index"
              :ref="el => otpRefs[index] = el"
              v-model="otpDigits[index]"
              type="text"
              inputmode="numeric"
              maxlength="1"
              class="w-20 h-20 bg-[#0d2621] text-white text-center text-3xl font-bold rounded-2xl border-2 border-taxini-green/30 focus:border-taxini-yellow focus:outline-none focus:ring-4 focus:ring-taxini-yellow/30 transition-all duration-200 shadow-lg"
              @input="handleInput(index, $event)"
              @keydown="handleKeydown(index, $event)"
              @paste="handlePaste"
            />
          </div>

          <!-- Error Message -->
          <transition name="fade">
            <div v-if="error" class="bg-red-500 bg-opacity-10 border-2 border-red-500 text-red-500 px-6 py-4 rounded-2xl text-base text-center flex items-center justify-center gap-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{{ error }}</span>
            </div>
          </transition>

          <!-- Verify Button -->
          <button
            @click="handleVerify"
            :disabled="loading || otpCode.length !== 5"
            class="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed font-bold py-5 text-xl rounded-2xl shadow-xl hover:shadow-taxini-yellow/30 transition-all"
          >
            <span v-if="loading" class="flex items-center justify-center gap-3">
              <svg class="animate-spin h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Verifying...
            </span>
            <span v-else>Verify Now</span>
          </button>

          <!-- Resend Link -->
          <div class="text-center">
            <span class="text-taxini-text-gray text-lg">Not received code ? </span>
            <button 
              @click="handleResend" 
              :disabled="resendCooldown > 0"
              class="text-taxini-yellow font-bold hover:underline text-lg disabled:opacity-50 transition-all"
            >
              <span v-if="resendCooldown > 0">Send again ({{ resendCooldown }}s)</span>
              <span v-else>Send again</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const otpDigits = ref(['', '', '', '', ''])
const otpRefs = ref([])
const loading = ref(false)
const error = ref('')
const resendCooldown = ref(60)
let timerInterval = null

const phoneNumber = computed(() => authStore.phoneNumber || '+216 XX XXX XXX')
const otpCode = computed(() => otpDigits.value.join(''))

const handleInput = (index, event) => {
  const value = event.target.value
  
  // Only allow numbers
  if (!/^\d*$/.test(value)) {
    otpDigits.value[index] = ''
    return
  }

  otpDigits.value[index] = value

  // Auto-focus next input
  if (value && index < 4) {
    otpRefs.value[index + 1]?.focus()
  }

  // Auto-verify when all 5 digits are entered
  if (otpCode.value.length === 5) {
    handleVerify()
  }
}

const handleKeydown = (index, event) => {
  if (event.key === 'Backspace' && !otpDigits.value[index] && index > 0) {
    otpRefs.value[index - 1]?.focus()
  }
}

const handlePaste = (event) => {
  event.preventDefault()
  const pastedData = event.clipboardData.getData('text').replace(/\D/g, '')
  
  for (let i = 0; i < Math.min(pastedData.length, 5); i++) {
    otpDigits.value[i] = pastedData[i]
  }

  // Focus last filled input
  const lastIndex = Math.min(pastedData.length - 1, 4)
  otpRefs.value[lastIndex]?.focus()
}

const handleVerify = async () => {
  error.value = ''

  if (otpCode.value.length !== 5) {
    error.value = 'Please enter the complete 5-digit code'
    return
  }

  loading.value = true

  try {
    await authStore.verifyOTP(authStore.phoneNumber, otpCode.value)
    // Navigate to profile creation
    router.push('/create-profile')
  } catch (err) {
    error.value = err.message || 'Invalid verification code'
    // Clear OTP on error
    otpDigits.value = ['', '', '', '', '']
    otpRefs.value[0]?.focus()
  } finally {
    loading.value = false
  }
}

const handleResend = async () => {
  try {
    await authStore.sendOTP(authStore.phoneNumber)
    // Reset timer
    resendCooldown.value = 60
    startResendTimer()
  } catch (err) {
    error.value = 'Failed to resend code'
  }
}

const startResendTimer = () => {
  if (timerInterval) clearInterval(timerInterval)
  
  timerInterval = setInterval(() => {
    if (resendCooldown.value > 0) {
      resendCooldown.value--
    } else {
      clearInterval(timerInterval)
    }
  }, 1000)
}

onMounted(() => {
  // Focus first input
  otpRefs.value[0]?.focus()
  // Start resend timer
  startResendTimer()
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})
</script>
