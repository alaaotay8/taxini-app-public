<template>
  <div class="rider-profile">
    <!-- Header -->
    <div class="profile-header">
      <button @click="goBack" class="btn-back">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <h1 class="header-title">My Profile</h1>
      <div class="header-spacer"></div>
    </div>

    <!-- Profile Content -->
    <div class="profile-content">
      <div class="profile-card">
        <div class="profile-picture-section">
          <div class="profile-picture">
            <img v-if="displayProfilePicture" :src="displayProfilePicture" alt="Profile" />
            <div v-else class="profile-initials">{{ userInitials }}</div>
          </div>

          <button @click="triggerFileUpload" class="btn-change-picture">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
          <input ref="fileInput" type="file" accept="image/*" @change="handleFileUpload" class="hidden-file-input" />
        </div>

        <div class="user-info-section">
          <h2 class="user-name">{{ user.name }}</h2>

          <div class="status-badge-container">
            <div class="status-badge verified">
              <svg xmlns="http://www.w3.org/2000/svg" class="status-icon-svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="status-text">Verified Rider</span>
            </div>
          </div>

          <div class="contact-info">
            <div class="info-row">
              <svg xmlns="http://www.w3.org/2000/svg" class="info-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              <span class="info-text">{{ user.phone }}</span>
            </div>

            <div class="info-row">
              <svg xmlns="http://www.w3.org/2000/svg" class="info-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <span class="info-text">{{ user.email }}</span>
            </div>

            <div class="info-row">
              <svg xmlns="http://www.w3.org/2000/svg" class="info-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span class="info-text">{{ userResidence || 'Not set' }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="action-buttons">
        <button @click="editProfile" class="btn-action primary">
          <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          <span>Edit Profile</span>
        </button>

        <button v-if="user.hasDriverProfile" @click="switchToDriver" class="btn-action secondary">
          <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
          </svg>
          <span>Switch to Driver Mode</span>
        </button>
      </div>
    </div>

    <!-- Edit Modal -->
    <transition name="modal-fade">
      <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2 class="modal-title">Edit Profile</h2>
            <button type="button" @click="closeEditModal" class="btn-close-modal">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <form @submit.prevent="saveProfile" class="modal-form">
            <div class="form-group">
              <label class="form-label">Name</label>
              <div class="input-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" class="input-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <input v-model="editForm.name" type="text" class="form-input" placeholder="Enter your full name" required />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Phone</label>
              <div class="input-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" class="input-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                <input v-model="editForm.phone" type="tel" class="form-input" placeholder="+216 12 345 678" required />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Email</label>
              <div class="input-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" class="input-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <input v-model="editForm.email" type="email" class="form-input" placeholder="your.email@example.com" required />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Residence</label>
              <div class="input-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" class="input-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <input v-model="editForm.residence" type="text" class="form-input" placeholder="City, Country" />
              </div>
            </div>

            <div class="modal-actions">
              <button type="button" @click="closeEditModal" class="btn-modal-cancel">
                Cancel
              </button>
              <button type="submit" class="btn-modal-save" :disabled="saving">
                <span v-if="!saving">Save Changes</span>
                <span v-else class="saving-spinner">
                  <svg class="spinner" viewBox="0 0 24 24">
                    <circle class="spinner-circle" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
                  </svg>
                  Saving...
                </span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </transition>

    <!-- Success Toast -->
    <transition name="toast-slide">
      <div v-if="showSuccessToast" class="success-toast">
        <svg xmlns="http://www.w3.org/2000/svg" class="toast-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ toastMessage }}</span>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { userAPI } from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()
const fileInput = ref(null)
const profilePicture = ref(null)

// Modal state
const showEditModal = ref(false)
const saving = ref(false)
const showSuccessToast = ref(false)
const toastMessage = ref('')

// Edit form
const editForm = ref({
  name: '',
  phone: '',
  email: '',
  residence: ''
})

const user = computed(() => authStore.user || {
  name: 'Ahmed Ben Ali',
  phone: '+216 12 345 678',
  email: 'ahmed@example.com',
  residence_place: 'Tunis, Tunisia',
  hasDriverProfile: false
})

const userResidence = computed(() => user.value?.residence || user.value?.residence_place || '')

const userInitials = computed(() => {
  const name = user.value?.name || 'R'
  const parts = String(name).trim().split(/\s+/).filter(Boolean)
  if (parts.length >= 2) {
    return `${parts[0][0]}${parts[1][0]}`.toUpperCase()
  }
  return String(name).trim().charAt(0).toUpperCase() || 'R'
})

const displayProfilePicture = computed(() => {
  return profilePicture.value || user.value?.profile_picture || null
})

const goBack = () => {
  router.back()
}

const triggerFileUpload = () => {
  fileInput.value.click()
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      profilePicture.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const editProfile = () => {
  // Populate form with current data
  editForm.value = {
    name: user.value.name,
    phone: user.value.phone,
    email: user.value.email,
    residence: user.value.residence || user.value.residence_place || ''
  }
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
}

const saveProfile = async () => {
  saving.value = true
  
  try {
    console.log('💾 Saving profile changes to database:', editForm.value)
    
    // Call backend API to update profile in database
    const response = await userAPI.updateProfile({
      name: editForm.value.name,
      email: editForm.value.email,
      residence_place: editForm.value.residence
    })
    
    console.log('✅ Profile update response from backend:', response)
    
    // Refresh user data from backend to get latest values
    await authStore.getCurrentUser()
    
    console.log('✅ Profile saved and refreshed from database')
    toastMessage.value = 'Profile updated successfully!'
    
    showSuccessToast.value = true
    showEditModal.value = false
    
    // Hide toast after 3 seconds
    setTimeout(() => {
      showSuccessToast.value = false
    }, 3000)
  } catch (error) {
    console.error('❌ Error updating profile:', error)
    console.error('❌ Error details:', {
      message: error.message,
      response: error.response,
      status: error.response?.status,
      data: error.response?.data
    })
    
    let errorMessage = 'Failed to update profile'
    
    if (error.response?.status === 401) {
      errorMessage = 'Session expired. Please log in again.'
    } else if (error.response?.status === 403) {
      errorMessage = 'You do not have permission to update this profile.'
    } else if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail
    } else if (error.message) {
      errorMessage = error.message
    }
    
    toastMessage.value = errorMessage
    showSuccessToast.value = true
    setTimeout(() => {
      showSuccessToast.value = false
    }, 3000)
  } finally {
    saving.value = false
  }
}

const switchToDriver = () => {
  router.push('/driver')
}
</script>

<style scoped>
.rider-profile {
  min-height: 100vh;
  background: #0a1f1a;
  padding-bottom: 2rem;
}

.profile-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(13, 38, 33, 0.95);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 208, 0, 0.2);
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.btn-back {
  background: transparent;
  border: none;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  color: white;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.1);
}

.btn-back svg {
  width: 1.5rem;
  height: 1.5rem;
}

.header-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: white;
}

.header-spacer {
  width: 2.5rem;
}

.profile-content {
  max-width: 768px;
  margin: 0 auto;
  padding: 1.5rem;
}

.profile-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255, 208, 0, 0.2);
  margin-bottom: 1.5rem;
}

.profile-picture-section {
  position: relative;
  width: fit-content;
  margin: 0 auto 1.5rem;
}

.profile-picture {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid #FFD000;
  box-shadow: 0 6px 20px rgba(255, 208, 0, 0.3);
}

.profile-picture img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-initials {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #FFD000 0%, #ff8800 100%);
  color: #0a1f1a;
  font-size: 2.5rem;
  font-weight: 800;
}

.btn-change-picture {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #FFD000;
  border: 3px solid #0a1f1a;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  color: #0a1f1a;
}

.btn-change-picture:hover {
  transform: scale(1.1);
  background: #ffed4e;
}


.btn-change-picture svg {
  width: 20px;
  height: 20px;
  color: #0a1f1a;
}

.hidden-file-input {
  display: none;
}


.user-info-section {
  text-align: center;
}

.user-name {
  font-size: 1.75rem;
  font-weight: 800;
  color: white;
  margin-bottom: 1rem;
}

.status-badge-container {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.5rem;
  border-radius: 25px;
  font-weight: 700;
  font-size: 1rem;
  border: 2px solid;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.status-badge.verified {
  background: rgba(34, 197, 94, 0.25);
  color: #22c55e;
  border-color: #22c55e;
}

.status-icon-svg {
  width: 1.5rem;
  height: 1.5rem;
  stroke-width: 2.5;
  flex-shrink: 0;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
}

.info-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: #FFD000;
}

.info-text {
  font-size: 1rem;
}

.action-buttons {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.btn-action {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-radius: 14px;
  font-weight: 700;
  font-size: 1rem;
  border: 2px solid;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-action.primary {
  background: #FFD000;
  border-color: #FFD000;
  color: #0a1f1a;
}

.btn-action.primary:hover {
  background: #ffed4e;
  transform: translateY(-2px);
}

.btn-action.secondary {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.3);
  color: white;
}

.btn-action.secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
}

.btn-icon {
  width: 1.25rem;
  height: 1.25rem;
}

@media (max-width: 640px) {
  .profile-content {
    padding: 1.5rem 1rem;
  }

  .profile-picture {
    width: 100px;
    height: 100px;
  }

  .btn-change-picture {
    width: 36px;
    height: 36px;
  }
}

/* ===================================
   Edit Profile Modal
   =================================== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: linear-gradient(135deg, rgba(13, 38, 33, 0.98) 0%, rgba(10, 31, 26, 0.98) 100%);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 2px solid rgba(255, 208, 0, 0.3);
  border-radius: 24px;
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 208, 0, 0.1);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.75rem 1.5rem;
  border-bottom: 1px solid rgba(255, 208, 0, 0.15);
  background: rgba(255, 208, 0, 0.05);
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  letter-spacing: -0.02em;
}

.btn-close-modal {
  background: transparent;
  border: none;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  color: rgba(255, 255, 255, 0.6);
}

.btn-close-modal:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.btn-close-modal svg {
  width: 1.5rem;
  height: 1.5rem;
}

.modal-form {
  padding: 2rem 1.5rem 1.5rem;
  max-height: calc(90vh - 100px);
  overflow-y: auto;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group:last-of-type {
  margin-bottom: 0;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  width: 1.25rem;
  height: 1.25rem;
  color: rgba(255, 208, 0, 0.6);
  pointer-events: none;
  z-index: 1;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0.625rem;
  letter-spacing: 0.01em;
}

.form-input {
  width: 100%;
  background: rgba(255, 255, 255, 0.05);
  border: 1.5px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 0.875rem 1rem 0.875rem 3rem;
  color: white;
  font-size: 0.9375rem;
  transition: all 0.3s ease;
  font-weight: 500;
}

.form-input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 208, 0, 0.6);
  box-shadow: 0 0 0 3px rgba(255, 208, 0, 0.1);
}

.form-input:focus + .input-icon {
  color: rgba(255, 208, 0, 1);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.35);
  font-weight: 400;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.btn-modal-cancel,
.btn-modal-save {
  flex: 1;
  padding: 1rem;
  border-radius: 12px;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  letter-spacing: 0.01em;
}

.btn-modal-cancel {
  background: rgba(239, 68, 68, 0.08);
  border: 1.5px solid rgba(239, 68, 68, 0.4);
  color: #ef4444;
}

.btn-modal-cancel:hover {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.6);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

.btn-modal-save {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #FFD000 0%, #FFC700 100%);
  color: #0a1f1a;
  box-shadow: 0 4px 12px rgba(255, 208, 0, 0.3);
}

.btn-modal-save:hover:not(:disabled) {
  background: linear-gradient(135deg, #ffed4e 0%, #FFD000 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 208, 0, 0.4);
}

.btn-modal-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.saving-spinner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.spinner {
  width: 1.25rem;
  height: 1.25rem;
  animation: spin 1s linear infinite;
}

.spinner-circle {
  stroke-dasharray: 50;
  stroke-dashoffset: 25;
  opacity: 0.5;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* ===================================
   Success Toast
   =================================== */
.success-toast {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background: rgba(34, 197, 94, 0.95);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: white;
  font-weight: 600;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  z-index: 1001;
}

.toast-icon {
  width: 1.5rem;
  height: 1.5rem;
  flex-shrink: 0;
}

/* ===================================
   Animations
   =================================== */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-active .modal-content,
.modal-fade-leave-active .modal-content {
  transition: transform 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .modal-content,
.modal-fade-leave-to .modal-content {
  transform: scale(0.9);
}

.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: all 0.3s ease;
}

.toast-slide-enter-from,
.toast-slide-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(2rem);
}
</style>
