<template>
  <div class="rider-dashboard">
    <!-- Header -->
    <div class="bg-taxini-dark-light border-b border-taxini-green/20 px-6 py-4 flex items-center justify-between shadow-lg fixed top-0 left-0 right-0 z-50">
      <button @click="showSideMenu = true" class="text-white">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      <div class="text-center">
        <h1 class="text-xl font-bold text-white">Hello, {{ user.name.split(' ')[0] }}!</h1>
        <p class="text-xs text-taxini-yellow">Where would you like to go?</p>
      </div>
      <button @click="toggleNotifications" class="text-white relative">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        <span v-if="unreadNotifications > 0" class="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">{{ unreadNotifications }}</span>
      </button>
    </div>

    <!-- Notifications Panel -->
    <transition name="slide-left">
      <div v-if="showNotificationsPanel" class="notifications-overlay" @click="toggleNotifications">
        <div class="notifications-panel" @click.stop>
          <div class="notifications-header">
            <h2 class="notifications-title">Notifications</h2>
            <button @click="toggleNotifications" class="btn-close-notifications">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="notifications-content">
            <div v-if="notifications.length === 0" class="notifications-empty">
              <svg xmlns="http://www.w3.org/2000/svg" class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <p class="empty-text">No notifications yet</p>
            </div>

            <div v-else class="notifications-list">
              <div 
                v-for="notification in notifications" 
                :key="notification.id" 
                class="notification-item"
                :class="{ 'unread': !notification.read }"
                @click="markAsRead(notification.id)"
              >
                <div class="notification-icon" :class="notification.type">
                  <svg v-if="notification.type === 'trip'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <svg v-else-if="notification.type === 'cancelled'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <svg v-else-if="notification.type === 'earnings'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="notification-content">
                  <h4 class="notification-title">{{ notification.title }}</h4>
                  <p class="notification-message">{{ notification.message }}</p>
                  <span class="notification-time">{{ notification.time }}</span>
                </div>
                <div v-if="!notification.read" class="unread-dot"></div>
              </div>
            </div>
          </div>

          <button @click="clearAllNotifications_func" class="btn-clear-all" v-if="notifications.length > 0">
            Clear All
          </button>
        </div>
      </div>
    </transition>

    <!-- Map Container -->
    <div class="map-wrapper">
      <!-- Mapbox Map -->
      <div ref="mapContainer" class="map-container" @click="(e) => handleMapClick(e, showTripDetails)"></div>

      <!-- Map Controls Group (Zoom + Location) -->
      <div class="map-controls-group">
        <!-- Zoom In -->
        <button @click="zoomIn" class="map-control-btn" title="Zoom in">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
          </svg>
        </button>
        
        <!-- Zoom Out -->
        <button @click="zoomOut" class="map-control-btn" title="Zoom out">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
            <path stroke-linecap="round" stroke-linejoin="round" d="M20 12H4"/>
          </svg>
        </button>
        
        <!-- Location Button -->
        <button @click="recenterToMyLocation" class="map-control-btn map-control-location" title="Return to current location">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </button>
      </div>

      <!-- Show Bottom Sheet Button or Compact Trip Info -->
      <transition name="fade">
        <!-- Yellow button for search/non-active states -->
        <div v-if="!showBottomSheet && !showSideMenu && tripState !== 'active'" class="show-sheet-btn" @click="toggleBottomSheet">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="18 15 12 9 6 15"/>
          </svg>
        </div>
        
        <!-- Compact Navigation Card for active trips (replaces yellow button) -->
        <div 
          v-else-if="tripState === 'active' && !showBottomSheet && !showSideMenu"
          @click="showTripDetails = true; showBottomSheet = true"
          class="fixed bottom-6 left-1/2 transform -translate-x-1/2 z-40 w-[calc(100%-32px)] max-w-lg"
        >
          <div class="bg-gradient-to-br from-taxini-green to-taxini-green-dark rounded-2xl p-5 cursor-pointer transition-all hover:shadow-lg border border-taxini-yellow/20 shadow-xl">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-4">
                <div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                  </svg>
                </div>
                <div>
                  <p class="text-white font-bold text-base mb-1">En Route to Destination</p>
                  <div class="flex items-center gap-5 mt-1">
                    <div class="flex items-center gap-1.5">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-taxini-yellow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span class="text-white text-sm font-mono font-medium">{{ Math.floor(tripDuration / 60) }}:{{ String(tripDuration % 60).padStart(2, '0') }}</span>
                    </div>
                    <div class="flex items-center gap-1.5">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-taxini-yellow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                      </svg>
                      <span class="text-white text-sm font-mono font-medium">{{ tripDistance.toFixed(2) }} km</span>
                    </div>
                  </div>
                </div>
              </div>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
              </svg>
            </div>
          </div>
        </div>
      </transition>

      <!-- Destination Confirmation Overlay -->
      <transition name="fade">
        <div 
          v-if="showDestinationConfirmation" 
          class="destination-confirmation"
          :class="{ 'destination-confirmation-raised': showBottomSheet }"
        >
          <div class="confirmation-card">
            <div class="confirmation-header">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-taxini-yellow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span class="text-white font-bold">Confirm Destination</span>
            </div>
            <p class="text-white/80 text-sm mt-2">{{ destination }}</p>
            <div class="confirmation-actions">
              <button @click="handleCancelDestination" class="btn-cancel">
                Cancel
              </button>
              <button @click="handleConfirmDestination" class="btn-confirm">
                Confirm
              </button>
            </div>
          </div>
        </div>
      </transition>

      <!-- Bottom Sheet -->
      <transition name="slide-up">
        <div 
          v-if="showBottomSheet"
          class="absolute bottom-0 left-0 right-0 bg-taxini-dark-light rounded-t-3xl shadow-2xl transition-all duration-300 z-30" 
          :class="bottomSheetHeight"
          @touchstart="handleBottomSheetTouchStart"
          @touchmove="handleBottomSheetTouchMove"
          @touchend="handleBottomSheetTouchEnd"
        >
          <!-- Sheet Handle -->
          <div class="flex justify-center pt-3 pb-2 cursor-pointer" @click="toggleBottomSheet">
            <div class="w-12 h-1.5 bg-taxini-text-gray/30 rounded-full hover:bg-taxini-yellow/60 transition-all"></div>
          </div>

        <!-- Search/Request Trip View -->
        <div v-if="tripState === 'search'" class="px-6 pb-6">
          <h2 class="text-2xl font-bold text-white mb-6">Where to?</h2>
          
          <!-- Pickup Location -->
          <div class="mb-4">
            <label class="block text-sm font-bold text-taxini-text-gray uppercase tracking-wider mb-2">Pickup Location</label>
            <div class="relative">
              <input 
                v-model="pickupLocation" 
                type="text" 
                placeholder="Current location" 
                class="input-field-dark pl-12"
              />
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 absolute left-4 top-1/2 -translate-y-1/2 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
          </div>

          <!-- Destination -->
          <div class="mb-6 relative destination-wrapper">
            <label class="block text-sm font-bold text-taxini-text-gray uppercase tracking-wider mb-2">Destination</label>
            
            <div class="relative">
              <input 
                v-model="destinationSearch" 
                type="text" 
                placeholder="Type to search location..." 
                class="input-field-dark pl-12"
                @input="handleDestinationSearch"
                @focus="destinationSuggestions = nearestPlaces; showDestinationSuggestions = nearestPlaces.length > 0"
                @blur="hideDestinationSuggestions"
              />
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 absolute left-4 top-1/2 -translate-y-1/2 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              
              <!-- Autocomplete Suggestions (Absolute Position Above) -->
              <div v-if="showDestinationSuggestions && destinationSuggestions.length > 0" class="destination-suggestions-dropdown">
                <button
                  v-for="(suggestion, index) in destinationSuggestions"
                  :key="index"
                  @mousedown.prevent="handleSelectDestination(suggestion)"
                  class="w-full px-4 py-3 text-left hover:bg-taxini-green/20 transition-colors border-b border-taxini-green/10 last:border-b-0"
                >
                  <p class="text-white font-medium">{{ suggestion.name }}</p>
                  <p class="text-taxini-text-gray text-sm">{{ suggestion.address }}</p>
                </button>
              </div>
            </div>
            
            <!-- Pick from Map Button -->
            <button 
              @click="handleEnableDestinationPicker"
              class="mt-2 w-full py-2 px-4 bg-taxini-yellow text-taxini-dark font-bold rounded-xl hover:bg-yellow-400 transition-all flex items-center justify-center gap-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Pick Destination on Map
            </button>
          </div>

          <!-- Find Driver Button -->
          <button 
            @click="handleFindDriver"
            :disabled="!destination"
            class="btn-primary w-full max-w-sm mx-auto disabled:opacity-50 font-bold py-3 text-base rounded-xl mb-5"
          >
            Find Driver
          </button>
        </div>

        <!-- Select Driver View -->
        <div v-if="tripState === 'select-driver'" class="px-6 pb-3" @click="handleClickOutsideDriverCard">
          <h2 class="text-2xl font-bold text-white mb-4">Available Drivers</h2>
          <p class="text-taxini-text-gray mb-6">Select a driver to request a ride</p>
          
          <!-- Driver Count Indicator -->
          <div v-if="nearbyDrivers.length > 0" class="mb-4 flex items-center justify-between px-4 py-2 bg-taxini-green/10 rounded-lg border border-taxini-green/30">
            <span class="text-taxini-text-gray text-sm">{{ nearbyDrivers.length }} driver{{ nearbyDrivers.length !== 1 ? 's' : '' }} available</span>
            <svg v-if="nearbyDrivers.length > 3" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-taxini-yellow animate-bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>
          
          <!-- No Drivers Found Message -->
          <div v-if="nearbyDrivers.length === 0" class="mb-4">
            <div class="bg-[#0d2621] rounded-xl p-6 border border-taxini-green/20 text-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-3 text-taxini-text-gray opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 class="text-base font-semibold text-white mb-1">No Drivers Available</h3>
              <p class="text-taxini-text-gray text-xs">No drivers nearby right now</p>
            </div>
          </div>
          
          <!-- Driver Cards with Dynamic Sizing -->
          <div 
            v-if="nearbyDrivers.length > 0"
            class="driver-cards-container space-y-3 mb-3"
            :class="{
              'single-driver': nearbyDrivers.length === 1,
              'two-drivers': nearbyDrivers.length === 2,
              'three-drivers': nearbyDrivers.length === 3,
              'many-drivers': nearbyDrivers.length > 3
            }"
          >
            <div 
              v-for="(driver, index) in nearbyDrivers" 
              :key="driver.id"
              @click.stop="selectDriverForBooking(driver)"
              @dblclick="handleSelectAndConfirmDriver(driver)"
              class="driver-card bg-[#0d2621] rounded-xl p-4 border border-taxini-green/20 hover:border-taxini-yellow/60 hover:shadow-lg hover:shadow-taxini-yellow/20 transition-all duration-300 cursor-pointer transform hover:scale-[1.02]"
              :class="{ 
                'border-taxini-yellow shadow-lg shadow-taxini-yellow/20': selectedDriver?.id === driver.id,
                'animate-slide-in': true
              }"
              :style="{ animationDelay: `${index * 100}ms` }"
            >
              <div class="flex items-center gap-4">
                <div class="w-16 h-16 rounded-full flex items-center justify-center flex-shrink-0 border border-taxini-green/30">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-taxini-yellow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <div class="flex-1">
                  <h3 class="text-lg font-bold text-white">{{ driver.name }}</h3>
                  <p class="text-taxini-text-gray text-sm">{{ driver.taxiNumber }}</p>
                  <div class="flex items-center gap-2 mt-1">
                    <div class="flex items-center">
                      <svg v-for="i in 5" :key="i" xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" :class="i <= driver.rating ? 'text-taxini-yellow' : 'text-gray-600'" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    </div>
                    <span class="text-taxini-text-gray text-xs">({{ driver.rating }})</span>
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-taxini-yellow font-bold text-lg">{{ driver.approachFee.toFixed(2) }} DT</div>
                  <div class="text-taxini-text-gray text-sm">~{{ driver.eta }} min</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex gap-3">
            <button @click="cancelDriverSelection" class="flex-1 bg-red-500/20 text-red-500 border-2 border-red-500 font-bold py-4 rounded-xl hover:bg-red-500/30 transition-all">
              Cancel
            </button>
            <button 
              @click="confirmDriverSelection" 
              :disabled="!selectedDriver || isCreatingTrip"
              class="flex-1 btn-primary font-bold py-4 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="!isCreatingTrip">Request Ride</span>
              <span v-else class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Requesting...
              </span>
            </button>
          </div>
        </div>

        <!-- Driver Confirmation View - REMOVED, goes straight to requested state -->
        <div v-if="false" class="px-6 pb-6 overflow-y-auto" style="max-height: 85vh;">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold text-white">Confirm Ride</h2>
            <div class="px-4 py-2 bg-blue-500/20 border border-blue-500 rounded-full">
              <span class="text-blue-500 font-bold text-sm">{{ tripStatus }}</span>
            </div>
          </div>
          
          <!-- Backend Status Indicator -->
          <div v-if="activeTrip" class="mb-4 px-4 py-2 bg-taxini-dark-light/50 rounded-lg border border-taxini-green/20">
            <p class="text-xs text-taxini-text-gray text-center">
              Backend: <span class="text-taxini-yellow font-mono">{{ activeTrip.status }}</span> | 
              Waiting for driver acceptance
            </p>
          </div>
          
          <div class="bg-[#0d2621] rounded-2xl p-8 mb-6 border border-taxini-green/20" style="min-height: 500px;">
            <!-- Driver Info -->
            <div class="flex items-center gap-4 mb-6">
              <div class="w-20 h-20 bg-taxini-green/20 rounded-full flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-taxini-yellow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div class="flex-1">
                <h3 class="text-xl font-bold text-white">{{ selectedDriver?.name }}</h3>
                <div class="flex items-center gap-2 mt-1">
                  <div class="flex items-center">
                    <svg v-for="i in 5" :key="i" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" :class="i <= selectedDriver?.rating ? 'text-taxini-yellow' : 'text-gray-600'" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  </div>
                  <span class="text-taxini-text-gray text-sm">({{ selectedDriver?.rating }})</span>
                </div>
              </div>
            </div>

            <!-- Trip Details -->
            <div class="space-y-5">
              <div class="flex items-center justify-between py-2">
                <span class="text-taxini-text-gray text-base">Taxi Number</span>
                <span class="text-white font-bold text-lg">{{ selectedDriver?.taxiNumber }}</span>
              </div>
              <div class="flex items-center justify-between py-2">
                <span class="text-taxini-text-gray text-base">Distance</span>
                <span class="text-white font-bold text-lg">{{ selectedDriver?.distance }} km</span>
              </div>
              <div class="flex items-center justify-between py-2">
                <span class="text-taxini-text-gray text-base">Pickup Time</span>
                <span class="text-white font-bold text-lg">~{{ selectedDriver?.eta }} min</span>
              </div>
              
              <!-- Cost Breakdown - Per Documentation -->
              <div class="border-t border-taxini-green/20 pt-5 mt-4 space-y-3">
                <!-- Approach Fee (FA) -->
                <div class="flex items-center justify-between">
                  <span class="text-taxini-text-gray text-sm">
                    Frais d'approche ({{ estimatedCost?.approachDistance?.toFixed(1) || selectedDriver?.distance?.toFixed(1) || '0' }} km)
                  </span>
                  <span class="text-white font-semibold">{{ (estimatedCost?.approachFee || selectedDriver?.approachFee || 0).toFixed(3) }} TND</span>
                </div>
                
                <!-- Trip Cost Estimate (CC_estimé) -->
                <div class="flex items-center justify-between">
                  <span class="text-taxini-text-gray text-sm">
                    Estimation course compteur ({{ estimatedCost?.tripDistance?.toFixed(1) || '0' }} km)
                  </span>
                  <span class="text-white font-semibold">~{{ (estimatedCost?.meterEstimate || 0).toFixed(3) }} TND</span>
                </div>
                
                <!-- Total Divider -->
                <div class="border-t border-taxini-yellow/30 pt-3">
                  <div class="flex items-center justify-between">
                    <span class="text-taxini-text-gray text-base font-medium">Total Estimé</span>
                    <span class="text-taxini-yellow font-bold text-2xl">~{{ (estimatedCost?.totalEstimate || selectedDriver?.approachFee || 0).toFixed(3) }} TND</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Optional Notes Section -->
          <div class="bg-[#0d2621] rounded-2xl p-4 mb-4 border border-taxini-green/20">
            <label class="block text-sm font-medium text-taxini-text-gray mb-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 inline mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
              </svg>
              Notes for Driver (Optional)
            </label>
            <textarea
              v-model="riderNotes"
              placeholder="e.g., Please call when you arrive, I'm at the back entrance..."
              class="w-full bg-taxini-dark border border-taxini-green/20 rounded-lg px-4 py-3 text-white placeholder-taxini-text-gray/50 focus:outline-none focus:border-taxini-yellow transition-colors resize-none"
              rows="3"
              maxlength="200"
            ></textarea>
            <div class="text-right text-xs text-taxini-text-gray mt-1">
              {{ riderNotes.length }}/200
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex gap-3">
            <button 
              @click="tripState = 'search'; riderNotes = ''" 
              :disabled="isCreatingTrip"
              class="flex-1 bg-red-500/20 text-red-500 border-2 border-red-500 font-bold py-4 rounded-2xl hover:bg-red-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button 
              @click="confirmDriverSelection" 
              :disabled="isCreatingTrip"
              class="flex-1 btn-primary font-bold py-4 rounded-2xl hover:bg-yellow-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="!isCreatingTrip">Request Ride</span>
              <span v-else class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Creating Trip...
              </span>
            </button>
          </div>
        </div>

        <!-- Trip Requested View -->
        <!-- Waiting for Driver Acceptance View -->
        <div v-if="tripState === 'requested'" class="flex flex-col h-full">
            <!-- Header -->
            <div class="text-center px-6 pt-6 pb-6 flex-shrink-0">
              <div class="w-20 h-20 mx-auto bg-taxini-yellow/20 rounded-full flex items-center justify-center mb-4">
                <svg class="animate-spin h-10 w-10 text-taxini-yellow" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
              <h2 class="text-xl font-bold text-white mb-2">Searching for Driver...</h2>
              <p class="text-taxini-text-gray text-sm">Your trip request is being sent to nearby drivers</p>
            </div>

            <!-- Waiting Message Card -->
            <div class="bg-[#0d2621] rounded-2xl mx-6 mb-4 p-6 border border-taxini-green/20">
              <!-- Animated dots -->
              <div class="flex justify-center items-center gap-2 mb-4">
                <div class="w-3 h-3 bg-taxini-yellow rounded-full animate-bounce" style="animation-delay: 0s"></div>
                <div class="w-3 h-3 bg-taxini-yellow rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                <div class="w-3 h-3 bg-taxini-yellow rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
              </div>
              
              <!-- Trip Info -->
              <div class="space-y-3 text-center">
                <div class="text-white">
                  <div class="text-sm text-taxini-text-gray mb-1">From</div>
                  <div class="font-semibold text-base">{{ formattedPickupAddress || 'Loading...' }}</div>
                </div>
                
                <div class="flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-taxini-yellow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                </div>
                
                <div class="text-white">
                  <div class="text-sm text-taxini-text-gray mb-1">To</div>
                  <div class="font-semibold text-base">{{ formattedDestinationAddress || 'Loading...' }}</div>
                </div>
                
                <div class="border-t border-taxini-green/20 pt-3 mt-3">
                  <div class="flex items-center justify-between">
                    <span class="text-taxini-text-gray text-sm">Estimated Cost</span>
                    <span class="text-taxini-yellow font-bold text-lg">{{ activeTrip?.estimated_cost_tnd || '0.00' }} TND</span>
                  </div>
                </div>
              </div>
              
              <!-- Status Message -->
              <div class="mt-4 px-4 py-3 bg-blue-500/10 rounded-lg border border-blue-500/30">
                <p class="text-sm text-blue-400 text-center">
                  Notifying nearby drivers of your request...
                </p>
              </div>
            </div>

          <!-- Cancel Button - Always visible at bottom -->
          <div class="px-6 pb-4 pt-2 flex-shrink-0">
            <button @click="handleCancelTrip" class="w-full bg-red-500/20 text-red-500 border-2 border-red-500 font-semibold py-3 rounded-xl hover:bg-red-500/30 transition-all text-sm">
              Cancel Trip Request
            </button>
          </div>
        </div>

        <!-- Driver Approaching View - Driver accepted, rider needs to confirm pickup -->
        <div v-if="tripState === 'driver-approaching'" class="px-6 pb-4">
          <!-- Important Notice -->
          <div class="mb-4 bg-taxini-yellow/10 border border-taxini-yellow rounded-xl p-4">
            <div class="flex items-start gap-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-taxini-yellow flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 class="text-taxini-yellow font-bold mb-1">Driver is on the way!</h3>
                <p class="text-white text-sm">When your driver arrives, please confirm below so the trip can begin.</p>
              </div>
            </div>
          </div>

          <!-- Driver Card -->
          <div class="bg-[#0d2621] rounded-xl p-4 mb-4 border border-taxini-green/20">
            <div class="flex items-center gap-4">
              <div class="w-16 h-16 rounded-full flex items-center justify-center border border-taxini-green/30">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-taxini-yellow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div class="flex-1">
                <h3 class="text-lg font-bold text-white">{{ activeTrip?.driver?.name || selectedDriver?.name || 'Driver' }}</h3>
                <p class="text-taxini-text-gray text-sm">{{ activeTrip?.driver?.taxi_number || selectedDriver?.taxiNumber || 'TU-123-456' }}</p>
              </div>
              <button 
                v-if="activeTrip?.driver?.phone_number"
                @click="window.open(`tel:${activeTrip.driver.phone_number}`)" 
                class="bg-taxini-yellow text-taxini-dark p-3 rounded-full hover:bg-yellow-400 transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Trip Route -->
          <div class="bg-[#0d2621] rounded-xl p-4 mb-4 border border-taxini-green/20">
            <div class="space-y-3">
              <div class="flex items-start gap-3">
                <div class="w-3 h-3 bg-green-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <div class="flex-1 min-w-0">
                  <p class="text-taxini-text-gray text-xs uppercase tracking-wide mb-1">Pickup</p>
                  <p class="text-white text-sm leading-snug">{{ formattedPickupAddress || 'Loading...' }}</p>
                </div>
              </div>
              <div class="ml-1.5 border-l-2 border-dashed border-taxini-green/30 h-6"></div>
              <div class="flex items-start gap-3">
                <div class="w-3 h-3 bg-red-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <div class="flex-1 min-w-0">
                  <p class="text-taxini-text-gray text-xs uppercase tracking-wide mb-1">Destination</p>
                  <p class="text-white text-sm leading-snug">{{ formattedDestinationAddress || 'Loading...' }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Estimated Cost -->
          <div class="bg-taxini-yellow/10 border border-taxini-yellow/30 rounded-xl p-4 mb-4">
            <div class="flex items-center justify-between">
              <span class="text-white font-medium">Estimated Cost</span>
              <span class="text-taxini-yellow font-bold text-xl">{{ activeTrip?.estimated_cost_tnd?.toFixed(2) || '0.00' }} TND</span>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="space-y-3">
            <button 
              @click="handleConfirmPickup" 
              class="w-full bg-taxini-green text-white font-bold py-4 rounded-xl hover:bg-taxini-green/90 transition-all shadow-lg flex items-center justify-center gap-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              Confirm Driver Arrived
            </button>

            <button 
              @click="handleCancelTrip" 
              class="w-full bg-red-500/20 text-red-500 border-2 border-red-500 font-bold py-3 rounded-xl hover:bg-red-500/30 transition-all"
            >
              Cancel Trip
            </button>
          </div>
        </div>

        <!-- Active Trip View -->
        <div v-if="tripState === 'active'" class="px-6 pb-6 overflow-y-auto" style="max-height: 85vh;">
          <!-- Backend Status Indicator -->
          <div v-if="activeTrip && showTripDetails" class="mb-4 px-4 py-2 bg-taxini-dark-light/50 rounded-lg border border-taxini-green/20">
            <p class="text-xs text-taxini-text-gray text-center">
              Backend: <span class="text-taxini-yellow font-mono">{{ activeTrip.status }}</span>
              <span v-if="activeTrip.started_at" class="ml-2">
                | Started: {{ new Date(activeTrip.started_at).toLocaleTimeString() }}
              </span>
            </p>
          </div>

          <!-- Trip Details Section (can be toggled) -->
          <div v-if="showTripDetails">
            <!-- Driver Card -->
            <div class="bg-[#0d2621] rounded-2xl p-4 mb-4 border border-taxini-green/20">
            <div class="flex items-center gap-4">
              <div class="w-16 h-16 bg-taxini-green/20 rounded-full flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-taxini-yellow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div class="flex-1">
                <h3 class="text-lg font-bold text-white">{{ activeTrip?.driver?.name || selectedDriver?.name || 'Driver' }}</h3>
                <p class="text-taxini-text-gray text-sm">{{ activeTrip?.driver?.taxi_number || selectedDriver?.taxiNumber || 'TU-123-456' }}</p>
                <div v-if="activeTrip?.driver?.phone_number" class="flex items-center gap-1 mt-1">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-taxini-text-gray" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  <span class="text-taxini-text-gray text-xs">{{ activeTrip.driver.phone_number }}</span>
                </div>
              </div>
              <button @click="activeTrip?.driver?.phone_number && window.open(`tel:${activeTrip.driver.phone_number}`)" class="bg-taxini-yellow text-taxini-dark p-3 rounded-full hover:bg-yellow-400 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Trip Route -->
          <div class="bg-[#0d2621] rounded-2xl p-4 mb-4 border border-taxini-green/20">
            <div class="space-y-4">
              <div class="flex items-start gap-3">
                <div class="w-3 h-3 bg-green-500 rounded-full mt-2"></div>
                <div class="flex-1">
                  <p class="text-taxini-text-gray text-sm">Pickup</p>
                  <p class="text-white font-medium">{{ formattedPickupAddress || 'Loading...' }}</p>
                </div>
              </div>
              <div class="ml-1.5 border-l-2 border-dashed border-taxini-green/30 h-8"></div>
              <div class="flex items-start gap-3">
                <div class="w-3 h-3 bg-red-500 rounded-full mt-2"></div>
                <div class="flex-1">
                  <p class="text-taxini-text-gray text-sm">Destination</p>
                  <p class="text-white font-medium">{{ formattedDestinationAddress || 'Loading...' }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Distance -->
          <div class="bg-[#0d2621] rounded-2xl p-4 mb-4 border border-taxini-green/20">
            <div class="flex items-center justify-between">
              <span class="text-taxini-text-gray">Distance</span>
              <span class="text-white font-bold text-xl">{{ activeTrip?.estimated_distance_km?.toFixed(2) || '0.00' }} km</span>
            </div>
          </div>

          <!-- Cost Breakdown - From Backend -->
          <div class="bg-taxini-yellow/10 border border-taxini-yellow/30 rounded-2xl p-4 mb-6">
            <!-- If backend provides cost breakdown -->
            <div v-if="activeTrip?.approach_fee_tnd !== null && activeTrip?.approach_fee_tnd !== undefined" class="space-y-2">
              <div class="text-white font-medium text-sm mb-3">Estimation de votre course :</div>
              
              <!-- Frais d'approche -->
              <div class="flex items-center justify-between">
                <span class="text-taxini-text-gray text-sm">
                  Frais d'approche ({{ activeTrip.approach_distance_km?.toFixed(1) || '0' }} km)
                </span>
                <span class="text-white font-semibold">{{ activeTrip.approach_fee_tnd?.toFixed(3) || '0.000' }} TND</span>
              </div>
              
              <!-- Estimation course compteur -->
              <div class="flex items-center justify-between">
                <span class="text-taxini-text-gray text-sm">
                  Estimation course (compteur)
                </span>
                <span class="text-white font-semibold">~{{ activeTrip.estimated_cost_tnd?.toFixed(3) || '0.000' }} TND</span>
              </div>
              
              <!-- Total divider -->
              <div class="border-t border-taxini-yellow/30 pt-2 mt-2">
                <div class="flex items-center justify-between">
                  <span class="text-white font-medium">Total Estimé à payer</span>
                  <span class="text-taxini-yellow font-bold text-2xl">
                    ~{{ ((activeTrip.approach_fee_tnd || 0) + (activeTrip.estimated_cost_tnd || 0)).toFixed(3) }} TND
                  </span>
                </div>
              </div>
            </div>
            
            <!-- Fallback if no breakdown available -->
            <div v-else class="flex items-center justify-between">
              <span class="text-white font-medium">Estimated Cost</span>
              <span class="text-taxini-yellow font-bold text-2xl">{{ activeTrip?.estimated_cost_tnd?.toFixed(2) || estimatedCost?.totalEstimate?.toFixed(2) || '0.00' }} TND</span>
            </div>
          </div>
          </div>

          <!-- Cancel Button (only if not started) -->
          <button v-if="tripStatus !== 'Started'" @click="handleCancelTrip" class="w-full bg-red-500/20 text-red-500 border-2 border-red-500 font-bold py-4 rounded-2xl hover:bg-red-500/30 transition-all">
            Cancel Trip
          </button>
        </div>

        <!-- Trip Completed View -->
        <div v-if="tripState === 'completed'" class="px-6 pb-6 overflow-y-auto" style="max-height: 580px;">
          <div class="text-center mb-6">
            <div class="w-24 h-24 mx-auto bg-green-500/20 rounded-full flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-white mb-2">Trip Completed!</h2>
            <p class="text-taxini-text-gray">Thank you for riding with Taxini</p>
          </div>

          <!-- Trip Summary -->
          <div class="bg-[#0d2621] rounded-2xl p-6 mb-6 border border-taxini-green/20">
            <h3 class="text-lg font-bold text-white mb-4">Trip Summary</h3>
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-taxini-text-gray">Distance</span>
                <span class="text-white font-bold">{{ tripSummary.distance }} km</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-taxini-text-gray">Duration</span>
                <span class="text-white font-bold">{{ tripSummary.duration }} min</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-taxini-text-gray">Base Fare</span>
                <span class="text-white">{{ tripSummary.baseFare }} TND</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-taxini-text-gray">Distance Fee</span>
                <span class="text-white">{{ tripSummary.distanceFee }} TND</span>
              </div>
              <div class="flex items-center justify-between border-t border-taxini-green/20 pt-3">
                <span class="text-white font-bold text-lg">Total Cost</span>
                <span class="text-taxini-yellow font-bold text-2xl">{{ tripSummary.totalCost }} TND</span>
              </div>
            </div>
          </div>

          <!-- Rating -->
          <div class="bg-[#0d2621] rounded-2xl p-6 mb-6 border border-taxini-green/20">
            <h3 class="text-lg font-bold text-white mb-4 text-center">Rate Your Driver</h3>
            <div class="flex justify-center gap-2 mb-4">
              <button
                v-for="star in 5"
                :key="star"
                @click="rating = star"
                class="transition-all"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" :class="star <= rating ? 'text-taxini-yellow' : 'text-gray-600'" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </button>
            </div>
            <textarea
              v-model="review"
              placeholder="Share your experience (optional)"
              class="input-field-dark resize-none h-24"
            ></textarea>
          </div>

          <button 
            @click="handleCompleteTripRating" 
            :disabled="isSubmittingRating"
            class="btn-primary w-full font-bold py-5 text-xl rounded-2xl disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <span v-if="!isSubmittingRating">Done</span>
            <span v-else class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Submitting...
            </span>
          </button>
        </div>
      </div>
      </transition>
    </div>

    <!-- Cancel Trip Confirmation Modal -->
    <transition name="fade">
      <div v-if="showCancelModal" class="fixed inset-0 z-50 flex items-center justify-center px-4">
        <div @click="showCancelModal = false" class="absolute inset-0 bg-black/70"></div>
        <div class="relative bg-taxini-dark-light rounded-2xl p-6 w-full max-w-md border border-taxini-green/20 shadow-2xl" @click.stop>
          <h3 class="text-xl font-bold text-white mb-4">Cancel Trip?</h3>
          <p class="text-taxini-text-gray mb-4">Are you sure you want to cancel this trip? The driver may have already started heading your way.</p>
          
          <!-- Cancel Reason (Optional) -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-taxini-text-gray mb-2">
              Reason (Optional)
            </label>
            <select
              v-model="cancelReason"
              class="w-full bg-taxini-dark border border-taxini-green/20 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-taxini-yellow transition-colors"
            >
              <option value="">Select a reason...</option>
              <option value="changed_plans">Changed my plans</option>
              <option value="found_alternative">Found alternative transport</option>
              <option value="too_long">Taking too long</option>
              <option value="wrong_location">Wrong pickup location</option>
              <option value="other">Other</option>
            </select>
          </div>
          
          <!-- Action Buttons -->
          <div class="flex gap-3">
            <button
              @click="showCancelModal = false"
              :disabled="isCancelling"
              class="flex-1 bg-taxini-dark border-2 border-taxini-green/20 text-white font-bold py-3 rounded-xl hover:border-taxini-green/40 transition-all disabled:opacity-50"
            >
              Keep Trip
            </button>
            <button
              @click="confirmCancelTrip"
              :disabled="isCancelling"
              class="flex-1 bg-red-500 text-white font-bold py-3 rounded-xl hover:bg-red-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="!isCancelling">Yes, Cancel</span>
              <span v-else class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Cancelling...
              </span>
            </button>
          </div>
        </div>
      </div>
    </transition>



    <!-- Side Menu -->
    <transition name="slide-fade">
      <div v-if="showSideMenu" class="fixed inset-0 z-50">
        <div @click="showSideMenu = false" class="absolute inset-0 bg-black/70"></div>
        <div class="absolute left-0 top-0 bottom-0 w-80 bg-taxini-dark-light shadow-2xl">
          <!-- Profile Header -->
          <div class="p-6 border-b border-taxini-green/20">
            <div class="flex items-center gap-4 mb-4">
              <div class="w-20 h-20 bg-taxini-green/20 rounded-full flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-taxini-yellow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div>
                <h3 class="text-xl font-bold text-white">{{ user?.name }}</h3>
                <p class="text-taxini-text-gray text-sm">{{ user?.phone }}</p>
              </div>
            </div>
            <button @click="navigateTo('/rider/profile')" class="w-full bg-taxini-yellow text-taxini-dark font-bold py-3 rounded-xl hover:bg-taxini-yellow-dark transition-all">
              Edit Profile
            </button>
          </div>

          <!-- Menu Items -->
          <div class="p-6 space-y-2">
            <button @click="navigateTo('/rider/profile')" class="w-full flex items-center gap-4 px-4 py-3 text-white hover:bg-taxini-green/20 rounded-xl transition-all">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <span class="font-medium">My Profile</span>
            </button>
            <button @click="navigateTo('/rider/history')" class="w-full flex items-center gap-4 px-4 py-3 text-white hover:bg-taxini-green/20 rounded-xl transition-all">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="font-medium">Trip History</span>
            </button>
            <button @click="navigateTo('/rider/support')" class="w-full flex items-center gap-4 px-4 py-3 text-white hover:bg-taxini-green/20 rounded-xl transition-all">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              <span class="font-medium">Support</span>
            </button>
            <button v-if="user?.hasDriverProfile" @click="switchToDriver" class="w-full flex items-center gap-4 px-4 py-3 text-taxini-yellow hover:bg-taxini-green/20 rounded-xl transition-all">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              </svg>
              <span class="font-medium">Switch to Driver</span>
            </button>
          </div>

          <!-- Logout -->
          <div class="absolute bottom-0 left-0 right-0 p-6 border-t border-taxini-green/20">
            <button @click="logout" class="w-full flex items-center gap-4 px-4 py-3 text-red-500 hover:bg-red-500/10 rounded-xl transition-all">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span class="font-medium">Logout</span>
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Trip Completion Confirmation Modal -->
    <transition name="fade">
      <div v-if="showCompletionModal" class="fixed inset-0 z-50 flex items-center justify-center px-4">
        <div @click.self class="absolute inset-0 bg-black/80"></div>
        <div class="relative bg-taxini-dark-light rounded-2xl p-6 w-full max-w-md border border-taxini-green/30 shadow-2xl" @click.stop>
          <!-- Success Icon -->
          <div class="flex justify-center mb-4">
            <div class="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>

          <h3 class="text-2xl font-bold text-white text-center mb-2">Trip Completed!</h3>
          <p class="text-taxini-text-gray text-center mb-6">
            Your driver has marked the trip as completed. Please confirm to proceed to rating.
          </p>

          <!-- Trip Summary -->
          <div v-if="activeTrip" class="bg-taxini-dark rounded-xl p-4 mb-6 border border-taxini-green/20">
            <div class="flex items-center justify-between mb-2">
              <span class="text-taxini-text-gray text-sm">Distance</span>
              <span class="text-white font-bold">{{ activeTrip.estimated_distance_km?.toFixed(2) || '0.00' }} km</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-taxini-text-gray text-sm">Total Cost</span>
              <span class="text-taxini-yellow font-bold text-xl">{{ activeTrip.total_cost_tnd?.toFixed(2) || activeTrip.estimated_cost_tnd?.toFixed(2) || '0.00' }} TND</span>
            </div>
          </div>
          
          <!-- Action Button -->
          <button
            @click="handleConfirmCompletion"
            :disabled="isConfirmingCompletion"
            class="w-full bg-taxini-green text-white font-bold py-4 rounded-xl hover:bg-taxini-green-dark transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
          >
            <span v-if="!isConfirmingCompletion" class="flex items-center justify-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              Confirm & Rate Driver
            </span>
            <span v-else class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Confirming...
            </span>
          </button>
        </div>
      </div>
    </transition>

    <!-- Toast Notification -->
    <transition name="toast-slide">
      <div v-if="showToast" class="toast-notification" :class="`toast-${toastType}`">
        <div class="toast-icon">
          <svg v-if="toastType === 'error'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg v-if="toastType === 'warning'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <svg v-if="toastType === 'success'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg v-if="toastType === 'info'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <span class="toast-message">{{ toastMessage }}</span>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import riderNotificationService from '@/services/riderNotificationService'
import { useNotificationStore } from '@/services/notificationStore'

// Composables
import { useMap } from '@/composables/rider/useMap'
import { useTripManagement } from '@/composables/rider/useTripManagement'
import { useDestinationPicker } from '@/composables/rider/useDestinationPicker'
import { useUIState } from '@/composables/rider/useUIState'

const router = useRouter()
const authStore = useAuthStore()

// Use composables
const {
  mapContainer,
  map,
  userLocation,
  initMap,
  getCurrentLocation,
  centerOnUserLocation,
  setDestinationMarker,
  removeDestinationMarker,
  drawRoute,
  clearRoute,
  reverseGeocode
} = useMap()

// Import location formatter service
import { formatTripLocation, formatCurrentLocation, formatLocation } from '@/services/locationFormatter'

const {
  destination,
  isPickingDestination,
  tempDestinationCoords,
  showDestinationConfirmation,
  showDestinationSuggestions,
  destinationSuggestions,
  enableDestinationPicker,
  onMapClickForDestination,
  confirmDestination,
  cancelDestination,
  selectDestination
} = useDestinationPicker()

// Initialize trip management with location refs
const {
  tripState,
  tripStatus,
  selectedDriver,
  estimatedCost,
  rating,
  review,
  activeTrip,
  nearbyDrivers,
  loadingDrivers,
  driversError,
  tripSummary,
  fetchNearbyDrivers,
  checkActiveTrip,
  mapBackendStatusToFrontendState,
  mapBackendStatusToDisplayText,
  refreshTripStatus,
  selectDriverForTrip,
  selectDriverForBooking,
  selectAndConfirmDriver,
  findDriver,
  cancelDriverSelection,
  requestRide,
  confirmPickup,
  cancelTrip,
  confirmCompletion,
  completeTripRating
} = useTripManagement(userLocation, destination)

const {
  showSideMenu,
  showBottomSheet,
  handleMapClick,
  handleBottomSheetTouchStart,
  handleBottomSheetTouchMove,
  handleBottomSheetTouchEnd,
  toggleBottomSheet
} = useUIState()

// Local state
const pickupLocation = ref('Loading location...')
const destinationSearch = ref('')
const riderNotes = ref('') // Optional notes for driver
const isCreatingTrip = ref(false) // Loading state for trip creation
const nearestPlaces = ref([]) // Dynamically fetched nearest places

// Cancel trip modal state
const showCancelModal = ref(false)
const cancelReason = ref('')
const isCancelling = ref(false)

// Rating state (rating and review come from useTripManagement composable)
const isSubmittingRating = ref(false)

// Completion confirmation modal state
const showCompletionModal = ref(false)
const isConfirmingCompletion = ref(false)

// Navigation card state
const showTripDetails = ref(false) // Hide details by default - show compact card at bottom
const tripDuration = ref(0) // in seconds
const tripDistance = ref(0) // in km
let tripTimer = null
let distanceTracker = null

// Toast notification state
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('error') // 'error', 'success', 'warning', 'info'

// Driver cards are now handled with simple CSS - no complex computed properties needed

// Handle clicking outside driver cards to deselect
const handleClickOutsideDriverCard = (event) => {
  // Only deselect if clicking on the background, not on cards or buttons
  if (event.target === event.currentTarget || 
      event.target.classList.contains('px-6') ||
      !event.target.closest('.driver-card') && !event.target.closest('button')) {
    selectedDriver.value = null
  }
}

// Format addresses for display
const formattedPickupAddress = ref('Loading location...')
const formattedDestinationAddress = ref('Loading location...')
const isGeocodingPickup = ref(false)
const isGeocodingDestination = ref(false)

// Function to update formatted addresses using locationFormatter service
const updateFormattedAddresses = async () => {
  console.log('🔄 Updating formatted addresses with locationFormatter...')
  console.log('ActiveTrip:', activeTrip.value)
  console.log('UserLocation:', userLocation.value)
  console.log('TempDestination:', tempDestinationCoords.value)
  
  try {
    if (activeTrip.value) {
      // PICKUP: Format using service
      isGeocodingPickup.value = true
      formattedPickupAddress.value = 'Getting location...'
      
      const pickupAddress = await formatTripLocation(activeTrip.value, 'pickup')
      formattedPickupAddress.value = pickupAddress
      isGeocodingPickup.value = false
      console.log('✅ Pickup formatted:', pickupAddress)
      
      // DESTINATION: Format using service
      isGeocodingDestination.value = true
      formattedDestinationAddress.value = 'Getting location...'
      
      const destinationAddress = await formatTripLocation(activeTrip.value, 'destination')
      formattedDestinationAddress.value = destinationAddress
      isGeocodingDestination.value = false
      console.log('✅ Destination formatted:', destinationAddress)
    } else {
      // No active trip yet - use current location and temp destination
      if (userLocation.value?.lat && userLocation.value?.lng) {
        isGeocodingPickup.value = true
        formattedPickupAddress.value = 'Getting location...'
        const pickupAddress = await formatCurrentLocation(userLocation.value)
        formattedPickupAddress.value = pickupAddress
        isGeocodingPickup.value = false
        console.log('✅ Pickup formatted from userLocation:', pickupAddress)
      } else {
        formattedPickupAddress.value = pickupLocation.value || 'Current Location'
      }
      
      if (tempDestinationCoords.value?.lat && tempDestinationCoords.value?.lng) {
        isGeocodingDestination.value = true
        formattedDestinationAddress.value = 'Getting location...'
        const destAddress = await formatLocation(tempDestinationCoords.value.lng, tempDestinationCoords.value.lat)
        formattedDestinationAddress.value = destAddress
        isGeocodingDestination.value = false
        console.log('✅ Destination formatted from tempCoords:', destAddress)
      } else {
        formattedDestinationAddress.value = destination.value || 'Select destination'
      }
      
      console.log('ℹ️ Using local coordinates for formatting')
    }
    
    console.log('📍 Final addresses:', {
      pickup: formattedPickupAddress.value,
      destination: formattedDestinationAddress.value
    })
  } catch (error) {
    console.error('❌ Error formatting addresses:', error)
    isGeocodingPickup.value = false
    isGeocodingDestination.value = false
    formattedPickupAddress.value = 'Pickup location'
    formattedDestinationAddress.value = 'Destination'
  }
}

// Watch for changes and update addresses
watch([activeTrip, pickupLocation, destination], async () => {
  await updateFormattedAddresses()
}, { deep: true, immediate: true })

// Dynamic trip info card sizing
const tripInfoCardStyle = computed(() => {
  // Adjust based on trip state and content visibility
  const baseHeight = 400
  let additionalHeight = 0
  
  if (tripState.value === 'accepted') additionalHeight += 200
  if (tripState.value === 'started') additionalHeight += 150
  if (currentTrip.value?.approach_fee_tnd) additionalHeight += 60
  
  return {
    maxHeight: `${baseHeight + additionalHeight}px`,
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
  }
})

// Show toast function
const displayToast = (message, type = 'error', options = {}) => {
  if (typeof window !== 'undefined' && window.$notification) {
    // Use new notification system
    window.$notification.toast(message, type, options)
  } else {
    // Fallback to old system
    toastMessage.value = message
    toastType.value = type
    showToast.value = true
    
    setTimeout(() => {
      showToast.value = false
    }, 3000)
  }
}

// Make displayToast available globally for composables
if (typeof window !== 'undefined') {
  window.displayToast = displayToast
  
  // Add refreshDriverList callback for when trip is cancelled
  window.refreshDriverList = async () => {
    if (userLocation.value && userLocation.value.lat && userLocation.value.lng) {
      console.log('🔄 Refreshing driver list after trip cancellation')
      await fetchNearbyDrivers(userLocation.value.lat, userLocation.value.lng)
      // Update hash to ensure UI reflects the refresh
      lastDriverListHash = createDriverListHash(nearbyDrivers.value)
    }
  }
}

// Fetch nearest known places based on current location
const fetchNearestPlaces = async () => {
  if (!userLocation.value || !userLocation.value.lng || !userLocation.value.lat) {
    console.log('⚠️ No user location available for fetching nearest places')
    return
  }
  
  try {
    const mapboxToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN
    const lng = userLocation.value.lng
    const lat = userLocation.value.lat
    
    // Mapbox reverse geocoding: Remove limit to avoid 422 errors with type restrictions
    const url = `https://api.mapbox.com/geocoding/v5/mapbox.places/${lng},${lat}.json?access_token=${mapboxToken}`
    
    console.log('📍 Fetching nearest places from current location...')
    const response = await fetch(url)
    const data = await response.json()
    
    if (data.features && data.features.length > 0) {
      nearestPlaces.value = data.features.map(feature => ({
        name: feature.text,
        address: feature.place_name,
        coords: {
          lng: feature.geometry.coordinates[0],
          lat: feature.geometry.coordinates[1]
        }
      }))
      console.log(`✅ Found ${nearestPlaces.value.length} nearest places:`, nearestPlaces.value)
    } else {
      console.log('⚠️ No nearest places found')
      nearestPlaces.value = []
    }
  } catch (error) {
    console.error('❌ Error fetching nearest places:', error)
    nearestPlaces.value = []
  }
}

// Search timeout for debouncing
let searchTimeout = null

// Handle destination search input using multiple geocoding sources
const handleDestinationSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  
  searchTimeout = setTimeout(async () => {
    console.log('🔍 Search triggered for:', destinationSearch.value)
    
    // Show nearest places when input is empty or too short
    if (destinationSearch.value.length < 2) {
      destinationSuggestions.value = nearestPlaces.value
      showDestinationSuggestions.value = nearestPlaces.value.length > 0
      console.log('📍 Showing nearest places')
      return
    }
    
    try {
      const query = encodeURIComponent(destinationSearch.value)
      let allResults = []
      
      // Strategy 1: OpenStreetMap Nominatim (best for Tunisia POIs)
      try {
        let nominatimUrl = `https://nominatim.openstreetmap.org/search?`
        nominatimUrl += `q=${query}&`
        nominatimUrl += `countrycodes=tn&`
        nominatimUrl += `format=json&`
        nominatimUrl += `limit=10&`
        nominatimUrl += `addressdetails=1&`
        
        // Add viewbox for proximity if user location available
        if (userLocation.value && userLocation.value.lng && userLocation.value.lat) {
          const lat = userLocation.value.lat
          const lng = userLocation.value.lng
          // Create a 0.5 degree box around user location (roughly 55km)
          nominatimUrl += `viewbox=${lng-0.5},${lat+0.5},${lng+0.5},${lat-0.5}&`
          nominatimUrl += `bounded=1&`
        }
        
        console.log('📡 Calling OpenStreetMap Nominatim...')
        const nominatimResponse = await fetch(nominatimUrl, {
          headers: {
            'User-Agent': 'Taxini-App/1.0' // Nominatim requires User-Agent
          }
        })
        const nominatimData = await nominatimResponse.json()
        
        if (nominatimData && nominatimData.length > 0) {
          const nominatimResults = nominatimData.map(item => ({
            name: item.name || item.display_name.split(',')[0],
            address: item.display_name,
            coords: {
              lng: parseFloat(item.lon),
              lat: parseFloat(item.lat)
            }
          }))
          allResults = [...nominatimResults]
          console.log(`✅ OSM Nominatim returned ${nominatimResults.length} results`)
        }
      } catch (error) {
        console.warn('⚠️ Nominatim search failed:', error)
      }
      
      // Strategy 2: Mapbox as fallback (for streets/places it knows better)
      try {
        const mapboxToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN
        let mapboxUrl = `https://api.mapbox.com/geocoding/v5/mapbox.places/${query}.json?`
        mapboxUrl += `country=tn&`
        mapboxUrl += `types=poi,address,place,locality&`
        mapboxUrl += `limit=5&`
        
        if (userLocation.value && userLocation.value.lng && userLocation.value.lat) {
          mapboxUrl += `proximity=${userLocation.value.lng},${userLocation.value.lat}&`
        }
        
        mapboxUrl += `access_token=${mapboxToken}`
        
        console.log('📡 Calling Mapbox as fallback...')
        const mapboxResponse = await fetch(mapboxUrl)
        const mapboxData = await mapboxResponse.json()
        
        if (mapboxData.features && mapboxData.features.length > 0) {
          const mapboxResults = mapboxData.features.map(feature => ({
            name: feature.text,
            address: feature.place_name,
            coords: {
              lng: feature.geometry.coordinates[0],
              lat: feature.geometry.coordinates[1]
            }
          }))
          
          // Add Mapbox results, avoiding duplicates
          mapboxResults.forEach(result => {
            const isDuplicate = allResults.some(existing => 
              existing.name.toLowerCase() === result.name.toLowerCase() ||
              (Math.abs(existing.coords.lat - result.coords.lat) < 0.001 &&
               Math.abs(existing.coords.lng - result.coords.lng) < 0.001)
            )
            if (!isDuplicate) {
              allResults.push(result)
            }
          })
          console.log(`✅ Mapbox added ${mapboxResults.length} results`)
        }
      } catch (error) {
        console.warn('⚠️ Mapbox search failed:', error)
      }
      
      console.log('📦 Total combined results:', allResults.length)
      let mapboxResults = allResults
      
      // Search in nearest places
      const searchLower = destinationSearch.value.toLowerCase()
      const nearestMatches = nearestPlaces.value.filter(location =>
        location.name.toLowerCase().includes(searchLower) ||
        location.address.toLowerCase().includes(searchLower)
      )
      
      // Combine results: Mapbox first, then nearest places (avoiding duplicates)
      const combinedResults = [...mapboxResults]
      
      // Add nearest matches
      nearestMatches.forEach(nearest => {
        const isDuplicate = combinedResults.some(result => 
          result.name.toLowerCase() === nearest.name.toLowerCase()
        )
        if (!isDuplicate) {
          combinedResults.push(nearest)
        }
      })
      
      destinationSuggestions.value = combinedResults.slice(0, 10)
      showDestinationSuggestions.value = combinedResults.length > 0
      
      console.log(`✅ Total results: ${destinationSuggestions.value.length}`, destinationSuggestions.value)
    } catch (error) {
      console.error('❌ Error fetching locations from Mapbox:', error)
      // Fallback to nearest places only
      const searchLower = destinationSearch.value.toLowerCase()
      
      destinationSuggestions.value = nearestPlaces.value.filter(location =>
        location.name.toLowerCase().includes(searchLower) ||
        location.address.toLowerCase().includes(searchLower)
      )
      showDestinationSuggestions.value = destinationSuggestions.value.length > 0
    }
  }, 300)
}

// Hide suggestions with delay to allow click
const hideDestinationSuggestions = () => {
  setTimeout(() => {
    showDestinationSuggestions.value = false
  }, 200)
}

// Handle cancel trip - shows confirmation modal
const handleCancelTrip = () => {
  showCancelModal.value = true
  cancelReason.value = '' // Reset reason
}

// Handle confirm pickup - rider confirms driver has arrived
const handleConfirmPickup = async () => {
  try {
    displayToast('Confirming pickup...', 'info')
    const response = await confirmPickup()
    
    if (response.success) {
      displayToast('Pickup confirmed! Driver can now start the trip.', 'success')
      // Refresh trip status to get updated state
      await refreshTripStatus()
    }
  } catch (error) {
    console.error('Failed to confirm pickup:', error)
    displayToast(error.message || 'Failed to confirm pickup. Please try again.', 'error')
  }
}

// Confirm cancel trip - executes cancellation
const confirmCancelTrip = async () => {
  isCancelling.value = true
  
  try {
    const result = await cancelTrip(cancelReason.value || null)
    
    if (result.success) {
      showCancelModal.value = false
      cancelReason.value = ''
      window.$notification?.success('Trip cancelled successfully', { title: 'Trip Cancelled' })
    } else {
      window.$notification?.error(result.error || 'Failed to cancel trip', { title: 'Cancellation Failed' })
    }
  } catch (error) {
    console.error('Error cancelling trip:', error)
    displayToast('Failed to cancel trip. Please try again.', 'error')
  } finally {
    isCancelling.value = false
  }
}

// Handle confirm completion
const handleConfirmCompletion = async () => {
  isConfirmingCompletion.value = true
  
  try {
    const result = await confirmCompletion()
    
    if (result.success) {
      showCompletionModal.value = false
      // Move to completed state to show rating
      tripState.value = 'completed'
      displayToast('Trip confirmed! Please rate your driver.', 'success')
    } else {
      displayToast(result.error || 'Failed to confirm completion', 'error')
    }
  } catch (error) {
    console.error('Error confirming completion:', error)
    displayToast('Failed to confirm completion. Please try again.', 'error')
  } finally {
    isConfirmingCompletion.value = false
  }
}

// Handle complete trip rating
const handleCompleteTripRating = async () => {
  // Validation
  if (rating.value === 0) {
    window.$notification?.warning('Please rate your driver before submitting', { title: 'Rating Required' })
    return
  }

  isSubmittingRating.value = true
  
  try {
    // First, confirm completion if not already confirmed
    if (activeTrip.value && !activeTrip.value.rider_confirmed_completion) {
      console.log('🔄 Auto-confirming trip completion before rating...')
      const confirmResult = await confirmCompletion()
      
      if (!confirmResult.success) {
        displayToast(confirmResult.error || 'Failed to confirm completion', 'error')
        return
      }
      console.log('✅ Trip completion confirmed')
    }
    
    // Then submit the rating
    const result = await completeTripRating(rating.value, review.value)
    
    if (result.success) {
      window.$notification?.success('Thank you for your feedback!', { title: 'Rating Submitted', priority: 'high' })
      // Reset rating state
      rating.value = 0
      review.value = ''
    } else {
      displayToast(result.error || 'Failed to submit rating', 'error')
    }
  } catch (error) {
    console.error('Error submitting rating:', error)
    displayToast('Failed to submit rating. Please try again.', 'error')
  } finally {
    isSubmittingRating.value = false
  }
}

// Computed
const bottomSheetHeight = computed(() => {
  switch (tripState.value) {
    case 'search':
      return 'h-[420px]' // Compact for destination input
    case 'select-driver':
      // Dynamic height based on number of drivers
      const driverCount = nearbyDrivers.value?.length || 0
      if (driverCount === 0) return 'h-[380px]' // No drivers - compact with message
      if (driverCount === 1) return 'h-[380px]' // Single driver - compact
      if (driverCount === 2) return 'h-[480px]' // Two drivers
      if (driverCount === 3) return 'h-[580px]' // Three drivers
      return 'h-[600px]' // Many drivers with scroll
    case 'driver-found':
      return 'h-[650px]'
    case 'requested':
      return 'h-[650px]'
    case 'driver-approaching':
      return 'h-[650px]' // Optimized for driver info + route + actions
    case 'active':
      return 'h-[700px]'
    case 'completed':
      return 'h-[600px]'
    default:
      return 'h-[420px]'
  }
})

const user = computed(() => authStore.user || {
  name: 'Ahmed Ben Ali',
  phone: '+216 12 345 678',
  email: 'ahmed@example.com',
  hasDriverProfile: false
})

// Methods - Wrappers to connect composables
const handleEnableDestinationPicker = () => {
  enableDestinationPicker(map.value, () => {
    showBottomSheet.value = false
  })
  
  // Add click listener
  if (map.value) {
    map.value.on('click', handleMapClickForDestination)
  }
}

const handleMapClickForDestination = (e) => {
  onMapClickForDestination(e, map.value, setDestinationMarker)
}

const handleConfirmDestination = () => {
  // Draw route before confirming
  if (tempDestinationCoords.value) {
    drawRoute(tempDestinationCoords.value.lng, tempDestinationCoords.value.lat)
    
    // Update the destination search field with coordinates or location name
    // Format: "Latitude, Longitude"
    destinationSearch.value = `${tempDestinationCoords.value.lat.toFixed(4)}, ${tempDestinationCoords.value.lng.toFixed(4)}`
  }
  
  confirmDestination(map.value, () => {
    showBottomSheet.value = true
  })
}

const handleCancelDestination = () => {
  // Clear the route when canceling
  clearRoute()
  
  cancelDestination(map.value, removeDestinationMarker, () => {
    showBottomSheet.value = true
  })
}

// Wrapper for selectDestination to also update search field
const handleSelectDestination = (suggestion) => {
  console.log('🎯 Destination selected from list:', suggestion)
  destinationSearch.value = suggestion.name
  selectDestination(suggestion)
  
  // Update tempDestinationCoords with the selected location coordinates
  if (suggestion.coords) {
    tempDestinationCoords.value = suggestion.coords
    console.log('📍 Destination coords set:', suggestion.coords)
    
    // Set the destination marker on the map
    if (map.value && suggestion.coords) {
      console.log('🗺️ Setting marker and drawing route...')
      setDestinationMarker(suggestion.coords.lng, suggestion.coords.lat)
      
      // Draw route from user location to destination
      drawRoute(suggestion.coords.lng, suggestion.coords.lat)
    }
  }
}

const confirmDriverSelection = async () => {
  // Prevent double submission
  if (isCreatingTrip.value) {
    console.log('⚠️ Trip creation already in progress')
    return
  }

  console.log('confirmDriverSelection called, selectedDriver:', selectedDriver.value?.name)
  console.log('tempDestinationCoords:', tempDestinationCoords.value)
  console.log('destination:', destination.value)
  
  if (!selectedDriver.value) {
    console.error('No driver selected!')
    window.$notification?.warning('Please select a driver first', { title: 'No Driver Selected' })
    return
  }
  
  if (!tempDestinationCoords.value) {
    console.error('No destination coordinates!')
    window.$notification?.warning('Please select a destination first', { title: 'No Destination' })
    return
  }
  
  // Set loading state
  isCreatingTrip.value = true
  
  try {
    // Fetch real pickup address name from coordinates using locationFormatter
    const pickupAddressName = await formatCurrentLocation(userLocation.value)
    console.log('📍 Fetched pickup address:', pickupAddressName)
    
    // Prepare destination address
    const destinationAddr = destination.value?.name || destination.value || destinationSearch.value || null
    
    // Prepare optional fields
    const options = {
      pickupAddress: pickupAddressName,
      riderNotes: riderNotes.value.trim() || null,
      tripType: 'regular' // Can be made dynamic later (regular, express, scheduled)
    }
    
    console.log('📤 Trip request details:', {
      pickup: userLocation.value,
      destination: tempDestinationCoords.value,
      destinationAddress: destinationAddr,
      options: options
    })
    
    // Request ride with all parameters
    console.log('🚀 About to call requestRide...')
    const result = await requestRide(
      userLocation.value, 
      tempDestinationCoords.value, 
      destinationAddr,
      options
    )
    
    console.log('📦 Result from requestRide:', result)
    console.log('📦 Result.success:', result.success)
    console.log('📦 Result.trip:', result.trip)
    
    if (result.success) {
      console.log('✅ Trip created successfully:', result.trip)
      console.log('📊 Current trip state:', tripState.value)
      console.log('📊 Backend status:', result.trip.status)
      
      displayToast('Searching for driver...', 'success')
      
      // Trip state is already set by useTripManagement based on backend status
      // Backend status "requested" = frontend state "requested" (searching for driver)
      // No need to force state here - let the backend status control it
      
      // Clear notes after successful trip creation
      riderNotes.value = ''
      // Polling will automatically start via watch on tripState
    } else {
      console.error('❌ Failed to create trip:', {
        error: result.error,
        message: result.message,
        fullResult: result
      })
      
      // Get the actual error message from backend
      const errorMsg = result.message || result.error || 'Failed to create trip. Please try again.'
      
      // Show error message
      displayToast(errorMsg, 'error')
    }
  } catch (error) {
    console.error('❌ Unexpected error:', error)
    displayToast('An unexpected error occurred. Please try again.', 'error')
  } finally {
    // Reset loading state
    isCreatingTrip.value = false
  }
}

const handleSelectAndConfirmDriver = (driver) => {
  selectAndConfirmDriver(driver, confirmDriverSelection)
}

const handleFindDriver = () => {
  findDriver((show) => {
    showBottomSheet.value = show
  })
}

const navigateTo = (path) => {
  showSideMenu.value = false
  router.push(path)
}

const switchToDriver = () => {
  showSideMenu.value = false
  router.push('/driver')
}

const logout = () => {
  showSideMenu.value = false
  authStore.logout()
  router.push('/login')
}

// Notifications
const showNotificationsPanel = ref(false)
const {
  notifications,
  unreadCount: unreadNotifications,
  markAsRead,
  clearAll: clearAllNotifications,
  notifyTripCompleted,
  notifyTripCancelled,
  notifyTripAccepted,
  notifyDriverArrived,
  notifyTripStarted,
  notifyNoDriversAvailable,
  notifyDriverDeclined
} = useNotificationStore()

// Map Methods
const recenterToMyLocation = () => {
  centerOnUserLocation()
}

const zoomIn = () => {
  if (map.value) {
    map.value.zoomIn({ duration: 300 })
  }
}

const zoomOut = () => {
  if (map.value) {
    map.value.zoomOut({ duration: 300 })
  }
}

const toggleNotifications = () => {
  showNotificationsPanel.value = !showNotificationsPanel.value
}

// markAsRead is now from notification store
// Function signature: markAsRead(notificationId)

const clearAllNotifications_func = () => {
  clearAllNotifications()
  showNotificationsPanel.value = false
}

// Trip status polling
let statusPollingInterval = null

const startTripStatusPolling = () => {
  // Poll every 3 seconds while trip is active (faster for real-time sync)
  if (statusPollingInterval) clearInterval(statusPollingInterval)
  
  statusPollingInterval = setInterval(async () => {
    if (tripState.value !== 'search' && tripState.value !== 'select-driver' && tripState.value !== 'completed') {
      console.log('🔄 Polling trip status...')
      await refreshTripStatus()
    }
  }, 3000) // Faster polling for real-time updates
}

const stopTripStatusPolling = () => {
  if (statusPollingInterval) {
    clearInterval(statusPollingInterval)
    statusPollingInterval = null
  }
}

// Real-time driver status polling with change detection
let driverPollingInterval = null
let lastDriverListHash = null

// Create hash from driver list to detect changes
const createDriverListHash = (drivers) => {
  if (!drivers || drivers.length === 0) return 'empty'
  // Create hash from driver IDs and count - this detects additions/removals
  // Include distances rounded to 0.1km to detect significant movements
  const driverIds = drivers.map(d => d.user_id).sort().join(',')
  const count = drivers.length
  const distances = drivers.map(d => Math.round(d.distance_km * 10)).sort().join(',')
  return `count:${count}|ids:${driverIds}|dist:${distances}`
}

const startDriverPolling = () => {
  // Poll every 10 seconds to get updated driver list (optimized interval)
  if (driverPollingInterval) clearInterval(driverPollingInterval)
  
  driverPollingInterval = setInterval(async () => {
    // Only poll drivers when in search/select-driver state and have user location
    if ((tripState.value === 'search' || tripState.value === 'select-driver') && 
        userLocation.value && userLocation.value.lat && userLocation.value.lng) {
      
      try {
        // Fetch updated driver list silently (no loading spinner, no console spam)
        const result = await fetchNearbyDrivers(
          userLocation.value.lat,
          userLocation.value.lng,
          { skipUpdate: true, silent: true }
        )
        
        if (result.updated) {
          const newDrivers = result.drivers
          const newHash = createDriverListHash(newDrivers)
          
          // Only update UI if driver list actually changed
          if (newHash !== lastDriverListHash) {
            console.log('✨ Driver list changed, updating UI...')
            console.log(`  Previous: ${lastDriverListHash || 'none'}`)
            console.log(`  New: ${newHash}`)
            console.log(`  Drivers count: ${newDrivers.length}`)
            
            // Update state and hash
            nearbyDrivers.value = newDrivers
            lastDriverListHash = newHash
          } else {
            console.log('✓ No driver changes detected')
          }
        }
      } catch (error) {
        console.error('Driver polling error:', error)
      }
    }
  }, 10000) // Poll every 10 seconds (optimized)
}

const stopDriverPolling = () => {
  if (driverPollingInterval) {
    clearInterval(driverPollingInterval)
    driverPollingInterval = null
    lastDriverListHash = null // Reset hash for fresh start
  }
}

// Watch trip state to manage polling
// Start trip timer and distance tracker
const startTripTracking = () => {
  // Reset counters
  tripDuration.value = 0
  tripDistance.value = 0
  
  // Start duration timer (updates every second)
  if (tripTimer) clearInterval(tripTimer)
  tripTimer = setInterval(() => {
    tripDuration.value++
  }, 1000)
  
  // Start distance tracker (updates every 5 seconds based on user location)
  if (distanceTracker) clearInterval(distanceTracker)
  
  let lastLocation = null
  distanceTracker = setInterval(() => {
    if (userLocation.value && userLocation.value.lat && userLocation.value.lng) {
      if (lastLocation) {
        // Calculate distance using Haversine formula
        const R = 6371 // Earth radius in km
        const dLat = (userLocation.value.lat - lastLocation.lat) * Math.PI / 180
        const dLon = (userLocation.value.lng - lastLocation.lng) * Math.PI / 180
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(lastLocation.lat * Math.PI / 180) * Math.cos(userLocation.value.lat * Math.PI / 180) *
                  Math.sin(dLon/2) * Math.sin(dLon/2)
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
        const distance = R * c
        
        // Add to total distance
        tripDistance.value += distance
      }
      lastLocation = { lat: userLocation.value.lat, lng: userLocation.value.lng }
    }
  }, 5000) // Update every 5 seconds
  
  console.log('📊 Trip tracking started')
}

const stopTripTracking = () => {
  if (tripTimer) {
    clearInterval(tripTimer)
    tripTimer = null
  }
  if (distanceTracker) {
    clearInterval(distanceTracker)
    distanceTracker = null
  }
  console.log('📊 Trip tracking stopped')
}

// Watch user location to fetch nearest places
watch(userLocation, async (newLocation) => {
  if (newLocation && newLocation.lat && newLocation.lng) {
    console.log('📍 User location updated, fetching nearest places...')
    fetchNearestPlaces()
    // Update pickup location address when location changes
    await updatePickupLocationAddress()
  }
}, { deep: true })

// Debug watcher for nearbyDrivers
watch(nearbyDrivers, (newDrivers) => {
  console.log('🚕 Nearby drivers updated:', {
    count: newDrivers?.length || 0,
    drivers: newDrivers,
    hasData: !!newDrivers && newDrivers.length > 0
  })
}, { deep: true, immediate: true })

watch(tripState, async (newState, oldState) => {
  console.log(`🔄 Trip state changed: ${oldState} → ${newState}`)
  
  // Update formatted addresses when entering requested, driver-approaching or active state
  if (newState === 'requested' || newState === 'driver-approaching' || newState === 'active') {
    console.log('📍 Updating formatted addresses for new state:', newState)
    await updateFormattedAddresses()
  }
  
  // When returning to search state, refresh the pickup location address
  if (newState === 'search' && (oldState === 'requested' || oldState === 'driver-found' || oldState === 'active' || oldState === 'completed')) {
    console.log('📍 Returning to search - refreshing pickup address')
    await updatePickupLocationAddress()
  }
  
  // Start trip status polling when trip becomes active
  if ((newState === 'requested' || newState === 'driver-found' || newState === 'active') && 
      (oldState === 'search' || oldState === 'select-driver')) {
    console.log('▶️ Starting trip status polling')
    startTripStatusPolling()
    // Stop driver polling when trip is active
    console.log('⏹️ Stopping driver polling (trip active)')
    stopDriverPolling()
  }
  
  // Start tracking when trip becomes active (driver started the trip)
  if (newState === 'active' && oldState !== 'active') {
    console.log('🚗 Trip started - beginning tracking and drawing route')
    startTripTracking()
    
    // Draw route from current location to destination
    if (activeTrip.value && activeTrip.value.destination_longitude && activeTrip.value.destination_latitude) {
      await drawRoute(activeTrip.value.destination_longitude, activeTrip.value.destination_latitude)
    }
  }
  
  // Stop tracking when trip ends
  if (oldState === 'active' && newState !== 'active') {
    console.log('🛑 Trip ended - stopping tracking')
    stopTripTracking()
  }
  
  // Stop trip polling and resume driver polling when trip completes or returns to search
  if ((newState === 'search' || newState === 'select-driver') && 
      (oldState === 'requested' || oldState === 'driver-found' || oldState === 'active' || oldState === 'completed')) {
    console.log('⏹️ Stopping trip status polling')
    stopTripStatusPolling()
    stopTripTracking()
    // Resume driver polling when back to searching
    console.log('▶️ Resuming driver status polling')
    startDriverPolling()
  }
  
  // Show completion confirmation modal when driver marks trip as completed
  if (newState === 'completed' && oldState === 'active') {
    console.log('✅ Trip completed by driver - showing confirmation modal')
    showCompletionModal.value = true
    stopTripStatusPolling()
    stopDriverPolling()
    stopTripTracking()
  }
  
  // Stop both when completed
  if (newState === 'completed') {
    console.log('⏹️ Stopping all polling (trip completed)')
    stopTripStatusPolling()
    stopDriverPolling()
    stopTripTracking()
  }
})

// Function to update pickup location with actual address using locationFormatter
const updatePickupLocationAddress = async () => {
  console.log('🔄 Fetching address for current location...')
  
  if (userLocation.value?.lat && userLocation.value?.lng) {
    try {
      const address = await formatCurrentLocation(userLocation.value)
      pickupLocation.value = address
      console.log('✅ Pickup location updated:', address)
    } catch (error) {
      console.error('❌ Error getting address:', error)
      pickupLocation.value = 'Current location'
    }
  } else {
    console.log('⚠️ Location not ready, retrying in 1s...')
    setTimeout(() => updatePickupLocationAddress(), 1000)
  }
}

// Watch for activeTrip changes to update formatted addresses
watch(activeTrip, async (newTrip) => {
  if (newTrip) {
    console.log('👁️ activeTrip changed, updating formatted addresses:', newTrip)
    
    // Use backend addresses if available
    if (newTrip.pickup_address && newTrip.pickup_address !== 'Pickup location') {
      formattedPickupAddress.value = newTrip.pickup_address
      console.log('✅ Pickup address from backend:', newTrip.pickup_address)
    } else if (newTrip.pickup_latitude && newTrip.pickup_longitude) {
      // Fallback to frontend geocoding
      try {
        formattedPickupAddress.value = await formatTripLocation(newTrip, 'pickup')
      } catch (error) {
        console.error('❌ Error formatting pickup:', error)
        formattedPickupAddress.value = `Location (${newTrip.pickup_latitude.toFixed(4)}, ${newTrip.pickup_longitude.toFixed(4)})`
      }
    }
    
    if (newTrip.destination_address && newTrip.destination_address !== 'Destination') {
      formattedDestinationAddress.value = newTrip.destination_address
      console.log('✅ Destination address from backend:', newTrip.destination_address)
    } else if (newTrip.destination_latitude && newTrip.destination_longitude) {
      // Fallback to frontend geocoding
      try {
        formattedDestinationAddress.value = await formatTripLocation(newTrip, 'destination')
      } catch (error) {
        console.error('❌ Error formatting destination:', error)
        formattedDestinationAddress.value = `${newTrip.destination_latitude.toFixed(4)}, ${newTrip.destination_longitude.toFixed(4)}`
      }
    }
  }
}, { immediate: true, deep: true })

// Lifecycle
onMounted(async () => {
  console.log('🚀 Rider Dashboard mounted')
  
  // Initialize map immediately (non-blocking)
  initMap()
  getCurrentLocation()
  
  // Parallelize independent operations for faster loading
  const user = authStore.user
  const operations = []
  
  // 1. Subscribe to notifications (non-blocking)
  if (user && user.id) {
    operations.push(
      riderNotificationService.subscribe(user.id, (notification) => {
        console.log('📬 Received real-time notification:', notification)
        if (['trip_accepted', 'trip_cancelled', 'trip_started', 'driver_arrived'].includes(notification.type)) {
          setTimeout(() => refreshTripStatus(), 500)
        }
      }).catch(err => console.warn('⚠️ Notification subscription failed:', err))
    )
  }
  
  // 2. Check for active trip (parallel with other operations)
  operations.push(checkActiveTrip())
  
  // Wait for all operations to complete
  const [, hasActiveTrip] = await Promise.allSettled(operations)
  const isActiveTripPresent = hasActiveTrip.status === 'fulfilled' && hasActiveTrip.value
  
  // Update pickup address in background (delayed, non-blocking)
  setTimeout(() => updatePickupLocationAddress(), 800)
  
  if (isActiveTripPresent) {
    console.log('✅ Resuming active trip')
    
    // Restore trip state to UI
    if (window.restoreTripState) {
      const tripData = window.restoreTripState
      
      // Restore destination
      if (tripData.destination) {
        destination.value = tripData.destination.address
        destinationCoords.value = {
          lat: tripData.destination.lat,
          lng: tripData.destination.lng
        }
      }
      
      // Restore pickup
      if (tripData.pickup) {
        pickupLocation.value = tripData.pickup.address
      }
      
      // Add map markers after a short delay to ensure map is ready
      setTimeout(() => {
        if (tripData.pickup && tripData.destination && map.value) {
          console.log('📍 Restoring trip markers on map')
          addPickupMarker(tripData.pickup.lat, tripData.pickup.lng)
          addDestinationMarker(tripData.destination.lat, tripData.destination.lng)
          
          // Draw route if available
          drawRoute(
            { lat: tripData.pickup.lat, lng: tripData.pickup.lng },
            { lat: tripData.destination.lat, lng: tripData.destination.lng }
          )
        }
      }, 500)
    }
    
    startTripStatusPolling()
  } else {
    // No active trip, start driver polling
    console.log('▶️ Starting driver status polling')
    startDriverPolling()
    
    // Do initial fetch if location is already available
    if (userLocation.value && userLocation.value.lat && userLocation.value.lng) {
      console.log('📍 User location available, fetching initial driver list...')
      fetchNearbyDrivers(userLocation.value.lat, userLocation.value.lng)
      // Also fetch nearest places for destination suggestions
      fetchNearestPlaces()
    }
  }
})

// Cleanup on unmount
onUnmounted(() => {
  stopTripStatusPolling()
  stopDriverPolling()
  stopTripTracking()
  riderNotificationService.unsubscribe()
  console.log('👋 Rider Dashboard unmounted, unsubscribed from notifications')
})
</script>

<style scoped src="./RiderDashboard.css"></style>
