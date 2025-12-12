<template>
  <div class="taxini-logo" :class="sizeClass">
    <div class="logo-icon">
      <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <!-- Taxi body -->
        <rect x="15" y="40" width="70" height="35" rx="8" fill="#FFD000"/>
        <!-- Windows -->
        <rect x="25" y="45" width="20" height="15" rx="2" fill="#0a1f1a" opacity="0.3"/>
        <rect x="55" y="45" width="20" height="15" rx="2" fill="#0a1f1a" opacity="0.3"/>
        <!-- Wheels -->
        <circle cx="30" cy="75" r="8" fill="#2d2d2d"/>
        <circle cx="70" cy="75" r="8" fill="#2d2d2d"/>
        <circle cx="30" cy="75" r="4" fill="#666"/>
        <circle cx="70" cy="75" r="4" fill="#666"/>
        <!-- Taxi sign -->
        <rect x="40" y="30" width="20" height="8" rx="2" fill="#FFD000"/>
        <text x="50" y="36" font-size="6" text-anchor="middle" fill="#0a1f1a" font-weight="bold">TAXI</text>
        <!-- Headlight -->
        <circle cx="12" cy="50" r="3" fill="#FFF" opacity="0.8"/>
      </svg>
    </div>
    <div class="logo-text" v-if="showText">
      <span class="logo-t">T</span><span class="logo-rest">axini</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: String,
    default: 'md', // sm, md, lg, xl
    validator: (value) => ['sm', 'md', 'lg', 'xl'].includes(value)
  },
  showText: {
    type: Boolean,
    default: true
  }
})

const sizeClass = computed(() => `logo-${props.size}`)
</script>

<style scoped>
.taxini-logo {
  @apply flex flex-col items-center justify-center gap-2;
}

.logo-icon svg {
  @apply drop-shadow-lg;
}

/* Size variations */
.logo-sm .logo-icon {
  @apply w-8 h-8;
}

.logo-sm .logo-text {
  @apply text-xl;
}

.logo-md .logo-icon {
  @apply w-12 h-12;
}

.logo-md .logo-text {
  @apply text-3xl;
}

.logo-lg .logo-icon {
  @apply w-16 h-16;
}

.logo-lg .logo-text {
  @apply text-4xl;
}

.logo-xl .logo-icon {
  @apply w-24 h-24;
}

.logo-xl .logo-text {
  @apply text-6xl;
}

.logo-text {
  @apply font-bold;
}

.logo-t {
  @apply text-taxini-yellow;
}

.logo-rest {
  @apply text-white;
}

/* Animation */
.logo-icon {
  @apply transition-transform duration-300;
}

.taxini-logo:hover .logo-icon {
  @apply scale-110;
}
</style>
