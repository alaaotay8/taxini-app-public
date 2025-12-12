<template>
  <div class="profile-container">
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
      <!-- Profile Picture Section -->
      <div class="profile-picture-section">
        <div class="profile-picture-wrapper">
          <div v-if="!profilePicture" class="profile-picture-placeholder">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <img v-else :src="profilePicture" alt="Profile" class="profile-picture" />
          <button @click="triggerFileUpload" class="btn-change-picture">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
          <input ref="fileInput" type="file" accept="image/*" @change="handleFileUpload" class="hidden-file-input" />
        </div>
      </div>

      <!-- Profile Information -->
      <div class="profile-info-section">
        <!-- Name -->
        <div class="info-card">
          <div class="info-label">
            <svg xmlns="http://www.w3.org/2000/svg" class="info-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span>Full Name</span>
          </div>
          <div class="info-value">{{ user.name }}</div>
        </div>

        <!-- Phone -->
        <div class="info-card">
          <div class="info-label">
            <svg xmlns="http://www.w3.org/2000/svg" class="info-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
            <span>Phone Number</span>
          </div>
          <div class="info-value-with-badge">
            <span>{{ user.phone }}</span>
            <span class="verified-badge">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Verified
            </span>
          </div>
        </div>

        <!-- Email -->
        <div class="info-card">
          <div class="info-label">
            <svg xmlns="http://www.w3.org/2000/svg" class="info-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <span>Email Address</span>
          </div>
          <div class="info-value">{{ user.email }}</div>
        </div>

        <!-- Residence -->
        <div class="info-card">
          <div class="info-label">
            <svg xmlns="http://www.w3.org/2000/svg" class="info-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span>Residence</span>
          </div>
          <div class="info-value">{{ user.residence || 'Not set' }}</div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <button @click="editProfile" class="btn-edit-profile">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          Edit Profile
        </button>

        <button v-if="user.hasDriverProfile" @click="switchToDriver" class="btn-switch-driver">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
          </svg>
          Switch to Driver
        </button>
      </div>
    </div>

    <!-- Edit Profile Modal -->
    <transition name="modal-fade">
      <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h2 class="modal-title">Edit Profile</h2>
            <button @click="closeEditModal" class="btn-close-modal">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form @submit.prevent="saveProfile" class="modal-form">
            <div class="form-group">
              <label class="form-label">Full Name</label>
              <input 
                v-model="editForm.name" 
                type="text" 
                class="form-input"
                placeholder="Enter your full name"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">Phone Number</label>
              <input 
                v-model="editForm.phone" 
                type="tel" 
                class="form-input"
                placeholder="+216 XX XXX XXX"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">Email Address</label>
              <input 
                v-model="editForm.email" 
                type="email" 
                class="form-input"
                placeholder="your.email@example.com"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">Residence</label>
              <input 
                v-model="editForm.residence" 
                type="text" 
                class="form-input"
                placeholder="City, Country"
              />
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
  residence: 'Tunis, Tunisia',
  hasDriverProfile: false
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
    residence: user.value.residence || ''
  }
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
}

const saveProfile = async () => {
  saving.value = true
  
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // TODO: Update user profile via API
    // await authStore.updateProfile(editForm.value)
    
    toastMessage.value = 'Profile updated successfully!'
    showSuccessToast.value = true
    showEditModal.value = false
    
    // Hide toast after 3 seconds
    setTimeout(() => {
      showSuccessToast.value = false
    }, 3000)
  } catch (error) {
    console.error('Error updating profile:', error)
    toastMessage.value = 'Failed to update profile'
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
.profile-container {
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
  max-width: 640px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.profile-picture-section {
  display: flex;
  justify-content: center;
  margin-bottom: 2.5rem;
}

.profile-picture-wrapper {
  position: relative;
}

.profile-picture-placeholder,
.profile-picture {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: rgba(255, 208, 0, 0.1);
  border: 3px solid rgba(255, 208, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  object-fit: cover;
}

.profile-picture-placeholder svg {
  width: 60px;
  height: 60px;
  color: rgba(255, 208, 0, 0.6);
}

.btn-change-picture {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #FFD000;
  border: 3px solid #0a1f1a;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
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

.profile-info-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
}

.info-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 1.25rem;
}

.info-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: #FFD000;
}

.info-value {
  color: white;
  font-size: 1.0625rem;
  font-weight: 500;
}

.info-value-with-badge {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.info-value-with-badge span:first-child {
  color: white;
  font-size: 1.0625rem;
  font-weight: 500;
}

.verified-badge {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 12px;
  color: #22c55e;
  font-size: 0.75rem;
  font-weight: 600;
}

.verified-badge svg {
  width: 1rem;
  height: 1rem;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.btn-edit-profile,
.btn-switch-driver {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-edit-profile {
  background: #FFD000;
  color: #0a1f1a;
}

.btn-edit-profile:hover {
  background: #ffed4e;
  transform: translateY(-2px);
}

.btn-switch-driver {
  background: rgba(255, 208, 0, 0.1);
  border: 2px solid rgba(255, 208, 0, 0.3);
  color: #FFD000;
}

.btn-switch-driver:hover {
  background: rgba(255, 208, 0, 0.15);
  border-color: rgba(255, 208, 0, 0.5);
  transform: translateY(-2px);
}

.btn-edit-profile svg,
.btn-switch-driver svg {
  width: 1.25rem;
  height: 1.25rem;
}

@media (max-width: 640px) {
  .profile-content {
    padding: 1.5rem 1rem;
  }
  
  .profile-picture-placeholder,
  .profile-picture {
    width: 100px;
    height: 100px;
  }
  
  .profile-picture-placeholder svg {
    width: 50px;
    height: 50px;
  }
  
  .btn-change-picture {
    width: 36px;
    height: 36px;
  }
  
  .btn-change-picture svg {
    width: 18px;
    height: 18px;
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
  background: rgba(13, 38, 33, 0.98);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 2px solid rgba(255, 208, 0, 0.3);
  border-radius: 24px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-title {
  font-size: 1.375rem;
  font-weight: 700;
  color: white;
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
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group:last-of-type {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 0.5rem;
}

.form-input {
  width: 100%;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  padding: 0.875rem 1rem;
  color: white;
  font-size: 0.9375rem;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 208, 0, 0.5);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-modal-cancel,
.btn-modal-save {
  flex: 1;
  padding: 0.875rem;
  border-radius: 10px;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-modal-cancel {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.btn-modal-cancel:hover {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.5);
}

.btn-modal-save {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: #FFD000;
  color: #0a1f1a;
}

.btn-modal-save:hover:not(:disabled) {
  background: #ffed4e;
  transform: translateY(-1px);
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
