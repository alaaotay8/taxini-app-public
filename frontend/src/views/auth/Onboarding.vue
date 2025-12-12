<template>
  <div class="phone-screen overflow-hidden">
    <!-- Onboarding Slider -->
    <div class="flex-1 flex flex-col items-center justify-between px-6 py-8 h-full">
      <!-- Slide Content -->
      <transition name="fade" mode="out-in">
        <div :key="currentSlide" class="w-full text-center animate-fade-in flex flex-col items-center">
          <!-- Logo -->
          <div class="mb-4">
            <img src="/src/assets/logo.png" alt="Taxini" class="w-32 h-32 mx-auto object-contain" />
          </div>

          <!-- Illustration -->
          <div class="mb-4 h-64 flex items-center justify-center">
            <div v-if="currentSlide === 0" class="animate-slide-up">
              <!-- Taxi Car Image -->
              <img src="/src/assets/taxi-car2.png" alt="Order Taxi" class="w-72 h-auto object-contain" />
            </div>

            <div v-else-if="currentSlide === 1" class="animate-slide-up">
              <!-- Request Taxi Image -->
              <img src="/src/assets/RequestTaxi.png" alt="Request Taxi" class="w-72 h-auto object-contain" />
            </div>

            <div v-else-if="currentSlide === 2" class="animate-slide-up">
              <!-- Confirm Driver Image -->
              <img src="/src/assets/ConfirmDriver.png" alt="Confirm Driver" class="w-72 h-auto object-contain" />
            </div>

            <div v-else-if="currentSlide === 3" class="animate-slide-up">
              <!-- Track Ride Image -->
              <img src="/src/assets/TrackRide.png" alt="Track Ride" class="w-72 h-auto object-contain" />
            </div>

            <div v-else-if="currentSlide === 4" class="animate-slide-up">
              <!-- Success Image -->
              <img src="/src/assets/SucessRide.png" alt="Success" class="w-72 h-auto object-contain" />
            </div>
          </div>

          <!-- Title & Description -->
          <div class="space-y-3 px-4">
            <h2 class="text-2xl font-bold text-white">
              {{ slides[currentSlide].title }}
            </h2>
            <p class="text-taxini-text-gray text-sm leading-relaxed">
              {{ slides[currentSlide].description }}
            </p>
          </div>
        </div>
      </transition>

      <!-- Pagination Dots -->
      <div class="flex gap-2 mt-6">
        <div
          v-for="(slide, index) in slides"
          :key="index"
          class="h-2 rounded-full transition-all duration-300"
          :class="index === currentSlide ? 'w-8 bg-taxini-yellow' : 'w-2 bg-taxini-green'"
        ></div>
      </div>

      <!-- Get Started Button / Skip Button -->
      <div class="w-full mt-6">
        <transition name="slide" mode="out-in">
          <button
            v-if="currentSlide === slides.length - 1"
            @click="goToLogin"
            class="btn-primary w-full text-lg"
          >
            Get Started
          </button>
          <button
            v-else
            @click="nextSlide"
            class="w-full py-4 text-taxini-yellow font-medium"
          >
            Skip →
          </button>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const currentSlide = ref(0)
let autoPlayInterval = null

const slides = [
  {
    title: 'Order your Taxi',
    description: 'Please login to book your Ride taxi or courier service.'
  },
  {
    title: 'Request Taxi',
    description: 'Request a ride get picked up by a nearby community driver'
  },
  {
    title: 'Confirm Your Driver',
    description: 'Huge drivers network helps you find comfortable, safe and cheap'
  },
  {
    title: 'Track your ride',
    description: 'Know your driver in advance and be able to view current location in real time on the map'
  },
  {
    title: "You're good to go!",
    description: 'You are now one of our validated partner couriers. Expect your uniform delivered soon.'
  }
]

const nextSlide = () => {
  if (currentSlide.value < slides.length - 1) {
    currentSlide.value++
  } else {
    goToLogin()
  }
}

const goToLogin = () => {
  router.push('/login')
}

// Auto-play slides
const startAutoPlay = () => {
  autoPlayInterval = setInterval(() => {
    nextSlide()
  }, 4000) // Change slide every 4 seconds
}

const stopAutoPlay = () => {
  if (autoPlayInterval) {
    clearInterval(autoPlayInterval)
  }
}

onMounted(() => {
  startAutoPlay()
})

onUnmounted(() => {
  stopAutoPlay()
})
</script>

<style scoped>
/* Swipe gesture support (optional) */
.phone-screen {
  touch-action: pan-y;
}
</style>
