<template>
  <div class="driver-support">
    <!-- Header -->
    <header class="support-header">
      <button @click="goBack" class="btn-back">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <h1 class="header-title">Support & Help</h1>
      <div class="header-spacer"></div>
    </header>

    <!-- Content -->
    <div class="support-content">
      
      <!-- Quick Contact -->
      <div class="contact-section">
        <h2 class="section-title">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
          </svg>
          Contact Support
        </h2>
        <div class="contact-cards">
          <a :href="`tel:${supportPhone}`" class="contact-card">
            <div class="contact-icon phone-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
            </div>
            <div class="contact-info">
              <div class="contact-label">Call Us</div>
              <div class="contact-value">{{ supportPhone }}</div>
            </div>
          </a>
          <a :href="`mailto:${supportEmail}`" class="contact-card">
            <div class="contact-icon email-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <div class="contact-info">
              <div class="contact-label">Email Us</div>
              <div class="contact-value">{{ supportEmail }}</div>
            </div>
          </a>
        </div>
        <div class="operating-hours">
          <span class="hours-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </span>
          <span>Available: Mon - Sun, 24/7</span>
        </div>
      </div>

      <!-- Account Verification Status -->
      <div class="verification-section" v-if="!allDocumentsVerified">
        <h2 class="section-title">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          Verification Status
        </h2>
        <div class="verification-card">
          <div class="verification-item" v-for="doc in documents" :key="doc.type">
            <div class="doc-info">
              <span class="doc-icon">
                <!-- ID Card Icon -->
                <svg v-if="doc.type === 'id'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
                </svg>
                <!-- Driver License Icon -->
                <svg v-else-if="doc.type === 'license'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <!-- Vehicle Registration Icon -->
                <svg v-else-if="doc.type === 'vehicle'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
              </span>
              <span class="doc-name">{{ doc.name }}</span>
            </div>
            <span class="verification-status" :class="doc.status">
              {{ formatStatus(doc.status) }}
            </span>
          </div>
          <div class="verification-actions" v-if="hasPendingDocs">
            <p class="verification-message">
              Some documents require your attention. Please upload or update pending documents.
            </p>
            <button class="btn-upload" @click="goToProfile">
              Upload Documents
            </button>
          </div>
        </div>
      </div>

      <!-- Create Ticket Form -->
      <div class="create-ticket-section">
        <h2 class="section-title">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          Create Support Ticket
        </h2>
        <form @submit.prevent="submitTicket" class="ticket-form">
          <div class="form-group">
            <label class="form-label">Category</label>
            <select v-model="newTicket.category" class="form-select" required>
              <option value="">Select category</option>
              <option value="trip_issue">Trip Issue</option>
              <option value="payment">Payment Problem</option>
              <option value="account">Account Issue</option>
              <option value="technical">Technical Problem</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Subject</label>
            <input 
              v-model="newTicket.subject" 
              type="text" 
              class="form-input" 
              placeholder="Brief description of your issue"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">Description</label>
            <textarea 
              v-model="newTicket.description" 
              class="form-textarea" 
              placeholder="Please provide detailed information about your issue..."
              rows="5"
              required
            ></textarea>
          </div>

          <div class="form-group">
            <label class="form-label">Attachments (Optional)</label>
            <div class="file-upload-area">
              <input 
                type="file" 
                @change="handleFileUpload" 
                accept="image/*,.pdf"
                multiple
                class="file-input"
                id="file-input"
              />
              <label for="file-input" class="file-upload-label">
                <span class="upload-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </span>
                <span>Click to upload files</span>
                <span class="upload-hint">Images or PDF only</span>
              </label>
              <div v-if="newTicket.attachments.length > 0" class="uploaded-files">
                <div v-for="(file, index) in newTicket.attachments" :key="index" class="file-item">
                  <span class="file-name">{{ file.name }}</span>
                  <button type="button" @click="removeFile(index)" class="btn-remove-file">
                    ✕
                  </button>
                </div>
              </div>
            </div>
          </div>

          <button type="submit" class="btn-submit" :disabled="submitting">
            {{ submitting ? 'Submitting...' : 'Submit Ticket' }}
          </button>
        </form>
      </div>

      <!-- My Tickets -->
      <div class="my-tickets-section">
        <h2 class="section-title">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
          </svg>
          My Tickets
        </h2>
        
        <!-- Loading -->
        <div v-if="loadingTickets" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Loading tickets...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="tickets.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
            </svg>
          </div>
          <p class="empty-text">No support tickets yet</p>
        </div>

        <!-- Tickets List -->
        <div v-else class="tickets-list">
          <div 
            v-for="ticket in tickets" 
            :key="ticket.id" 
            class="ticket-card"
            :class="{ expanded: expandedTicketId === ticket.id }"
            @click="toggleTicket(ticket.id)"
          >
            <div class="ticket-header">
              <div class="ticket-id-category">
                <span class="ticket-id">{{ ticket.id }}</span>
                <span class="ticket-category">{{ formatCategory(ticket.category) }}</span>
              </div>
              <span class="ticket-status-badge" :class="ticket.status">
                {{ formatTicketStatus(ticket.status) }}
              </span>
            </div>
            
            <div class="ticket-subject">{{ ticket.subject }}</div>
            
            <div class="ticket-meta">
              <span class="ticket-date">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                  <line x1="16" y1="2" x2="16" y2="6"/>
                  <line x1="8" y1="2" x2="8" y2="6"/>
                  <line x1="3" y1="10" x2="21" y2="10"/>
                </svg>
                {{ formatDate(ticket.created_at) }}
              </span>
              <span class="ticket-expand">
                {{ expandedTicketId === ticket.id ? '▲' : '▼' }}
              </span>
            </div>

            <!-- Expanded Details -->
            <div v-if="expandedTicketId === ticket.id" class="ticket-details">
              <div class="detail-divider"></div>
              <div class="ticket-description">
                <strong>Description:</strong>
                <p>{{ ticket.description }}</p>
              </div>
              
              <div v-if="ticket.attachments && ticket.attachments.length > 0" class="ticket-attachments">
                <strong>Attachments:</strong>
                <div class="attachments-list">
                  <a 
                    v-for="(file, index) in ticket.attachments" 
                    :key="index" 
                    :href="file.url" 
                    target="_blank"
                    class="attachment-link"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                    </svg>
                    {{ file.name }}
                  </a>
                </div>
              </div>

              <div v-if="ticket.response" class="ticket-response">
                <strong>Support Response:</strong>
                <p>{{ ticket.response }}</p>
                <span class="response-date">{{ formatDate(ticket.updated_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import './DriverSupport.css'

const router = useRouter()

// Support Contact Info
const supportPhone = ref('+1-800-TAXINI')
const supportEmail = ref('support@taxini.com')

// Document Verification Status
const documents = ref([
  { type: 'id', name: 'National ID', status: 'verified' },
  { type: 'license', name: "Driver's License", status: 'verified' },
  { type: 'vehicle', name: 'Vehicle Registration', status: 'pending' }
])

const allDocumentsVerified = computed(() => 
  documents.value.every(doc => doc.status === 'verified')
)

const hasPendingDocs = computed(() => 
  documents.value.some(doc => doc.status === 'pending' || doc.status === 'rejected')
)

// New Ticket Form
const newTicket = ref({
  category: '',
  subject: '',
  description: '',
  attachments: []
})

const submitting = ref(false)

const handleFileUpload = (event) => {
  const files = Array.from(event.target.files)
  newTicket.value.attachments.push(...files)
}

const removeFile = (index) => {
  newTicket.value.attachments.splice(index, 1)
}

const submitTicket = async () => {
  submitting.value = true
  
  // Simulate API call
  setTimeout(() => {
    // Create new ticket
    const ticket = {
      id: `#TKT${String(tickets.value.length + 1).padStart(4, '0')}`,
      category: newTicket.value.category,
      subject: newTicket.value.subject,
      description: newTicket.value.description,
      status: 'open',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      attachments: newTicket.value.attachments.map(file => ({
        name: file.name,
        url: URL.createObjectURL(file)
      }))
    }
    
    tickets.value.unshift(ticket)
    
    // Reset form
    newTicket.value = {
      category: '',
      subject: '',
      description: '',
      attachments: []
    }
    
    submitting.value = false
    alert('Ticket submitted successfully!')
  }, 1500)
}

// My Tickets
const loadingTickets = ref(false)
const expandedTicketId = ref(null)

const tickets = ref([
  {
    id: '#TKT0001',
    category: 'payment',
    subject: 'Missing payment for trip #TRP123',
    description: 'I completed a trip yesterday but the payment is not showing in my earnings. The trip ID was TRP123 and the amount was $45.',
    status: 'in_progress',
    created_at: '2024-01-15T10:30:00Z',
    updated_at: '2024-01-15T14:20:00Z',
    response: 'We are investigating this issue and will update your account within 24 hours. Thank you for your patience.',
    attachments: []
  },
  {
    id: '#TKT0002',
    category: 'technical',
    subject: 'App crashes when viewing trip history',
    description: 'The app keeps crashing whenever I try to view my trip history from last month. I have tried restarting the app multiple times.',
    status: 'resolved',
    created_at: '2024-01-10T08:15:00Z',
    updated_at: '2024-01-12T16:00:00Z',
    response: 'This issue has been fixed in the latest app update (v2.3.1). Please update your app from the store.',
    attachments: []
  }
])

const toggleTicket = (ticketId) => {
  expandedTicketId.value = expandedTicketId.value === ticketId ? null : ticketId
}

// Formatting Functions
const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatCategory = (category) => {
  const categories = {
    trip_issue: 'Trip Issue',
    payment: 'Payment',
    account: 'Account',
    technical: 'Technical',
    other: 'Other'
  }
  return categories[category] || category
}

const formatTicketStatus = (status) => {
  const statuses = {
    open: 'Open',
    in_progress: 'In Progress',
    resolved: 'Resolved',
    closed: 'Closed'
  }
  return statuses[status] || status
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  })
}

const goBack = () => {
  router.push('/driver/dashboard')
}

const goToProfile = () => {
  router.push('/driver/profile')
}
</script>
