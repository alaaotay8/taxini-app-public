<template>
  <div class="driver-container">
    <!-- Pending Approval Banner (Yellow) -->
    <transition name="fade">
      <div v-if="accountStatus === 'locked'" class="approval-banner pending">
        <div class="approval-banner-content">
          <svg xmlns="http://www.w3.org/2000/svg" class="approval-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div class="approval-text">
            <h3>Account Pending Verification</h3>
            <p>Please wait while we verify your documents. You'll be notified once your account is approved.</p>
          </div>
          <button @click="logout" class="btn-sign-out">
            <svg xmlns="http://www.w3.org/2000/svg" class="sign-out-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Sign Out
          </button>
        </div>
      </div>
    </transition>

    <!-- Account Blocked Banner (Red) -->
    <transition name="fade">
      <div v-if="accountStatus === 'banned'" class="approval-banner blocked">
        <div class="approval-banner-content">
          <svg xmlns="http://www.w3.org/2000/svg" class="approval-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
          </svg>
          <div class="approval-text">
            <h3>Account Blocked</h3>
            <p>Your account has been suspended. Please contact support for more information.</p>
          </div>
          <button @click="logout" class="btn-sign-out">
            <svg xmlns="http://www.w3.org/2000/svg" class="sign-out-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Sign Out
          </button>
        </div>
      </div>
    </transition>

    <!-- Map Container (Full Screen) -->
    <div ref="mapContainer" class="map-container" @click="handleMapClick"></div>

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
      <button @click="recenterMap" class="map-control-btn map-control-location" title="Return to current location">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </button>
    </div>

    <!-- Toggle Trip Card Button (shows when card is hidden) -->
    <button 
      v-if="!showTripCard && currentTrip && (currentTrip.status === 'accepted' || currentTrip.status === 'started')" 
      @click="showTripCard = true" 
      class="fixed bottom-6 left-1/2 transform -translate-x-1/2 z-50 bg-taxini-yellow text-taxini-dark px-6 py-3 rounded-full shadow-lg hover:bg-yellow-400 transition-all font-bold flex items-center gap-2"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      Show Trip Info
    </button>

    <!-- Top Bar (Rider-style with Hamburger Menu) -->
    <div class="top-bar">
      <button @click="toggleMenu" class="btn-hamburger">
        <svg xmlns="http://www.w3.org/2000/svg" class="hamburger-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      <div class="top-bar-title">
        <h1>Hi, {{ driverFirstName }}!</h1>
      </div>
      <button @click="toggleNotifications" class="btn-notification">
        <svg xmlns="http://www.w3.org/2000/svg" class="notification-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        <span v-if="unreadNotifications > 0" class="notification-badge">{{ unreadNotifications }}</span>
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

    <!-- Side Menu Drawer (Like Rider) -->
    <transition name="slide-left">
      <div v-if="showMenu" class="menu-overlay" @click="toggleMenu">
        <div class="side-menu" @click.stop>
          <!-- User Profile Section -->
          <div class="menu-header">
            <div class="user-avatar">
              <span class="avatar-text">{{ driverInitials }}</span>
            </div>
            <div class="user-info">
              <h3 class="user-name">{{ driverName }}</h3>
              <p class="user-phone">{{ driverPhone }}</p>
            </div>
          </div>

          <!-- Edit Profile Button -->
          <button @click="goToProfile" class="btn-edit-profile">
            Edit Profile
          </button>

          <!-- Menu Items -->
          <div class="menu-items">
            <button 
              @click="isAccountRestricted ? null : goToHistory()" 
              class="menu-item"
              :class="{ 'disabled': isAccountRestricted }"
              :disabled="isAccountRestricted"
            >
              <svg class="menu-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              <span class="menu-item-text">Trip History</span>
            </button>
            <button 
              @click="isAccountRestricted ? null : goToEarnings()" 
              class="menu-item"
              :class="{ 'disabled': isAccountRestricted }"
              :disabled="isAccountRestricted"
            >
              <svg class="menu-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="1" x2="12" y2="23"/>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
              </svg>
              <span class="menu-item-text">Earnings</span>
            </button>
            <button 
              @click="isAccountRestricted ? null : goToSupport()" 
              class="menu-item"
              :class="{ 'disabled': isAccountRestricted }"
              :disabled="isAccountRestricted"
            >
              <svg class="menu-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
              <span class="menu-item-text">Support</span>
            </button>
          </div>

          <!-- Logout Button -->
          <button @click="logout" class="btn-logout">
            <svg class="logout-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            <span class="logout-text">Logout</span>
          </button>
        </div>
      </div>
    </transition>

    <!-- Show Bottom Sheet Button (appears when hidden) -->
    <transition name="fade">
      <div v-if="!showBottomSheet && !currentTrip && !incomingRequest" class="show-sheet-btn" @click="toggleBottomSheet">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="18 15 12 9 6 15"/>
        </svg>
      </div>
    </transition>

    <!-- Bottom Sheet: OFFLINE MODE -->
    <transition name="slide-up">
      <div 
        v-if="!isOnline && !currentTrip && showBottomSheet" 
        class="bottom-sheet offline-mode"
        @touchstart="handleBottomSheetTouchStart"
        @touchmove="handleBottomSheetTouchMove"
        @touchend="handleBottomSheetTouchEnd"
      >
        <div class="sheet-handle" @click="toggleBottomSheet"></div>
        <div class="sheet-content">
          <!-- Today's Summary -->
          <div class="summary-section-title">Today's Summary</div>
          <div class="today-summary">
            <div class="summary-card">
              <div class="summary-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="1" x2="12" y2="23"/>
                  <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                </svg>
              </div>
              <div class="summary-info">
                <div class="summary-value">{{ todayEarnings.toFixed(2) }} TND</div>
                <div class="summary-label">Earnings</div>
              </div>
            </div>
            <div class="summary-card">
              <div class="summary-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
              </div>
              <div class="summary-info">
                <div class="summary-value">{{ todayTrips }}</div>
                <div class="summary-label">Trips</div>
              </div>
            </div>
            <div class="summary-card">
              <div class="summary-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
              </div>
              <div class="summary-info">
                <div class="summary-value">{{ onlineHours.toFixed(2) }}h</div>
                <div class="summary-label">Hours Online</div>
              </div>
            </div>
          </div>

          <!-- Large Status Toggle -->
          <div class="status-toggle-container">
            <div class="status-indicator offline">
              <div class="status-dot"></div>
              <span class="status-text">YOU'RE OFFLINE</span>
            </div>
            <button 
              @click="toggleOnlineStatus" 
              class="btn-toggle-status"
              :disabled="isAccountRestricted"
              :class="{ 'disabled': isAccountRestricted }"
            >
              <svg class="toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <circle cx="12" cy="12" r="10"/>
                <path d="M8 12l2 2 4-4"/>
              </svg>
              <span class="toggle-text">{{ isAccountRestricted ? 'ACCOUNT PENDING' : 'GO ONLINE' }}</span>
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Bottom Sheet: ONLINE MODE (Waiting for Trips) -->
    <transition name="slide-up">
      <div 
        v-if="isOnline && !currentTrip && !incomingRequest && showBottomSheet" 
        class="bottom-sheet online-waiting"
        @touchstart="handleBottomSheetTouchStart"
        @touchmove="handleBottomSheetTouchMove"
        @touchend="handleBottomSheetTouchEnd"
      >
        <div class="sheet-handle" @click="toggleBottomSheet"></div>
        <div class="sheet-content">
          <!-- Waiting Status -->
          <div class="waiting-header">
            <div class="waiting-animation">
              <div class="pulse-ring"></div>
              <div class="pulse-ring" style="animation-delay: 0.5s"></div>
              <div class="waiting-icon">🚕</div>
            </div>
            <h3 class="waiting-title">Waiting for trips...</h3>
            <p class="waiting-subtitle">You'll be notified when a rider requests</p>
          </div>

          <!-- Today's Stats -->
          <div class="stats-container">
            <div class="stat-card">
              <div class="stat-icon trips">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
              </div>
              <div class="stat-details">
                <div class="stat-value">{{ todayTrips }}</div>
                <div class="stat-label">Trips</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon earnings">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="1" x2="12" y2="23"/>
                  <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                </svg>
              </div>
              <div class="stat-details">
                <div class="stat-value">{{ todayEarnings.toFixed(2) }} TND</div>
                <div class="stat-label">Earnings</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon hours">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
              </div>
              <div class="stat-details">
                <div class="stat-value">{{ onlineHours.toFixed(2) }}h</div>
                <div class="stat-label">Online</div>
              </div>
            </div>
          </div>

          <!-- Large Status Toggle -->
          <div class="status-toggle-container">
            <div class="status-indicator online">
              <div class="status-dot"></div>
              <span class="status-text">YOU'RE ONLINE</span>
            </div>
            <button @click="toggleOnlineStatus" class="btn-toggle-status offline-mode">
              <svg class="toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <rect x="6" y="4" width="4" height="16"/>
                <rect x="14" y="4" width="4" height="16"/>
              </svg>
              <span class="toggle-text">GO OFFLINE</span>
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Trip Request Notification (Modal Pop-up with Timer) -->
    
    <!-- Floating Return Button (shown when previewing route) -->
    <transition name="fade">
      <div v-if="routeMode === 'preview' && !isModalContentVisible" class="floating-return-button">
        <button @click="previewTripRoute" class="btn-return">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 17l-5-5m0 0l5-5m-5 5h12" />
          </svg>
          <span>Back to Trip Details</span>
        </button>
      </div>
    </transition>
    
    <transition name="modal-fade">
      <div v-if="incomingRequest && isModalContentVisible" class="trip-request-modal">
        <div class="modal-overlay" @click="declineTrip"></div>
        <!-- Modal content -->
        <div class="modal-content compact">
          <!-- Countdown Timer -->
          <div class="countdown-timer">
            <div class="countdown-circle">
              <svg width="70" height="70">
                <circle cx="35" cy="35" r="30" class="countdown-bg"></circle>
                <circle cx="35" cy="35" r="30" class="countdown-progress" :style="{ strokeDashoffset: countdownOffset }"></circle>
              </svg>
              <div class="countdown-text">{{ countdown }}s</div>
            </div>
          </div>

          <!-- Notification Header -->
          <div class="modal-header">
            <h2 class="modal-title">New Trip Request</h2>
          </div>

          <!-- Rider Info with Rating -->
          <div class="rider-info-card">
            <div class="rider-avatar">
              <span class="avatar-text">{{ getInitials(incomingRequest.rider_name) }}</span>
            </div>
            <div class="rider-details">
              <div class="rider-name">{{ incomingRequest.rider_name }}</div>
              <div class="rider-rating">
                <span class="rating-stars">⭐ {{ incomingRequest.rider_rating || 4.8 }}</span>
                <span class="rating-count">({{ incomingRequest.rider_trips || 45 }} trips)</span>
              </div>
            </div>
          </div>

          <!-- Trip Details -->
          <div class="trip-request-details">
            <!-- Pickup Location with Distance -->
            <div class="location-card pickup-card">
              <div class="location-info">
                <div class="location-label">PICKUP LOCATION</div>
                <div class="location-address">{{ incomingRequest.pickup_location_name }}</div>
                <div class="location-distance">
                  <span class="distance-text">{{ incomingRequest.distance_from_driver || '2.3' }} km away</span>
                </div>
              </div>
            </div>

            <!-- Destination Preview -->
            <div class="location-card destination-card">
              <div class="location-info">
                <div class="location-label">DESTINATION</div>
                <div class="location-address">{{ incomingRequest.destination_location_name }}</div>
              </div>
            </div>
          </div>

          <!-- Earnings & Distance -->
          <div class="earnings-distance-card">
            <div class="earnings-item">
              <div class="earnings-info">
                <div class="earnings-label">Potential Earnings</div>
                <div class="earnings-amount">{{ incomingRequest.estimated_cost_tnd }} TND</div>
              </div>
            </div>
            <div class="earnings-divider"></div>
            <div class="earnings-item">
              <div class="earnings-info">
                <div class="earnings-label">Trip Distance</div>
                <div class="earnings-amount">{{ incomingRequest.estimated_distance_km }} km</div>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="modal-actions">
            <!-- Preview Route Button (Shows trip path) -->
            <button 
              @click="previewTripRoute" 
              class="btn-preview-route"
              :class="{ 'active': routeMode === 'preview' }"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
              <span>{{ routeMode === 'preview' ? 'Hide' : 'Preview' }} Route</span>
            </button>
          </div>
          
          <div class="modal-actions">
            <button @click="declineTrip" :disabled="isAcceptingTrip" class="btn-reject">
              <span>DECLINE</span>
            </button>
            <button @click="acceptTrip" :disabled="isAcceptingTrip" class="btn-accept-large">
              <span v-if="!isAcceptingTrip">ACCEPT TRIP</span>
              <span v-else class="loading-text">
                <svg class="spinner" viewBox="0 0 24 24">
                  <circle class="spinner-circle" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
                </svg>
                ACCEPTING...
              </span>
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Bottom Sheet: TRIP ACCEPTED (Going to Pickup) -->
    <transition name="slide-up">
      <div v-if="currentTrip && currentTrip.status === 'accepted' && showTripCard" class="bottom-sheet trip-accepted">
        <div class="sheet-handle"></div>
        <div class="sheet-content">
          <!-- Trip Status Header -->
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-xl font-bold text-white">Going to Pickup</h2>
            <div class="px-3 py-1 bg-green-500/20 border border-green-500 rounded-full">
              <span class="text-green-500 font-bold text-xs">Driver Accepted</span>
            </div>
          </div>

          <!-- Rider Info Card -->
          <div class="bg-[#0d2621] rounded-xl p-3 mb-3 border border-taxini-green/20">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 bg-taxini-green/20 rounded-full flex items-center justify-center">
                <span class="text-taxini-yellow font-bold text-base">{{ getInitials(currentTrip.rider_name) }}</span>
              </div>
              <div class="flex-1">
                <h3 class="text-base font-bold text-white">{{ currentTrip.rider_name }}</h3>
                <p class="text-taxini-text-gray text-xs">{{ currentTrip.rider_phone }}</p>
              </div>
              <a :href="`tel:${currentTrip.rider_phone}`" class="bg-taxini-yellow text-taxini-dark p-2 rounded-full hover:bg-yellow-400 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
              </a>
            </div>
          </div>

          <!-- Pickup Location Card -->
          <div class="bg-[#0d2621] rounded-xl p-3 mb-3 border border-taxini-green/20">
            <div class="flex items-start gap-2">
              <div class="w-2 h-2 bg-green-500 rounded-full mt-1"></div>
              <div class="flex-1">
                <p class="text-taxini-text-gray text-xs mb-1">Pickup Location</p>
                <p class="text-white font-medium text-sm mb-1">{{ currentTrip.pickup_location_name }}</p>
                <div class="flex items-center gap-1">
                  <span class="text-green-500 font-bold text-base">{{ approachDistance }} km</span>
                  <span class="text-taxini-text-gray text-xs">away</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Cost Breakdown Card -->
          <div class="bg-gradient-to-br from-taxini-yellow/10 to-taxini-green/10 border-2 border-taxini-yellow/30 rounded-xl p-3 mb-3">
            <div class="flex items-center gap-2 mb-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-taxini-yellow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="text-taxini-yellow font-bold text-xs uppercase tracking-wide">Estimated Cost</span>
            </div>
            
            <div class="space-y-1">
              <!-- Approach Fee -->
              <div v-if="currentTrip.approach_fee_tnd" class="flex justify-between items-center">
                <span class="text-white/80 text-xs">Frais d'approche ({{ currentTrip.approach_distance_km }}km)</span>
                <span class="text-white font-semibold text-sm">{{ currentTrip.approach_fee_tnd?.toFixed(3) || '0.000' }} TND</span>
              </div>
              
              <!-- Estimated Meter Cost -->
              <div class="flex justify-between items-center">
                <span class="text-white/80 text-xs">Estimation compteur</span>
                <span class="text-white font-semibold text-sm">~{{ currentTrip.estimated_cost_tnd?.toFixed(3) || '0.000' }} TND</span>
              </div>
              
              <div class="border-t border-taxini-yellow/20 my-1"></div>
              
              <!-- Total Estimated -->
              <div class="flex justify-between items-center">
                <span class="text-taxini-yellow font-bold text-sm">Total Estimé</span>
                <span class="text-taxini-yellow font-bold text-lg">~{{ ((currentTrip.approach_fee_tnd || 0) + (currentTrip.estimated_cost_tnd || 0)).toFixed(3) }} TND</span>
              </div>
            </div>
            
            <div class="mt-2 pt-2 border-t border-taxini-yellow/10">
              <p class="text-white/60 text-[10px] italic text-center">Le montant final dépendra de la valeur exacte du compteur à l'arrivée</p>
            </div>
          </div>

          <!-- Waiting for Rider Confirmation Notice (when close to pickup but rider hasn't confirmed) -->
          <div v-if="approachDistance <= 0.1 && !currentTrip.rider_confirmed_pickup" class="bg-blue-500/10 border-2 border-blue-500/30 rounded-xl p-3 mb-3 animate-pulse">
            <div class="flex items-start gap-2">
              <div class="flex-shrink-0 mt-0.5">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h4 class="text-blue-400 font-bold text-sm mb-0.5">Waiting for Rider</h4>
                <p class="text-white/80 text-xs">At pickup. Wait for rider confirmation.</p>
              </div>
            </div>
          </div>

          <!-- Ready to Start Notice (when rider confirmed) -->
          <div v-if="approachDistance <= 0.1 && currentTrip.rider_confirmed_pickup" class="bg-green-500/10 border-2 border-green-500/30 rounded-xl p-3 mb-3">
            <div class="flex items-start gap-2">
              <div class="flex-shrink-0 mt-0.5">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h4 class="text-green-400 font-bold text-sm mb-0.5">Rider Confirmed!</h4>
                <p class="text-white/80 text-xs">Ready to start the trip.</p>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="space-y-2">
            <button @click="openNavigation(currentTrip.pickup_lat, currentTrip.pickup_lng)" class="w-full bg-blue-500 text-white font-bold py-3 rounded-xl hover:bg-blue-600 transition-all flex items-center justify-center gap-2 text-sm">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
              Navigate to Pickup
            </button>
            
            <button @click="startTrip" :disabled="approachDistance > 0.1 || !currentTrip.rider_confirmed_pickup" class="w-full font-bold py-3 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed text-sm" :class="(approachDistance > 0.1 || !currentTrip.rider_confirmed_pickup) ? 'bg-gray-600 text-gray-300' : 'bg-taxini-yellow text-taxini-dark hover:bg-yellow-400'">
              <span v-if="approachDistance > 0.1">Approaching Pickup...</span>
              <span v-else-if="!currentTrip.rider_confirmed_pickup">Waiting for Confirmation...</span>
              <span v-else>Start Trip</span>
            </button>
            
            <button @click="cancelCurrentTrip" class="w-full bg-red-500/20 text-red-500 border-2 border-red-500 font-bold py-3 rounded-xl hover:bg-red-500/30 transition-all text-sm">
              Cancel Trip
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Bottom Sheet: TRIP IN PROGRESS -->
    <transition name="slide-up">
      <div v-if="currentTrip && currentTrip.status === 'started' && showTripCard" class="fixed bottom-0 left-0 right-0 bg-taxini-dark-light rounded-t-3xl shadow-2xl border-t-2 border-taxini-green/30 z-40 px-4 pb-4 overflow-y-auto" style="max-height: 85vh;">
        <!-- Drag Handle -->
        <div class="flex justify-center py-2">
          <div class="w-12 h-1.5 bg-taxini-green/30 rounded-full"></div>
        </div>

        <!-- Status Badge -->
        <div class="text-center mb-3">
          <div class="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500/20 to-taxini-green/20 border-2 border-taxini-green/40 rounded-full">
            <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span class="text-white font-bold text-sm">En Route to Destination</span>
          </div>
        </div>

        <!-- Rider Info Card -->
        <div class="bg-[#0d2621] rounded-xl p-3 mb-3 border border-taxini-green/20">
          <div class="flex items-center gap-3">
            <div class="w-11 h-11 bg-taxini-green/20 rounded-full flex items-center justify-center">
              <span class="text-taxini-yellow font-bold text-base">{{ getInitials(currentTrip.rider_name) }}</span>
            </div>
            <div class="flex-1">
              <h3 class="text-white font-bold text-base">{{ currentTrip.rider_name }}</h3>
              <p class="text-taxini-text-gray text-xs">{{ currentTrip.rider_phone }}</p>
            </div>
            <a :href="`tel:${currentTrip.rider_phone}`" class="bg-taxini-yellow text-taxini-dark px-3 py-2 rounded-lg hover:bg-yellow-400 transition-colors font-bold text-sm">
              📞 Call
            </a>
          </div>
        </div>

        <!-- Destination Card -->
        <div class="bg-[#0d2621] rounded-xl p-3 mb-3 border border-taxini-green/20">
          <div class="flex items-start gap-2">
            <div class="w-8 h-8 bg-red-500/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <div class="flex-1">
              <p class="text-taxini-text-gray text-[10px] font-semibold mb-0.5 uppercase tracking-wide">Destination</p>
              <p class="text-white font-medium text-xs leading-tight">{{ currentTrip.destination_location_name }}</p>
            </div>
          </div>
        </div>

        <!-- Trip Metrics Grid -->
        <div class="grid grid-cols-2 gap-2 mb-3">
          <!-- Duration -->
          <div class="bg-[#0d2621] rounded-lg p-2.5 border border-taxini-green/20">
            <div class="flex items-center gap-1.5 mb-1">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-taxini-green" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="text-taxini-text-gray text-[10px] font-semibold uppercase">Duration</span>
            </div>
            <p class="text-white font-bold text-base">{{ formatDuration(tripDuration) }}</p>
          </div>

          <!-- Distance -->
          <div class="bg-[#0d2621] rounded-lg p-2.5 border border-taxini-green/20">
            <div class="flex items-center gap-1.5 mb-1">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-taxini-yellow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <span class="text-taxini-text-gray text-[10px] font-semibold uppercase">Distance</span>
            </div>
            <p class="text-white font-bold text-base">{{ distanceTraveled.toFixed(1) }} km</p>
          </div>
        </div>

        <!-- Cost Breakdown Card -->
        <div class="bg-gradient-to-br from-taxini-yellow/10 to-taxini-green/10 border-2 border-taxini-yellow/30 rounded-xl p-3 mb-3">
          <div class="flex items-center gap-2 mb-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-taxini-yellow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="text-taxini-yellow font-bold text-xs uppercase tracking-wide">Estimated Cost</span>
          </div>
          
          <div class="space-y-1">
            <!-- Approach Fee -->
            <div v-if="currentTrip.approach_fee_tnd" class="flex justify-between items-center">
              <span class="text-white/80 text-xs">Frais d'approche ({{ currentTrip.approach_distance_km }}km)</span>
              <span class="text-white font-semibold text-sm">{{ currentTrip.approach_fee_tnd?.toFixed(3) || '0.000' }} TND</span>
            </div>
            
            <!-- Estimated Meter Cost -->
            <div class="flex justify-between items-center">
              <span class="text-white/80 text-xs">Estimation compteur</span>
              <span class="text-white font-semibold text-sm">~{{ currentTrip.estimated_cost_tnd?.toFixed(3) || '0.000' }} TND</span>
            </div>
            
            <div class="border-t border-taxini-yellow/20 my-1"></div>
            
            <!-- Total Estimated -->
            <div class="flex justify-between items-center">
              <span class="text-taxini-yellow font-bold text-sm">Total Estimé</span>
              <span class="text-taxini-yellow font-bold text-base">~{{ ((currentTrip.approach_fee_tnd || 0) + (currentTrip.estimated_cost_tnd || 0)).toFixed(3) }} TND</span>
            </div>
          </div>
          
          <div class="mt-2 text-center">
            <p class="text-white/60 text-[10px] italic">Le montant final dépendra de la valeur exacte du compteur à l'arrivée</p>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="space-y-2">
          <!-- Navigate to Destination -->
          <button @click="openNavigation(currentTrip.destination_lat, currentTrip.destination_lng)" class="w-full bg-blue-500 text-white font-bold py-3 rounded-xl hover:bg-blue-600 transition-all flex items-center justify-center gap-2 shadow-lg text-sm" :class="isNavigating ? 'ring-2 ring-blue-300 animate-pulse' : ''">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
            <span v-if="isNavigating && remainingDistance">Navigating ({{ remainingDistance }} km remaining)</span>
            <span v-else>Navigate to Destination</span>
          </button>

          <!-- Complete Trip -->
          <button @click="completeTrip" class="w-full bg-taxini-green text-white font-bold py-3 rounded-xl hover:bg-taxini-green-dark transition-all flex items-center justify-center gap-2 shadow-lg text-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Arrived - Complete Trip
          </button>

          <!-- Cancel Trip -->
          <button @click="cancelCurrentTrip" class="w-full bg-red-500/20 text-red-500 border-2 border-red-500 font-bold py-3 rounded-xl hover:bg-red-500/30 transition-all flex items-center justify-center gap-2 text-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            Cancel Trip
          </button>
        </div>
      </div>
    </transition>

    <!-- Trip Completed Modal (Rating) -->
    <transition name="modal-fade">
      <div v-if="showCompletedModal" class="trip-completed-modal">
        <div class="modal-overlay"></div>
        <div class="modal-content-completed">
          <!-- Success Icon -->
          <div class="success-icon">
            <div class="success-circle">✅</div>
          </div>

          <h2 class="completed-title">Trip Completed!</h2>

          <!-- Trip Summary -->
          <div class="trip-summary-card">
            <div class="summary-row">
              <span class="summary-label">Trip Fare</span>
              <span class="summary-value">{{ completedTrip.estimated_cost_tnd }} TND</span>
            </div>
            <div class="summary-row">
              <span class="summary-label">Distance</span>
              <span class="summary-value">{{ completedTrip.estimated_distance_km }} km</span>
            </div>
            <div class="summary-row">
              <span class="summary-label">Duration</span>
              <span class="summary-value">{{ formatDuration(completedTrip.duration) }}</span>
            </div>
          </div>

          <!-- Earnings Breakdown -->
          <div class="earnings-breakdown">
            <div class="breakdown-title">Earnings Breakdown</div>
            <div class="breakdown-row">
              <span class="breakdown-label">Total Fare</span>
              <span class="breakdown-value">{{ completedTrip.estimated_cost_tnd }} TND</span>
            </div>
            <div class="breakdown-row">
              <span class="breakdown-label">Platform Commission (20%)</span>
              <span class="breakdown-value negative">-{{ (completedTrip.estimated_cost_tnd * 0.2).toFixed(2) }} TND</span>
            </div>
            <div class="breakdown-divider"></div>
            <div class="breakdown-row total">
              <span class="breakdown-label">Your Earnings</span>
              <span class="breakdown-value">{{ (completedTrip.estimated_cost_tnd * 0.8).toFixed(2) }} TND</span>
            </div>
          </div>

          <!-- Rate Rider -->
          <div class="rate-rider-section">
            <div class="rate-title">Rate {{ completedTrip.rider_name }}</div>
            <div class="star-rating">
              <button v-for="star in 5" :key="star" @click="riderRating = star" class="star-btn" :class="{ active: star <= riderRating }">
                {{ star <= riderRating ? '⭐' : '☆' }}
              </button>
            </div>
          </div>

          <!-- Done Button -->
          <button @click="closeCompletedModal" class="btn-done">
            Done
          </button>
        </div>
      </div>
    </transition>

    <!-- Loading Overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>{{ loadingMessage }}</p>
    </div>

    <!-- Waiting for Confirmation Notification -->
    <transition name="slide-down">
      <div v-if="showWaitingNotification" class="confirmation-notification">
        <div class="confirmation-content">
          <div class="confirmation-icon">
            <svg class="animate-spin h-6 w-6 text-taxini-yellow" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          <div class="confirmation-text">
            <h3 class="text-taxini-yellow font-bold text-base">Waiting for Rider Confirmation</h3>
            <p class="text-white text-sm mt-1">Please wait for the rider to confirm pickup before starting the trip.</p>
          </div>
          <button @click="showWaitingNotification = false; stopConfirmationPolling()" class="confirmation-close">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </transition>

    <!-- Custom Dialog -->
    <transition name="fade">
      <div v-if="showDialog" class="dialog-overlay" @click.self="dialogConfig.type === 'alert' ? dialogConfig.onConfirm() : (dialogConfig.onCancel ? dialogConfig.onCancel() : null)">
        <div class="dialog-box">
          <div class="dialog-header">
            <h3 class="dialog-title">{{ dialogConfig.title }}</h3>
          </div>
          <div class="dialog-body">
            <p class="dialog-message">{{ dialogConfig.message }}</p>
          </div>
          <div class="dialog-footer">
            <button 
              v-if="dialogConfig.type === 'confirm'" 
              @click="dialogConfig.onCancel ? dialogConfig.onCancel() : (showDialog = false)" 
              class="dialog-btn dialog-btn-cancel">
              {{ dialogConfig.cancelText }}
            </button>
            <button 
              @click="dialogConfig.onConfirm ? dialogConfig.onConfirm() : (showDialog = false)" 
              class="dialog-btn dialog-btn-confirm">
              {{ dialogConfig.confirmText }}
            </button>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { driverAPI } from '@/services/api'
import { useDriverMap } from '@/composables/driver/useDriverMap'
import { useDriverStatus } from '@/composables/driver/useDriverStatus'
import { useDriverTrip } from '@/composables/driver/useDriverTrip'
import { useDriverUI } from '@/composables/driver/useDriverUI'
import { useDriverRouting } from '@/composables/driver/useDriverRouting'
import { useNotificationStore } from '@/services/notificationStore'

const router = useRouter()
const authStore = useAuthStore()

// Driver account status
const accountStatus = ref('verified') // 'locked', 'verified', 'banned'
const isAccountRestricted = computed(() => accountStatus.value !== 'verified')

// Check driver account status from API
const checkApprovalStatus = async () => {
  try {
    // Check if token exists
    const token = localStorage.getItem('taxini_token')
    if (!token) {
      console.warn('⚠️ No authentication token found')
      window.location.href = '/login'
      return
    }
    
    console.log('🔍 Fetching driver profile...')
    const response = await driverAPI.getDriverProfile()
    if (response.success && response.driver) {
      accountStatus.value = response.driver.account_status
      console.log('✅ Driver account status:', accountStatus.value)
      console.log('📋 Driver info:', response.driver)
    }
  } catch (error) {
    console.error('❌ Failed to fetch driver profile:', error)
    console.error('   Error message:', error.message)
    
    // Check if it's an authentication error
    if (error.message?.includes('token') || error.message?.includes('Invalid') || error.message?.includes('Signature') || error.message?.includes('401') || error.message?.includes('Session expired')) {
      console.error('🔐 Authentication error - redirecting to login')
      // Token is invalid, redirect to login
      localStorage.removeItem('taxini_token')
      localStorage.removeItem('taxini_user')
      window.location.href = '/login'
      return
    }
    
    // For 500 errors or other issues, log but don't block
    console.warn('⚠️ API error but continuing with default status')
    // Default to verified if API fails for other reasons to avoid blocking legitimate drivers
    accountStatus.value = 'verified'
  }
}

// Notifications State
const showNotificationsPanel = ref(false)
const {
  notifications,
  unreadCount,
  markAsRead,
  clearAll: clearAllNotifications,
  notifyTripCompleted,
  notifyTripCancelled,
  notifyTripRequested,
  notifyEarningsUpdate
} = useNotificationStore()

// Alias for compatibility
const markAsRead_compat = markAsRead
const clearAllNotifications_compat = clearAllNotifications

// Confirmation Waiting State
const showWaitingNotification = ref(false)
let confirmationPollingInterval = null

// Dialog State
const showDialog = ref(false)
const dialogConfig = ref({
  title: '',
  message: '',
  type: 'alert', // 'alert' or 'confirm'
  confirmText: 'OK',
  cancelText: 'Cancel',
  onConfirm: null,
  onCancel: null
})

// Use Map Composable
const {
  mapContainer,
  map,
  driverLocation,
  gpsActive,
  isNavigating,
  remainingDistance,
  initMap,
  getCurrentLocation,
  calculateDistance,
  addPickupMarker,
  addDestinationMarker,
  removePickupMarker,
  removeDestinationMarker,
  fitMapToBounds,
  drawRoute,
  startNavigation,
  stopNavigation,
  clearRoute,
  stopLocationTracking,
  recenterToDriver
} = useDriverMap()

// Use Routing Composable
const {
  tripRoute,
  driverToPickupRoute,
  isRoutesVisible,
  routeMode,
  showTripRoutePreview,
  showDriverToPickupRoute,
  updateDriverToPickupRoute,
  hideDriverToPickupRoute,
  clearAllRoutes,
  toggleRouteVisibility
} = useDriverRouting(map, driverLocation)

// Modal content visibility for route preview
const isModalContentVisible = ref(true)

// Use Status Composable
const {
  isOnline,
  loading,
  loadingMessage,
  todayEarnings,
  todayTrips,
  onlineHours,
  startLocationUpdates,
  toggleOnlineStatus: baseToggleOnlineStatus,
  updateStats,
  cleanupStatus
} = useDriverStatus()

// Use Trip Composable
const {
  incomingRequest,
  currentTrip,
  countdown,
  countdownOffset,
  tripDuration,
  distanceTraveled,
  approachDistance,
  showCompletedModal,
  completedTrip,
  riderRating,
  isAcceptingTrip,
  initializeActiveTrip,
  startPollingTrips,
  stopPollingTrips,
  checkForTripRequests,
  startCountdown,
  showTripRequestNotification,
  acceptTrip: baseAcceptTrip,
  declineTrip: baseDeclineTrip,
  startTrip: baseStartTrip,
  completeTrip: baseCompleteTrip,
  closeCompletedModal,
  cleanupTrip,
  getInitials,
  formatDuration
} = useDriverTrip()

// Use UI Composable
const {
  showMenu,
  showBottomSheet,
  handleMapClick: baseHandleMapClick,
  handleBottomSheetTouchStart,
  handleBottomSheetTouchMove,
  handleBottomSheetTouchEnd,
  toggleBottomSheet,
  toggleMenu,
  goToHistory: baseGoToHistory,
  goToEarnings: baseGoToEarnings,
  goToSupport: baseGoToSupport,
  goToProfile: baseGoToProfile,
  logout: baseLogout
} = useDriverUI()

// Override unreadNotifications from composable with our computed value
const unreadNotifications = unreadCount

// Local state for UI controls
const showTripCard = ref(true) // Toggle for trip info card visibility

// Override handleMapClick to also hide the trip card
const handleMapClick = (event) => {
  baseHandleMapClick(event)
  // Hide trip card when clicking on map (only if there's an active trip)
  if (currentTrip.value && (currentTrip.value.status === 'accepted' || currentTrip.value.status === 'started')) {
    showTripCard.value = false
  }
}

// Map Methods
const recenterMap = () => {
  recenterToDriver()
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

// Notifications Methods
const toggleNotifications = () => {
  showNotificationsPanel.value = !showNotificationsPanel.value
}

// markAsRead is now from notification store
// Function signature: markAsRead(notificationId)

const clearAllNotifications_func = () => {
  clearAllNotifications()
  showNotificationsPanel.value = false
}

// Computed - Driver Info
const driverName = computed(() => authStore.user?.name || 'Driver')
const driverFirstName = computed(() => {
  const name = authStore.user?.name || 'Driver'
  return name.split(' ')[0]
})
const driverInitials = computed(() => {
  const name = authStore.user?.name || 'D'
  const names = name.split(' ')
  if (names.length >= 2) {
    return `${names[0][0]}${names[1][0]}`.toUpperCase()
  }
  return name[0].toUpperCase()
})
const driverPhone = computed(() => authStore.user?.phone || '')

// Wrapper functions to integrate composables
const toggleOnlineStatus = async () => {
  await baseToggleOnlineStatus(currentTrip, startPollingTrips, stopPollingTrips)
}

// Preview trip route (pickup → destination)
const previewTripRoute = async () => {
  if (!incomingRequest.value) {
    console.warn('❌ No trip request to preview')
    return
  }
  
  console.log('🗺️ Preview route clicked, current mode:', routeMode.value)
  
  if (routeMode.value === 'preview') {
    // Hide route and show modal again
    console.log('✅ Showing modal, hiding route')
    clearAllRoutes()
    routeMode.value = null
    isModalContentVisible.value = true
  } else {
    // Show route and hide modal
    console.log('✅ Showing route, hiding modal')
    console.log('Coordinates:', {
      pickup: `${incomingRequest.value.pickup_latitude}, ${incomingRequest.value.pickup_longitude}`,
      destination: `${incomingRequest.value.destination_latitude}, ${incomingRequest.value.destination_longitude}`
    })
    
    isModalContentVisible.value = false
    routeMode.value = 'preview'
    
    await showTripRoutePreview(
      {
        longitude: incomingRequest.value.pickup_longitude,
        latitude: incomingRequest.value.pickup_latitude
      },
      {
        longitude: incomingRequest.value.destination_longitude,
        latitude: incomingRequest.value.destination_latitude
      }
    )
    
    console.log('✅ Route preview completed')
  }
}

const acceptTrip = async () => {
  try {
    await baseAcceptTrip(driverLocation, calculateDistance, drawRoute)
    addPickupMarker(currentTrip.value.pickup_lat, currentTrip.value.pickup_lng)
    addDestinationMarker(currentTrip.value.destination_lat, currentTrip.value.destination_lng)
    
    // Show trip card when trip is accepted
    showTripCard.value = true
    
    // Reset modal visibility
    isModalContentVisible.value = true
    
    // Show driver-to-pickup route (blue) + keep trip route (yellow)
    await showDriverToPickupRoute({
      latitude: currentTrip.value.pickup_lat,
      longitude: currentTrip.value.pickup_lng
    })
    
    fitMapToBounds()
  } catch (error) {
    console.error('Accept trip error:', error)
    const errorMessage = error.message || 'Failed to accept trip. Please try again.'
    showAlertDialog('Error', errorMessage)
  }
}

const declineTrip = () => {
  baseDeclineTrip(() => {
    clearRoute()
    removePickupMarker()
    removeDestinationMarker()
    clearAllRoutes() // Clear all route layers
    isModalContentVisible.value = true // Reset modal visibility
    
    // Show confirmation notification
    window.$notification?.info(
      'You have declined the trip request. The rider has been notified.',
      { title: 'Trip Declined', priority: 'normal' }
    )
  })
}

const startTrip = async () => {
  showConfirmDialog(
    'Start Trip',
    'Have you picked up the rider? Ready to start the trip?',
    async () => {
      try {
        loading.value = true
        loadingMessage.value = 'Starting trip...'
        showDialog.value = false
        
        // Hide driver-to-pickup route, keep only trip route
        hideDriverToPickupRoute()
        
        await baseStartTrip(driverLocation, removePickupMarker, drawRoute)
        
        // Show trip card when trip starts
        showTripCard.value = true
      } catch (error) {
        console.error('Failed to start trip:', error)
        
        // Check if waiting for rider confirmation
        if (error.message === 'WAITING_FOR_CONFIRMATION') {
          // Notification already shown, start polling for confirmation
          startConfirmationPolling()
        } else {
          // Show the actual error message from backend for other errors
          const errorMessage = error.message || 'Failed to start trip. Please try again.'
          showAlertDialog('Cannot Start Trip', errorMessage)
        }
      } finally {
        loading.value = false
      }
    }
  )
}

// Dialog helpers
const showConfirmDialog = (title, message, onConfirm) => {
  dialogConfig.value = {
    title,
    message,
    type: 'confirm',
    confirmText: 'OK',
    cancelText: 'Cancel',
    onConfirm,
    onCancel: () => { showDialog.value = false }
  }
  showDialog.value = true
}

const showAlertDialog = (title, message) => {
  dialogConfig.value = {
    title,
    message,
    type: 'alert',
    confirmText: 'OK',
    onConfirm: () => { showDialog.value = false }
  }
  showDialog.value = true
}

// Confirmation polling logic
const startConfirmationPolling = () => {
  showWaitingNotification.value = true
  
  confirmationPollingInterval = setInterval(async () => {
    try {
      const { driverAPI } = await import('@/services/api')
      const response = await driverAPI.getActiveTrip()
      
      if (response.has_active_trip && response.trip) {
        // Check if rider confirmed pickup
        if (response.trip.rider_confirmed_pickup) {
          // Stop polling
          stopConfirmationPolling()
          showWaitingNotification.value = false
          
          // Update current trip with confirmation status - FORCE REACTIVITY
          if (currentTrip.value) {
            // Use Object.assign to trigger Vue reactivity
            Object.assign(currentTrip.value, {
              ...currentTrip.value,
              rider_confirmed_pickup: true
            })
            console.log('✅ Current trip updated with rider confirmation:', currentTrip.value.rider_confirmed_pickup)
          }
          
          console.log('✅ Rider confirmed pickup - Start Trip button now enabled')
          
          // Show success notification
          if (typeof window !== 'undefined' && window.$notification) {
            window.$notification.success(
              'You can now start the trip',
              { title: 'Rider Confirmed Pickup', priority: 'high' }
            )
          }
        }
      }
    } catch (error) {
      console.error('Error checking confirmation status:', error)
    }
  }, 2000) // Check every 2 seconds
}
          }
        }
      }
    } catch (error) {
      console.error('Error checking confirmation status:', error)
    }
  }, 2000) // Check every 2 seconds
}

const stopConfirmationPolling = () => {
  if (confirmationPollingInterval) {
    clearInterval(confirmationPollingInterval)
    confirmationPollingInterval = null
  }
}

// Dynamic card sizing for driver trip info
const tripCardStyle = computed(() => {
  if (!currentTrip.value) return {}
  
  const status = currentTrip.value.status
  const hasApproachFee = currentTrip.value.approach_fee_tnd > 0
  const isWaitingConfirmation = approachDistance.value <= 0.1 && !currentTrip.value.rider_confirmed_pickup
  
  let baseHeight = 480 // Base height for trip card
  
  // Add height for approach fee section
  if (hasApproachFee) baseHeight += 60
  
  // Add height for confirmation notice
  if (isWaitingConfirmation) baseHeight += 80
  
  // Adjust based on status
  if (status === 'started') baseHeight += 40 // Timer/duration display
  
  return {
    maxHeight: `${baseHeight}px`,
    transition: 'max-height 0.3s ease-in-out'
  }
})

const requestCardStyle = computed(() => {
  if (!incomingRequest.value) return {}
  
  return {
    maxHeight: '600px',
    transition: 'all 0.3s ease-in-out',
    animation: 'slideUpFade 0.4s ease-out'
  }
})

// Make functions available globally for composables
if (typeof window !== 'undefined') {
  window.showWaitingForConfirmation = () => {
    showWaitingNotification.value = true
  }
  
  window.showCancellationAlert = (message) => {
    showAlertDialog('Trip Cancelled', message || 'The rider has cancelled the trip')
    // Clear the trip state
    if (currentTrip.value) {
      cleanupTrip()
      clearRoute()
      removePickupMarker()
      removeDestinationMarker()
      stopNavigation()
    }
  }
}

const cancelCurrentTrip = async () => {
  showConfirmDialog(
    'Cancel Trip',
    'Are you sure you want to cancel this trip? The rider will be notified.',
    async () => {
      try {
        loading.value = true
        loadingMessage.value = 'Cancelling trip...'
        
        // Call backend to cancel the trip
        const response = await driverAPI.updateTripStatus(
          currentTrip.value.id,
          'cancelled',
          'Driver cancelled the trip'
        )
        
        console.log('✅ Trip cancelled successfully')
        
        // Clear current trip and map
        currentTrip.value = null
        clearRoute()
        removePickupMarker()
        removeDestinationMarker()
        
        showDialog.value = false
        // Show success message
        showAlertDialog('Success', 'Trip cancelled successfully')
      } catch (error) {
        console.error('❌ Failed to cancel trip:', error)
        showDialog.value = false
        showAlertDialog('Error', 'Failed to cancel trip. Please try again.')
      } finally {
        loading.value = false
      }
    }
  )
}

const openNavigation = async (lat, lng) => {
  console.log(`🧭 Drawing route to: ${lat}, ${lng}`)
  
  // Use the existing drawRoute function to show the route on the map
  if (driverLocation.value?.lat && driverLocation.value?.lng) {
    const destination = { lat, lng }
    await drawRoute(driverLocation.value, destination, true)
    console.log('✅ Route drawn on map')
    
    // Hide the card to show full map
    showTripCard.value = false
  } else {
    console.warn('⚠️ Driver location not available')
  }
}

const completeTrip = async () => {
  // Stop navigation when completing trip
  stopNavigation()
  
  showConfirmDialog(
    'Complete Trip',
    'Have you reached the destination? Ready to complete this trip?',
    async () => {
      try {
        loading.value = true
        loadingMessage.value = 'Completing trip...'
        showDialog.value = false
        const netEarnings = await baseCompleteTrip(() => {
          clearRoute()
          removePickupMarker()
          removeDestinationMarker()
          clearAllRoutes() // Clear all routing layers
        })
        todayEarnings.value += netEarnings
        todayTrips.value += 1
      } catch (error) {
        showAlertDialog('Error', 'Failed to complete trip. Please try again.')
      } finally {
        loading.value = false
      }
    }
  )
}

// Check for new trip requests periodically
const checkTrips = async () => {
  const hasRequest = await checkForTripRequests(isOnline)
  if (hasRequest && incomingRequest.value) {
    addPickupMarker(incomingRequest.value.pickup_lat, incomingRequest.value.pickup_lng)
    addDestinationMarker(incomingRequest.value.destination_lat, incomingRequest.value.destination_lng)
    fitMapToBounds()
    startCountdown(declineTrip)
    showTripRequestNotification()
  }
}

// Navigation wrappers
const showNotifications = () => baseShowNotifications(router)
const goToHistory = () => baseGoToHistory(router)
const goToEarnings = () => baseGoToEarnings(router)
const goToSupport = () => baseGoToSupport(router)
const goToProfile = () => baseGoToProfile(router)
const logout = () => baseLogout(router, authStore)

// Fetch initial driver status
const fetchInitialStatus = async () => {
  try {
    const response = await driverAPI.getStatus()
    if (response.success) {
      // Set online status based on backend data
      isOnline.value = response.status === 'online'
      console.log('✅ Initial driver status:', response.status)
    }
  } catch (error) {
    console.error('❌ Failed to fetch driver status:', error)
  }
}

// Set driver offline on window/tab close or session end
const handleBeforeUnload = async () => {
  try {
    // Use sendBeacon for reliability when page is closing
    const token = localStorage.getItem('taxini_token')
    if (token && authStore.isDriver) {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
      const blob = new Blob([JSON.stringify({ status: 'offline' })], { type: 'application/json' })
      navigator.sendBeacon(`${apiBaseUrl}/drivers/status`, blob)
      console.log('✅ Driver set to offline on window close')
    }
  } catch (error) {
    console.error('❌ Failed to set driver offline on close:', error)
  }
}

// Lifecycle
onMounted(async () => {
  // Add beforeunload event listener
  window.addEventListener('beforeunload', handleBeforeUnload)
  
  // Start map initialization immediately (non-blocking)
  initMap()
  
  // Parallelize independent API calls for faster loading
  const [statusResult, tripResult, earningsResult] = await Promise.allSettled([
    // Check approval and fetch status in parallel
    (async () => {
      await checkApprovalStatus()
      await fetchInitialStatus()
      
      // Force driver to offline status on mount
      if (isOnline.value) {
        try {
          await driverAPI.updateStatus('offline')
          isOnline.value = false
          stopPollingTrips()
          console.log('✅ Driver set to offline on dashboard mount')
        } catch (error) {
          console.error('❌ Failed to set offline on mount:', error)
        }
      }
    })(),
    
    // Check for active trip in parallel
    (async () => {
      try {
        return await initializeActiveTrip()
      } catch (error) {
        console.warn('⚠️ Could not check for active trip:', error.message)
        return false
      }
    })(),
    
    // Fetch today's earnings and trip stats
    (async () => {
      try {
        const response = await driverAPI.getEarnings('today')
        console.log('📊 Earnings API Response:', response)
        if (response.success) {
          todayEarnings.value = response.net_earnings || 0
          todayTrips.value = response.total_trips || 0
          console.log(`✅ Loaded today's stats: ${todayTrips.value} trips, ${todayEarnings.value.toFixed(2)} TND earnings`)
        } else {
          console.warn('⚠️ Earnings API returned success=false')
        }
      } catch (error) {
        console.error('❌ Failed to fetch earnings:', error.message, error)
      }
    })()
  ])
  
  // Get location (non-blocking, runs in background)
  getCurrentLocation(currentTrip, approachDistance, distanceTraveled)
  startLocationUpdates(driverLocation)
  
  // Check if we have an active trip from the parallel call
  const hasActiveTrip = tripResult.status === 'fulfilled' && tripResult.value
  
  // Restore trip map markers if there's an active trip
  if (hasActiveTrip && window.restoreDriverTripState) {
    setTimeout(() => {
      const tripData = window.restoreDriverTripState
      console.log('📍 Restoring driver trip markers on map')
      
      if (tripData.status === 'accepted' && tripData.pickup && map.value) {
        // Going to pickup - show route to pickup
        addPickupMarker(tripData.pickup.lat, tripData.pickup.lng)
        if (driverLocation.value?.lat && driverLocation.value?.lng) {
          drawRoute(
            { lat: driverLocation.value.lat, lng: driverLocation.value.lng },
            { lat: tripData.pickup.lat, lng: tripData.pickup.lng }
          )
        }
      } else if (tripData.status === 'started' && tripData.destination && map.value) {
        // Trip started - show route to destination
        addDestinationMarker(tripData.destination.lat, tripData.destination.lng)
        if (driverLocation.value?.lat && driverLocation.value?.lng) {
          drawRoute(
            { lat: driverLocation.value.lat, lng: driverLocation.value.lng },
            { lat: tripData.destination.lat, lng: tripData.destination.lng }
          )
        }
      }
    }, 500)
  }
  
  // Start polling for trip requests if driver is online and no active trip
  if (isOnline.value && !hasActiveTrip) {
    console.log('▶️ Starting trip request polling (driver is online)')
    startPollingTrips(isOnline)
  }
})

onUnmounted(async () => {
  // Remove beforeunload event listener
  window.removeEventListener('beforeunload', handleBeforeUnload)
  
  // Set driver offline when component unmounts
  try {
    if (authStore.isDriver) {
      await driverAPI.updateStatus('offline')
      console.log('✅ Driver set to offline on component unmount')
    }
  } catch (error) {
    console.error('❌ Failed to set driver offline on unmount:', error)
  }
  
  stopLocationTracking()
  cleanupStatus()
  cleanupTrip()
  stopConfirmationPolling()
  if (map.value) {
    map.value.remove()
  }
})
</script>

<style scoped src="./DriverDashboard.css"></style>
