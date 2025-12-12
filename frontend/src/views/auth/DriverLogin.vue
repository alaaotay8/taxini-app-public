<template>
  <div class="phone-screen">
    <!-- Header with Logo -->
    <div class="p-6 pt-16 text-center">
      <img src="/src/assets/logo.png" alt="Taxini" class="w-32 h-32 mx-auto object-contain" />
    </div>

    <!-- Content -->
    <div class="flex-1 flex flex-col justify-center px-8 py-8">
      <div class="space-y-6 animate-slide-up">
        <div class="mb-8">
          <h2 class="text-2xl font-semibold text-white mb-2">Welcome to RIIDE</h2>
        </div>

        <!-- Username Input -->
        <div class="space-y-2">
          <label class="block text-xs font-medium text-taxini-text-gray uppercase tracking-wider">
            Username
          </label>
          <input
            v-model="username"
            type="text"
            placeholder="Enter email or username"
            class="input-field-dark"
            @keyup.enter="handleLogin"
          />
        </div>

        <!-- Password Input -->
        <div class="space-y-2">
          <label class="block text-xs font-medium text-taxini-text-gray uppercase tracking-wider">
            Password
          </label>
          <input
            v-model="password"
            type="password"
            placeholder="Enter your password"
            class="input-field-dark"
            @keyup.enter="handleLogin"
          />
        </div>

        <!-- Remember me & Forgot password -->
        <div class="flex items-center justify-between">
          <label class="flex items-center gap-2 cursor-pointer">
            <input 
              v-model="rememberMe" 
              type="checkbox" 
              class="w-4 h-4 rounded border-gray-600 bg-[#0d2621] text-taxini-yellow focus:ring-taxini-yellow focus:ring-offset-0"
            />
            <span class="text-sm text-taxini-text-gray">Remember me</span>
          </label>
          <router-link to="/forgot-password" class="text-xs text-taxini-yellow hover:underline">
            Forgot password
          </router-link>
        </div>

        <!-- Error Message -->
        <transition name="fade">
          <div v-if="error" class="bg-red-500 bg-opacity-10 border border-red-500 text-red-500 px-4 py-3 rounded-xl text-sm">
            {{ error }}
          </div>
        </transition>

        <!-- Sign In Button -->
        <button
          @click="handleLogin"
          :disabled="loading || !username || !password"
          class="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
        >
          <span v-if="loading">Signing in...</span>
          <span v-else>Sign in</span>
        </button>

        <!-- Sign Up Link -->
        <div class="text-center pt-4">
          <span class="text-taxini-text-gray text-sm">Don't have an account ? </span>
          <router-link to="/driver-signup" class="text-taxini-yellow font-medium hover:underline text-sm">
            Sign up
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const rememberMe = ref(false)
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  error.value = ''
  
  if (!username.value || !password.value) {
    error.value = 'Please enter username and password'
    return
  }

  loading.value = true

  try {
    // Driver-specific login
    await authStore.loginWithEmail(username.value, password.value, 'driver')
    
    // Redirect to driver dashboard
    router.push('/driver/dashboard')
  } catch (err) {
    error.value = err.message || 'Login failed. Please check your credentials.'
  } finally {
    loading.value = false
  }
}
</script>
