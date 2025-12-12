<template>
  <div class="phone-screen bg-taxini-dark">
    <!-- Header with Logo -->
    <div class="p-6 pt-12 text-center">
      <img src="/src/assets/logo.png" alt="Taxini" class="w-32 h-32 mx-auto object-contain" />
    </div>

    <!-- Content -->
    <div class="flex-1 flex flex-col px-8 py-6 overflow-y-auto">
      <div class="space-y-6 animate-slide-up">
        <!-- Step 1: Registration Form -->
        <div v-if="step === 1">
          <div class="mb-6">
            <h2 class="text-2xl font-semibold text-white mb-2">Create Account</h2>
            <p class="text-taxini-text-gray text-sm">Join Taxini community</p>
          </div>
        
        <!-- Role Selection -->
        <div class="space-y-3">
          <label class="block text-xs font-medium text-taxini-text-gray uppercase tracking-wider">Select Role</label>
          <div class="flex gap-3">
            <button 
              @click="selectedRole = 'rider'" 
              :class="selectedRole === 'rider' ? 'bg-taxini-yellow text-taxini-dark shadow-lg' : 'bg-taxini-dark-light text-taxini-text-gray border border-taxini-green/20'" 
              class="flex-1 py-4 rounded-xl font-semibold transition-all duration-200 flex flex-col items-center justify-center gap-2"
            >
              <img src="/src/assets/RiderIcon.png" alt="Rider" class="w-8 h-8 object-contain" :class="selectedRole === 'rider' ? '' : 'opacity-60'" />
              <span>Rider</span>
            </button>
            <button 
              @click="selectedRole = 'driver'" 
              :class="selectedRole === 'driver' ? 'bg-taxini-yellow text-taxini-dark shadow-lg' : 'bg-taxini-dark-light text-taxini-text-gray border border-taxini-green/20'" 
              class="flex-1 py-4 rounded-xl font-semibold transition-all duration-200 flex flex-col items-center justify-center gap-2"
            >
              <img src="/src/assets/DriverIcon.png" alt="Driver" class="w-8 h-8 object-contain" :class="selectedRole === 'driver' ? '' : 'opacity-60'" />
              <span>Driver</span>
            </button>
          </div>
        </div>
        
        <!-- Extra spacing before form fields -->
        <div class="pt-4"></div>
        
        <!-- Form Fields -->
        <div class="space-y-4">
          <div class="space-y-2">
            <label class="block text-xs font-medium text-taxini-text-gray uppercase tracking-wider">Full Name</label>
            <input 
              v-model="formData.name" 
              type="text" 
              placeholder="Enter your full name" 
              class="input-field-dark" 
            />
          </div>
          
          <div class="space-y-2">
            <label class="block text-xs font-medium text-taxini-text-gray uppercase tracking-wider">Email Address</label>
            <input 
              v-model="formData.email" 
              type="email" 
              placeholder="your.email@example.com" 
              class="input-field-dark" 
              @blur="validateEmail" 
            />
            <p v-if="emailError" class="text-red-500 text-xs mt-1">{{ emailError }}</p>
          </div>
          
          <div class="space-y-2">
            <label class="block text-xs font-medium text-taxini-text-gray uppercase tracking-wider">Phone Number</label>
            <input 
              v-model="formData.phone" 
              type="tel" 
              placeholder="+216 12 345 678" 
              class="input-field-dark" 
            />
            <p class="text-xs text-taxini-text-gray">Format: +216 (country code) followed by your number</p>
          </div>
        </div>
        
        <!-- Extra spacing before role-specific fields -->
        <div class="pt-4"></div>
        
        <!-- Rider-specific fields -->
        <div v-if="selectedRole === 'rider'" class="space-y-4">
          <div class="space-y-2">
            <label class="block text-xs font-medium text-taxini-text-gray uppercase tracking-wider">Residence Place</label>
            <input 
              v-model="formData.residencePlace" 
              type="text" 
              placeholder="Enter your address" 
              class="input-field-dark" 
              list="locations" 
            />
            <datalist id="locations">
              <option value="Tunis, Tunisia"></option>
              <option value="La Marsa, Tunisia"></option>
              <option value="Carthage, Tunisia"></option>
            </datalist>
          </div>
        </div>
        
        <!-- Driver-specific fields -->
        <div v-if="selectedRole === 'driver'" class="space-y-4">
          <div class="space-y-2">
            <label class="block text-xs font-medium text-taxini-text-gray uppercase tracking-wider">Taxi Number</label>
            <input 
              v-model="formData.taxiNumber" 
              type="text" 
              placeholder="TN 12345 A" 
              class="input-field-dark" 
            />
          </div>
          
          <div class="space-y-2">
            <label class="block text-xs font-medium text-taxini-text-gray uppercase tracking-wider">ID Card</label>
            <input 
              ref="idCardInput" 
              type="file" 
              accept="image/*" 
              @change="handleIDCardUpload" 
              class="hidden" 
            />
            <button 
              @click="$refs.idCardInput.click()" 
              class="w-full bg-taxini-dark-light text-taxini-text-gray px-4 py-3 rounded-xl border border-dashed border-taxini-green/30 hover:border-taxini-yellow hover:bg-taxini-dark transition-all flex items-center justify-center gap-2 text-sm"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>{{ formData.idCardName || 'Upload ID Card' }}</span>
            </button>
            <div v-if="formData.idCardPreview" class="mt-2 relative rounded-xl overflow-hidden border border-taxini-green/20">
              <img :src="formData.idCardPreview" alt="ID Card" class="w-full h-32 object-cover" />
              <button 
                @click="removeIDCard" 
                class="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white w-8 h-8 rounded-full shadow-lg transition-colors flex items-center justify-center text-sm"
              >✕</button>
            </div>
          </div>
          
          <div class="space-y-2">
            <label class="block text-xs font-medium text-taxini-text-gray uppercase tracking-wider">Driver License</label>
            <input 
              ref="licenseInput" 
              type="file" 
              accept="image/*" 
              @change="handleLicenseUpload" 
              class="hidden" 
            />
            <button 
              @click="$refs.licenseInput.click()" 
              class="w-full bg-taxini-dark-light text-taxini-text-gray px-4 py-3 rounded-xl border border-dashed border-taxini-green/30 hover:border-taxini-yellow hover:bg-taxini-dark transition-all flex items-center justify-center gap-2 text-sm"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
              </svg>
              <span>{{ formData.licenseName || 'Upload Driver License' }}</span>
            </button>
            <div v-if="formData.licensePreview" class="mt-2 relative rounded-xl overflow-hidden border border-taxini-green/20">
              <img :src="formData.licensePreview" alt="License" class="w-full h-32 object-cover" />
              <button 
                @click="removeLicense" 
                class="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white w-8 h-8 rounded-full shadow-lg transition-colors flex items-center justify-center text-sm"
              >✕</button>
            </div>
          </div>
        </div>
        
        <!-- Extra spacing before buttons -->
        <div class="pt-4"></div>
        
        <!-- Error Message -->
        <transition name="fade">
          <div v-if="error" class="bg-red-500 bg-opacity-10 border border-red-500 text-red-500 px-4 py-3 rounded-xl text-sm">
            {{ error }}
          </div>
        </transition>
        
        <!-- Continue Button -->
        <button 
          @click="handleContinue" 
          :disabled="loading || !isFormValid" 
          class="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
        >
          <span v-if="loading">Sending OTP...</span>
          <span v-else>Continue</span>
        </button>
        
        <!-- Login Link -->
        <div class="text-center pt-2">
          <span class="text-taxini-text-gray text-sm">Already have an account? </span>
          <router-link to="/login" class="text-taxini-yellow font-semibold hover:underline text-sm">Sign in</router-link>
        </div>
        </div>

        <!-- Step 2: OTP Verification -->
        <div v-if="step === 2">
          <div class="mb-6">
            <h2 class="text-2xl font-semibold text-white mb-2">Verify Phone Number</h2>
            <p class="text-taxini-text-gray text-sm">Enter the OTP code sent to {{ formData.phone }}</p>
          </div>

          <div class="space-y-4">
            <div class="space-y-2">
              <label class="block text-xs font-medium text-taxini-text-gray uppercase tracking-wider">Enter OTP Code</label>
              <input
                v-model="otpCode"
                type="text"
                maxlength="6"
                placeholder="000000"
                class="input-field-dark text-center text-2xl tracking-widest"
                @keyup.enter="handleVerifyOTP"
              />
              <p class="text-xs text-taxini-text-gray text-center">
                In development mode, use: 123456
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
              :disabled="loading || !otpCode || otpCode.length !== 6"
              class="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
            >
              <span v-if="loading">Verifying...</span>
              <span v-else>Verify & Create Account</span>
            </button>

            <!-- Back Button -->
            <button
              @click="step = 1; error = ''"
              class="w-full text-taxini-text-gray hover:text-white transition-colors text-sm py-2"
            >
              ← Back to registration form
            </button>
          </div>
        </div>

        <!-- Step 3: Success Message -->
        <div v-if="step === 3">
          <div class="mb-6 text-center">
            <div class="w-20 h-20 bg-taxini-green/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-taxini-green" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 class="text-2xl font-semibold text-white mb-2">Account Created!</h2>
            <p class="text-taxini-text-gray text-sm">{{ successMessage }}</p>
          </div>

          <button
            @click="redirectToDashboard"
            class="btn-primary w-full font-semibold"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const step = ref(1) // 1: Form, 2: OTP Verification, 3: Success
const selectedRole = ref('rider')
const loading = ref(false)
const error = ref('')
const emailError = ref('')
const otpCode = ref('')
const successMessage = ref('')

const formData = ref({ 
  name: '', 
  email: '', 
  phone: '', 
  residencePlace: '', 
  taxiNumber: '', 
  idCard: null, 
  idCardName: '', 
  idCardPreview: null, 
  license: null, 
  licenseName: '', 
  licensePreview: null 
})

const validateEmail = () => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  emailError.value = formData.value.email && !emailRegex.test(formData.value.email) ? 'Please enter a valid email address' : ''
}

const isFormValid = computed(() => {
  const baseValid = formData.value.name && formData.value.email && formData.value.phone && !emailError.value
  return selectedRole.value === 'rider' ? baseValid && formData.value.residencePlace : baseValid && formData.value.taxiNumber && formData.value.idCard && formData.value.license
})

const handleIDCardUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    formData.value.idCard = file
    formData.value.idCardName = file.name
    const reader = new FileReader()
    reader.onload = (e) => { formData.value.idCardPreview = e.target.result }
    reader.readAsDataURL(file)
  }
}

const handleLicenseUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    formData.value.license = file
    formData.value.licenseName = file.name
    const reader = new FileReader()
    reader.onload = (e) => { formData.value.licensePreview = e.target.result }
    reader.readAsDataURL(file)
  }
}

const removeIDCard = () => { 
  formData.value.idCard = null
  formData.value.idCardName = ''
  formData.value.idCardPreview = null 
}

const removeLicense = () => { 
  formData.value.license = null
  formData.value.licenseName = ''
  formData.value.licensePreview = null 
}

// Step 1: Send OTP
const handleContinue = async () => {
  error.value = ''
  validateEmail()
  
  if (!isFormValid.value) { 
    error.value = 'Please fill in all required fields'
    return 
  }
  
  loading.value = true
  try {
    await authStore.sendOTP(formData.value.phone)
    step.value = 2
  } catch (err) {
    error.value = err.message || 'Failed to send OTP. Please try again.'
  } finally {
    loading.value = false
  }
}

// Step 2: Verify OTP and Create Account
const handleVerifyOTP = async () => {
  error.value = ''
  
  if (!otpCode.value || otpCode.value.length !== 6) {
    error.value = 'Please enter a valid 6-digit OTP code'
    return
  }
  
  loading.value = true
  try {
    // In development mode, just check if OTP is correct (123456)
    if (otpCode.value !== '123456') {
      throw new Error('Invalid OTP code. In development mode, use: 123456')
    }
    
    // Create the account after OTP verification
    const signupData = { 
      name: formData.value.name, 
      email: formData.value.email, 
      phone: formData.value.phone, 
      role: selectedRole.value 
    }
    
    if (selectedRole.value === 'rider') { 
      signupData.residence_place = formData.value.residencePlace 
      successMessage.value = 'Welcome to Taxini! Your rider account is ready to use.'
    } else { 
      signupData.taxi_number = formData.value.taxiNumber
      successMessage.value = 'Your driver account has been created. Please wait while we verify your documents.'
    }
    
    // Create account
    await authStore.signup(signupData)
    
    // Show success step
    step.value = 3
  } catch (err) {
    error.value = err.message || 'Verification failed. Please try again.'
  } finally {
    loading.value = false
  }
}

// Step 3: Redirect to dashboard
const redirectToDashboard = () => {
  if (selectedRole.value === 'rider') {
    router.push('/rider')
  } else {
    router.push('/driver')
  }
}
</script>
