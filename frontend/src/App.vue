<template>
  <div id="app">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
    <NotificationManager />
  </div>
</template>

<script setup>
import NotificationManager from './components/NotificationManager.vue'
</script>

<style>
#app {
  width: 100%;
  min-height: 100vh;
}
</style>
