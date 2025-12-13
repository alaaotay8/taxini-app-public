import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
import 'mapbox-gl/dist/mapbox-gl.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Initialize auth state from localStorage before mounting
;(async () => {
  const { useAuthStore } = await import('./stores/auth')
  const authStore = useAuthStore()
  
  // If token exists, fetch current user to restore session
  if (authStore.token) {
    try {
      await authStore.getCurrentUser()
      console.log('✅ Session restored:', authStore.user?.role)
    } catch (error) {
      console.warn('⚠️ Failed to restore session:', error.message)
      // Token invalid, will be logged out by router guard
    }
  }
  
  app.mount('#app')
})()
