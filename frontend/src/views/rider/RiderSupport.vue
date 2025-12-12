<template>
  <div class="support-container">
    <!-- Header -->
    <div class="support-header">
      <button @click="goBack" class="btn-back">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <h1 class="header-title">Support</h1>
      <div class="header-spacer"></div>
    </div>

    <!-- Support Content -->
    <div class="support-content">
      <!-- Contact Cards -->
      <div class="contact-section">
        <h2 class="section-title">Contact Us</h2>
        <div class="contact-cards">
          <a href="tel:+21612345678" class="contact-card">
            <div class="contact-icon phone">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
            </div>
            <div class="contact-info">
              <div class="contact-label">Phone Support</div>
              <div class="contact-value">+216 12 345 678</div>
            </div>
          </a>

          <a href="mailto:support@taxini.tn" class="contact-card">
            <div class="contact-icon email">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <div class="contact-info">
              <div class="contact-label">Email Support</div>
              <div class="contact-value">support@taxini.tn</div>
            </div>
          </a>
        </div>
      </div>

      <!-- Create Ticket Section -->
      <div class="create-ticket-section">
        <div class="section-header">
          <h2 class="section-title">Create Support Ticket</h2>
          <button 
            v-if="!showCreateForm" 
            @click="showCreateForm = true" 
            class="btn-toggle-form"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            New Ticket
          </button>
        </div>

        <transition name="expand">
          <div v-if="showCreateForm" class="ticket-form">
            <div class="form-group">
              <label class="form-label">Subject *</label>
              <input 
                v-model="newTicket.subject" 
                type="text" 
                placeholder="Brief description of your issue"
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Category *</label>
              <select v-model="newTicket.category" class="form-select">
                <option value="">Select a category</option>
                <option value="trip">Trip Issue</option>
                <option value="payment">Payment Issue</option>
                <option value="driver">Driver Issue</option>
                <option value="app">App Issue</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Description *</label>
              <textarea 
                v-model="newTicket.description" 
                placeholder="Describe your issue in detail..."
                rows="5"
                class="form-textarea"
              ></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">Attachment (Optional)</label>
              <div class="file-upload-area" @click="triggerFileUpload">
                <input 
                  ref="fileInput" 
                  type="file" 
                  accept="image/*,.pdf" 
                  @change="handleFileUpload"
                  class="hidden-file-input"
                />
                <svg xmlns="http://www.w3.org/2000/svg" class="upload-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <div v-if="!newTicket.attachment" class="upload-text">
                  <span class="upload-primary">Click to upload</span>
                  <span class="upload-secondary">PNG, JPG or PDF (max 5MB)</span>
                </div>
                <div v-else class="file-name">{{ newTicket.attachment.name }}</div>
              </div>
            </div>

            <div class="form-actions">
              <button @click="cancelCreateTicket" class="btn-cancel">
                Cancel
              </button>
              <button 
                @click="createTicket" 
                :disabled="!isFormValid || isSubmittingTicket"
                class="btn-submit"
              >
                <template v-if="!isSubmittingTicket">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                  Submit Ticket
                </template>
                <template v-else>
                  <div class="loading-spinner"></div>
                  Submitting...
                </template>
              </button>
            </div>
          </div>
        </transition>
      </div>

      <!-- My Tickets Section -->
      <div class="tickets-section">
        <h2 class="section-title">My Tickets</h2>

        <!-- Filter Tabs -->
        <div class="filter-tabs">
          <button 
            @click="filterStatus = 'all'" 
            class="filter-tab"
            :class="{ active: filterStatus === 'all' }"
          >
            All
          </button>
          <button 
            @click="filterStatus = 'open'" 
            class="filter-tab"
            :class="{ active: filterStatus === 'open' }"
          >
            Open
          </button>
          <button 
            @click="filterStatus = 'in_progress'" 
            class="filter-tab"
            :class="{ active: filterStatus === 'in_progress' }"
          >
            In Progress
          </button>
          <button 
            @click="filterStatus = 'resolved'" 
            class="filter-tab"
            :class="{ active: filterStatus === 'resolved' }"
          >
            Resolved
          </button>
        </div>

        <!-- Tickets List -->
        <div v-if="loading" class="empty-state">
          <div class="loading-spinner"></div>
          <p class="empty-text">Loading tickets...</p>
        </div>

        <div v-else-if="error" class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" class="empty-icon text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="empty-text">{{ error }}</p>
          <button @click="fetchTickets" class="btn-create-first">
            Retry
          </button>
        </div>

        <div v-else-if="filteredTickets.length === 0" class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
          <p class="empty-text">No tickets found</p>
          <button @click="showCreateForm = true" class="btn-create-first">
            Create Your First Ticket
          </button>
        </div>

        <div v-else class="tickets-list">
          <div 
            v-for="ticket in filteredTickets" 
            :key="ticket.id"
            class="ticket-card"
            :class="{ expanded: expandedTicket === ticket.id }"
            @click="toggleTicket(ticket.id)"
          >
            <div class="ticket-header">
              <div class="ticket-main">
                <div class="ticket-title">{{ ticket.subject }}</div>
                <div class="ticket-meta">
                  <span class="ticket-id">#{{ ticket.id }}</span>
                  <span class="ticket-divider">•</span>
                  <span class="ticket-category">{{ getCategoryLabel(ticket.category) }}</span>
                  <span class="ticket-divider">•</span>
                  <span class="ticket-date">{{ ticket.createdAt }}</span>
                </div>
              </div>
              <div class="ticket-status-wrapper">
                <span class="ticket-status" :class="ticket.status">
                  {{ getStatusLabel(ticket.status) }}
                </span>
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  class="expand-icon"
                  :class="{ rotated: expandedTicket === ticket.id }"
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>

            <transition name="expand-content">
              <div v-if="expandedTicket === ticket.id" class="ticket-details" @click.stop>
                <div class="ticket-description">
                  <div class="detail-label">Description</div>
                  <p class="detail-text">{{ ticket.description }}</p>
                </div>

                <div v-if="ticket.attachment" class="ticket-attachment">
                  <div class="detail-label">Attachment</div>
                  <a :href="ticket.attachment.url" class="attachment-link" target="_blank">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                    </svg>
                    {{ ticket.attachment.name }}
                  </a>
                </div>

                <div v-if="ticket.responses && ticket.responses.length > 0" class="ticket-responses">
                  <div class="detail-label">Admin Responses</div>
                  <div 
                    v-for="response in ticket.responses" 
                    :key="response.id"
                    class="response-item"
                  >
                    <div class="response-header">
                      <div class="response-author">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M12 2a5 5 0 100 10 5 5 0 000-10zm0 12c-5.33 0-8 2.67-8 4v2h16v-2c0-1.33-2.67-4-8-4z" />
                        </svg>
                        {{ response.author }}
                      </div>
                      <div class="response-date">{{ response.date }}</div>
                    </div>
                    <p class="response-text">{{ response.message }}</p>
                  </div>
                </div>

                <div v-else class="no-responses">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Waiting for admin response...</span>
                </div>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ticketAPI } from '@/services/api'

const router = useRouter()
const showCreateForm = ref(false)
const fileInput = ref(null)
const filterStatus = ref('all')
const expandedTicket = ref(null)
const loading = ref(false)
const error = ref(null)
const isSubmittingTicket = ref(false)

const newTicket = ref({
  subject: '',
  category: '',
  description: '',
  attachment: null,
  priority: 'medium'
})

// Backend tickets data
const tickets = ref([])

// Fetch tickets from backend
const fetchTickets = async () => {
  loading.value = true
  error.value = null
  
  try {
    console.log('📋 Fetching support tickets from backend...')
    
    const response = await ticketAPI.getTickets()
    
    console.log('✅ Tickets response:', response)
    
    if (response.data) {
      // Map backend response to frontend format
      tickets.value = response.data.map(ticket => ({
        id: ticket.id,
        subject: ticket.title,
        category: ticket.issue_at || 'other',
        description: ticket.content,
        status: ticket.status,
        createdAt: formatTimeAgo(ticket.created_at),
        attachment: null, // Backend might not support attachments yet
        responses: ticket.admin_response ? [
          {
            id: 1,
            author: 'Admin Support',
            date: formatTimeAgo(ticket.updated_at),
            message: ticket.admin_response
          }
        ] : []
      }))
      
      console.log(`✅ Loaded ${tickets.value.length} tickets`)
    } else {
      tickets.value = []
    }
  } catch (err) {
    console.error('❌ Error fetching tickets:', err)
    error.value = err.message || 'Failed to load tickets'
    tickets.value = []
  } finally {
    loading.value = false
  }
}

// Format time ago (simple implementation)
const formatTimeAgo = (dateString) => {
  if (!dateString) return 'Unknown'
  
  const date = new Date(dateString)
  const now = new Date()
  const seconds = Math.floor((now - date) / 1000)
  
  if (seconds < 60) return 'Just now'
  if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`
  if (seconds < 604800) return `${Math.floor(seconds / 86400)} days ago`
  
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const filteredTickets = computed(() => {
  if (filterStatus.value === 'all') {
    return tickets.value
  }
  return tickets.value.filter(t => t.status === filterStatus.value)
})

const isFormValid = computed(() => {
  return newTicket.value.subject.trim() !== '' &&
         newTicket.value.category !== '' &&
         newTicket.value.description.trim() !== ''
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
    newTicket.value.attachment = file
  }
}

const createTicket = async () => {
  if (!isFormValid.value) return

  isSubmittingTicket.value = true
  
  try {
    console.log('📝 Creating support ticket...')
    
    // Prepare ticket data for backend
    const ticketData = {
      title: newTicket.value.subject,
      content: newTicket.value.description,
      issue_at: newTicket.value.category,
      priority: newTicket.value.priority || 'medium'
    }
    
    const response = await ticketAPI.createTicket(ticketData)
    
    console.log('✅ Ticket created:', response)
    
    // Refresh tickets list
    await fetchTickets()
    
    // Reset form
    newTicket.value = {
      subject: '',
      category: '',
      description: '',
      attachment: null,
      priority: 'medium'
    }
    showCreateForm.value = false
    
    // Show success message (you can add a toast notification here)
    alert('Support ticket created successfully!')
    
  } catch (err) {
    console.error('❌ Error creating ticket:', err)
    alert(`Failed to create ticket: ${err.message}`)
  } finally {
    isSubmittingTicket.value = false
  }
}

const cancelCreateTicket = () => {
  newTicket.value = {
    subject: '',
    category: '',
    description: '',
    attachment: null
  }
  showCreateForm.value = false
}

const toggleTicket = (ticketId) => {
  expandedTicket.value = expandedTicket.value === ticketId ? null : ticketId
}

const getCategoryLabel = (category) => {
  const labels = {
    trip: 'Trip Issue',
    payment: 'Payment Issue',
    driver: 'Driver Issue',
    app: 'App Issue',
    other: 'Other'
  }
  return labels[category] || category
}

const getStatusLabel = (status) => {
  const labels = {
    open: 'Open',
    in_progress: 'In Progress',
    resolved: 'Resolved',
    closed: 'Closed'
  }
  return labels[status] || status
}

// Lifecycle
onMounted(() => {
  fetchTickets()
})
</script>

<style scoped src="./RiderSupport.css"></style>
