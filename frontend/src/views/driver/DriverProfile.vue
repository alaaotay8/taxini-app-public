<template>
  <div class="driver-profile">
    <!-- Header -->
    <div class="profile-header">
      <button @click="goBack" class="btn-back">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <h1 class="header-title">My Profile</h1>
      <div class="header-spacer"></div>
    </div>

    <!-- Content -->
    <div class="profile-content">
      <!-- Profile Picture & Basic Info -->
      <div class="profile-card">
        <div class="profile-picture-section">
          <div class="profile-picture">
            <img v-if="user.profile_picture" :src="user.profile_picture" alt="Profile" />
            <div v-else class="profile-initials">{{ userInitials }}</div>
          </div>
          <button @click="changeProfilePicture" class="btn-change-picture">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
        </div>

        <!-- User Info -->
        <div class="user-info-section">
          <h2 class="user-name">{{ user.name }}</h2>
          
          <!-- Status Badge -->
          <div class="status-badge-container">
            <div class="status-badge" :class="statusClass">
              <svg v-if="user.is_verified" xmlns="http://www.w3.org/2000/svg" class="status-icon-svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="status-text">{{ statusText }}</span>
            </div>
          </div>

          <!-- Contact Info -->
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
            <div class="info-row taxi-number">
              <svg xmlns="http://www.w3.org/2000/svg" class="info-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              </svg>
              <span class="info-text">Taxi #{{ user.taxi_number || 'Not Set' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <button @click="editProfile" class="btn-action primary">
          <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          <span>Edit Profile</span>
        </button>
        
        <button v-if="hasRiderProfile" @click="switchToRider" class="btn-action secondary">
          <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
          </svg>
          <span>Switch to Rider Mode</span>
        </button>
      </div>

      <!-- Documents Section -->
      <div class="documents-section">
        <h3 class="section-title">Documents</h3>
        
        <div class="document-card" @click="viewDocument('id')">
          <div class="document-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
            </svg>
          </div>
          <div class="document-info">
            <div class="document-name">National ID</div>
            <div class="document-status verified">
              <span class="status-dot"></span>
              <span>Verified</span>
            </div>
          </div>
          <svg xmlns="http://www.w3.org/2000/svg" class="chevron-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </div>

        <div class="document-card" @click="viewDocument('license')">
          <div class="document-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div class="document-info">
            <div class="document-name">Driver's License</div>
            <div class="document-status verified">
              <span class="status-dot"></span>
              <span>Verified</span>
            </div>
          </div>
          <svg xmlns="http://www.w3.org/2000/svg" class="chevron-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </div>

        <div class="document-card" @click="viewDocument('vehicle')">
          <div class="document-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
          </div>
          <div class="document-info">
            <div class="document-name">Vehicle Registration</div>
            <div class="document-status verified">
              <span class="status-dot"></span>
              <span>Verified</span>
            </div>
          </div>
          <svg xmlns="http://www.w3.org/2000/svg" class="chevron-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>

      <!-- Account Settings -->
      <div class="settings-section">
        <h3 class="section-title">Account Settings</h3>
        
        <button @click="changePassword" class="settings-item">
          <svg xmlns="http://www.w3.org/2000/svg" class="settings-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
          </svg>
          <span>Change Password</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="chevron-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>

        <button @click="privacySettings" class="settings-item">
          <svg xmlns="http://www.w3.org/2000/svg" class="settings-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          <span>Privacy & Security</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="chevron-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>

        <button @click="deleteAccount" class="settings-item danger">
          <svg xmlns="http://www.w3.org/2000/svg" class="settings-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          <span>Delete Account</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="chevron-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Edit Profile Modal -->
    <transition name="modal-fade">
      <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h2 class="modal-title">Edit Profile</h2>
            <button @click="closeEditModal" class="btn-close-modal">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form @submit.prevent="saveProfile" class="modal-content">
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
              <label class="form-label">Taxi Number</label>
              <input 
                v-model="editForm.taxi_number" 
                type="text" 
                class="form-input"
                placeholder="Enter taxi number"
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

const user = computed(() => authStore.user || {
  name: 'Karim Jebali',
  phone: '+216 12 345 682',
  email: 'karim.jebali@example.com',
  taxi_number: '1234',
  account_status: 'verified', // verified, locked, banned
  profile_picture: null
})

const hasRiderProfile = ref(true)

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
  taxi_number: ''
})

const userInitials = computed(() => {
  const name = user.value.name || 'D'
  const names = name.split(' ')
  if (names.length >= 2) {
    return `${names[0][0]}${names[1][0]}`.toUpperCase()
  }
  return name[0].toUpperCase()
})

const statusClass = computed(() => {
  const status = user.value.account_status || 'verified'
  return {
    'verified': status === 'verified',
    'locked': status === 'locked',
    'banned': status === 'banned'
  }
})

const statusIcon = computed(() => {
  const status = user.value.account_status || 'verified'
  return {
    'verified': '✅',
    'locked': '🔒',
    'banned': '🚫'
  }[status]
})

const statusText = computed(() => {
  const status = user.value.account_status || 'verified'
  return {
    'verified': 'Verified Driver',
    'locked': 'Account Locked',
    'banned': 'Account Banned'
  }[status]
})

const goBack = () => {
  router.back()
}

const changeProfilePicture = () => {
  // In a real app, this would open a file picker
  toastMessage.value = 'Profile picture upload feature coming soon!'
  showSuccessToast.value = true
  setTimeout(() => {
    showSuccessToast.value = false
  }, 3000)
}

const editProfile = () => {
  // Initialize form with current user data
  editForm.value = {
    name: user.value.name,
    phone: user.value.phone,
    email: user.value.email,
    taxi_number: user.value.taxi_number || ''
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
    
    // Update user data (in real app, this would be an API call)
    Object.assign(user.value, editForm.value)
    
    // Close modal
    showEditModal.value = false
    
    // Show success toast
    toastMessage.value = 'Profile updated successfully!'
    showSuccessToast.value = true
    
    // Hide toast after 3 seconds
    setTimeout(() => {
      showSuccessToast.value = false
    }, 3000)
  } catch (error) {
    console.error('Error saving profile:', error)
    toastMessage.value = 'Failed to update profile'
    showSuccessToast.value = true
    setTimeout(() => {
      showSuccessToast.value = false
    }, 3000)
  } finally {
    saving.value = false
  }
}

const switchToRider = () => {
  router.push('/rider/dashboard')
}

const viewDocument = (type) => {
  toastMessage.value = `${type} document viewer opening...`
  showSuccessToast.value = true
  setTimeout(() => {
    showSuccessToast.value = false
  }, 3000)
}

const changePassword = () => {
  toastMessage.value = 'Password change feature coming soon!'
  showSuccessToast.value = true
  setTimeout(() => {
    showSuccessToast.value = false
  }, 3000)
}

const privacySettings = () => {
  toastMessage.value = 'Privacy settings feature coming soon!'
  showSuccessToast.value = true
  setTimeout(() => {
    showSuccessToast.value = false
  }, 3000)
}

const deleteAccount = () => {
  if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
    toastMessage.value = 'Account deletion requested'
    showSuccessToast.value = true
    setTimeout(() => {
      showSuccessToast.value = false
    }, 3000)
  }
}
</script>

<style scoped src="./DriverProfile.css"></style>
