<template>
  <div class="phone-screen">
    <!-- Header -->
    <div class="p-6 pt-12">
      <button @click="goBack" class="text-taxini-yellow mb-6">
        ← Back
      </button>
      <h1 class="text-4xl font-bold text-white flex items-center gap-2">
        <span class="text-taxini-yellow">🚕</span>
        <span>
          <span class="text-taxini-yellow">T</span>axini
        </span>
      </h1>
    </div>

    <!-- Content -->
    <div class="flex-1 flex flex-col px-6 py-8 overflow-y-auto">
      <div class="space-y-6 animate-slide-up">
        <div>
          <h2 class="text-3xl font-bold text-white mb-2">Complete Your Profile</h2>
          <p class="text-taxini-text-gray">Choose your role and fill in details</p>
        </div>

        <!-- Role Selection -->
        <div class="space-y-3">
          <label class="block text-sm font-medium text-taxini-text-gray uppercase tracking-wide">
            I want to be a
          </label>
          <div class="grid grid-cols-2 gap-3">
            <button
              @click="selectedRole = 'rider'"
              class="p-4 rounded-xl border-2 transition-all"
              :class="selectedRole === 'rider' ? 'border-taxini-yellow bg-taxini-yellow bg-opacity-10' : 'border-taxini-green bg-taxini-dark-light'"
            >
              <div class="text-3xl mb-2">👥</div>
              <div class="font-medium text-white">Rider</div>
            </button>
            <button
              @click="selectedRole = 'driver'"
              class="p-4 rounded-xl border-2 transition-all"
              :class="selectedRole === 'driver' ? 'border-taxini-yellow bg-taxini-yellow bg-opacity-10' : 'border-taxini-green bg-taxini-dark-light'"
            >
              <div class="text-3xl mb-2">🚗</div>
              <div class="font-medium text-white">Driver</div>
            </button>
          </div>
        </div>

        <!-- Common Fields -->
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-taxini-text-gray mb-2">NAME</label>
            <input v-model="formData.name" type="text" placeholder="Enter your name" class="input-field" />
          </div>

          <div>
            <label class="block text-sm font-medium text-taxini-text-gray mb-2">EMAIL</label>
            <input v-model="formData.email" type="email" placeholder="Enter email" class="input-field" />
          </div>
        </div>

        <!-- Rider-specific Fields -->
        <div v-if="selectedRole === 'rider'" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-taxini-text-gray mb-2">RESIDENCE PLACE</label>
            <input v-model="formData.residence_place" type="text" placeholder="Your city or area" class="input-field" />
          </div>
        </div>

        <!-- Driver-specific Fields -->
        <div v-if="selectedRole === 'driver'" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-taxini-text-gray mb-2">TAXI NUMBER</label>
            <input v-model="formData.taxi_number" type="text" placeholder="TN 12345 A" class="input-field" />
          </div>

          <div>
            <label class="block text-sm font-medium text-taxini-text-gray mb-2">ID CARD</label>
            <input @change="handleFileChange($event, 'id_card')" type="file" accept="image/*" class="input-field" />
          </div>

          <div>
            <label class="block text-sm font-medium text-taxini-text-gray mb-2">DRIVER LICENSE</label>
            <input @change="handleFileChange($event, 'license')" type="file" accept="image/*" class="input-field" />
          </div>
        </div>

        <!-- Error Message -->
        <transition name="fade">
          <div v-if="error" class="bg-red-500 bg-opacity-10 border border-red-500 text-red-500 px-4 py-3 rounded-xl text-sm">
            {{ error }}
          </div>
        </transition>

        <!-- Submit Button -->
        <button
          @click="handleSubmit"
          :disabled="loading || !isFormValid"
          class="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="loading">Creating Profile...</span>
          <span v-else>Complete Profile</span>
        </button>
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

const selectedRole = ref('rider')
const loading = ref(false)
const error = ref('')

const formData = ref({
  name: '',
  email: '',
  residence_place: '',
  taxi_number: '',
  id_card_file: null,
  driver_license_file: null
})

const isFormValid = computed(() => {
  if (!formData.value.name || !formData.value.email) return false
  
  if (selectedRole.value === 'rider') {
    return formData.value.residence_place !== ''
  } else if (selectedRole.value === 'driver') {
    return formData.value.taxi_number !== '' && 
           formData.value.id_card_file && 
           formData.value.driver_license_file
  }
  return false
})

const handleFileChange = (event, type) => {
  const file = event.target.files[0]
  if (file) {
    if (type === 'id_card') {
      formData.value.id_card_file = file
    } else if (type === 'license') {
      formData.value.driver_license_file = file
    }
  }
}

const handleSubmit = async () => {
  error.value = ''
  loading.value = true

  try {
    const profileData = {
      role: selectedRole.value,
      name: formData.value.name,
      email: formData.value.email,
    }

    if (selectedRole.value === 'rider') {
      profileData.residence_place = formData.value.residence_place
    } else if (selectedRole.value === 'driver') {
      profileData.taxi_number = formData.value.taxi_number
      profileData.account_status = 'locked'
      profileData.id_card_file = formData.value.id_card_file
      profileData.driver_license_file = formData.value.driver_license_file
    }

    await authStore.createProfile(profileData)

    // Navigate to appropriate dashboard
    if (selectedRole.value === 'rider') {
      router.push('/rider')
    } else if (selectedRole.value === 'driver') {
      router.push('/driver')
    }
  } catch (err) {
    error.value = err.message || 'Failed to create profile'
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}
</script>
