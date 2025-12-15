import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './style.css'
import 'mapbox-gl/dist/mapbox-gl.css'

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)

// Initialize auth state - restore session from HttpOnly cookie if exists
const authStore = useAuthStore()

authStore.getCurrentUser()
  .then(() => {
    app.use(router)
    app.mount('#app')
  })
  .catch(() => {
    app.use(router)
    app.mount('#app')
  })
