// Quick fix script - Run this in browser console
// OR add a "Clear Auth" button in your app temporarily

// Clear all auth data
localStorage.removeItem('taxini_token')
localStorage.removeItem('taxini_phone')
localStorage.removeItem('taxini_user')

// Reload page
window.location.href = '/login'

console.log('✅ Auth cleared! Please login again.')
