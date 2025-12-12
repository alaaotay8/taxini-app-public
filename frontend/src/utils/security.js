/**
 * Security utilities for frontend input validation and sanitization
 */

/**
 * Sanitize user input to prevent XSS attacks
 * @param {string} input - Raw user input
 * @returns {string} - Sanitized input
 */
export const sanitizeInput = (input) => {
  if (typeof input !== 'string') return input
  
  // HTML entity encoding
  const div = document.createElement('div')
  div.textContent = input
  return div.innerHTML
}

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} - True if valid
 */
export const isValidEmail = (email) => {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  return emailRegex.test(email) && email.length <= 254
}

/**
 * Validate phone number format (E.164)
 * @param {string} phone - Phone number to validate
 * @returns {boolean} - True if valid
 */
export const isValidPhone = (phone) => {
  const phoneRegex = /^\+?1?\d{9,15}$/
  return phoneRegex.test(phone)
}

/**
 * Validate name (letters, spaces, hyphens, apostrophes only)
 * @param {string} name - Name to validate
 * @returns {boolean} - True if valid
 */
export const isValidName = (name) => {
  if (!name || name.length < 2 || name.length > 100) return false
  const nameRegex = /^[a-zA-Z\u0600-\u06FF\s'-]+$/
  return nameRegex.test(name) && !name.includes('  ')
}

/**
 * Validate coordinates
 * @param {number} lat - Latitude
 * @param {number} lng - Longitude
 * @returns {boolean} - True if valid
 */
export const isValidCoordinates = (lat, lng) => {
  return (
    typeof lat === 'number' &&
    typeof lng === 'number' &&
    lat >= -90 &&
    lat <= 90 &&
    lng >= -180 &&
    lng <= 180
  )
}

/**
 * Remove potentially dangerous content from strings
 * @param {string} str - String to clean
 * @returns {string} - Cleaned string
 */
export const removeScriptTags = (str) => {
  if (typeof str !== 'string') return str
  return str.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
}

/**
 * Limit string length safely
 * @param {string} str - String to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} - Truncated string
 */
export const truncateString = (str, maxLength) => {
  if (typeof str !== 'string') return ''
  if (str.length <= maxLength) return str
  return str.substring(0, maxLength)
}

/**
 * Validate JWT token format (basic check)
 * @param {string} token - Token to validate
 * @returns {boolean} - True if format is valid
 */
export const isValidJWT = (token) => {
  if (!token || typeof token !== 'string') return false
  const parts = token.split('.')
  return parts.length === 3
}

/**
 * Check if token is expired (client-side check)
 * @param {string} token - JWT token
 * @returns {boolean} - True if expired
 */
export const isTokenExpired = (token) => {
  if (!isValidJWT(token)) return true
  
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    if (!payload.exp) return false
    
    const now = Date.now() / 1000
    return payload.exp < now
  } catch (e) {
    return true
  }
}

/**
 * Safe JSON parse with fallback
 * @param {string} jsonString - JSON string to parse
 * @param {*} fallback - Fallback value if parse fails
 * @returns {*} - Parsed object or fallback
 */
export const safeJSONParse = (jsonString, fallback = null) => {
  try {
    return JSON.parse(jsonString)
  } catch (e) {
    console.warn('JSON parse error:', e)
    return fallback
  }
}

/**
 * Validate URL format
 * @param {string} url - URL to validate
 * @returns {boolean} - True if valid
 */
export const isValidURL = (url) => {
  try {
    const urlObj = new URL(url)
    return urlObj.protocol === 'http:' || urlObj.protocol === 'https:'
  } catch (e) {
    return false
  }
}

/**
 * Rate limiter for client-side actions
 */
export class RateLimiter {
  constructor(maxAttempts = 5, windowMs = 60000) {
    this.maxAttempts = maxAttempts
    this.windowMs = windowMs
    this.attempts = new Map()
  }

  /**
   * Check if action is allowed
   * @param {string} key - Unique key for the action
   * @returns {boolean} - True if allowed
   */
  isAllowed(key) {
    const now = Date.now()
    const attempts = this.attempts.get(key) || []
    
    // Remove old attempts outside the window
    const validAttempts = attempts.filter(time => now - time < this.windowMs)
    
    if (validAttempts.length >= this.maxAttempts) {
      return false
    }
    
    // Record new attempt
    validAttempts.push(now)
    this.attempts.set(key, validAttempts)
    
    return true
  }

  /**
   * Reset attempts for a key
   * @param {string} key - Key to reset
   */
  reset(key) {
    this.attempts.delete(key)
  }
}

export default {
  sanitizeInput,
  isValidEmail,
  isValidPhone,
  isValidName,
  isValidCoordinates,
  removeScriptTags,
  truncateString,
  isValidJWT,
  isTokenExpired,
  safeJSONParse,
  isValidURL,
  RateLimiter
}
