/**
 * TMA API utilities for communicating with backend
 * Automatically includes Telegram init data in requests
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://nonpalliatively-jellylike-delorse.ngrok-free.dev'
/**
 * Make authenticated API request with TMA data
 */
export const tmaFetch = async (endpoint, options = {}) => {
  const initData = localStorage.getItem('tmaInitData') || ''
  const telegramUserId = localStorage.getItem('telegramUserId') || ''

  const headers = {
    'Content-Type': 'application/json',
    'X-Telegram-Init-Data': initData,
    'X-Telegram-User-Id': telegramUserId,
    ...options.headers
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || `API error: ${response.status}`)
  }

  return response.json()
}

/**
 * Get user info from backend (verified via TMA)
 */
export const getTmaUserInfo = () => {
  return tmaFetch('/api/tma/user')
}

/**
 * Get list of hostels (with user context from TMA)
 */
export const getHostels = () => {
  return tmaFetch('/api/hostels')
}

/**
 * Get user's hostels (host role)
 */
export const getUserHostels = () => {
  return tmaFetch('/api/hostels/my')
}

/**
 * Create a new hostel
 */
export const createHostel = (data) => {
  return tmaFetch('/api/hostels', {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

/**
 * Update hostel
 */
export const updateHostel = (hostelId, data) => {
  return tmaFetch(`/api/hostels/${hostelId}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  })
}

/**
 * Send support message
 */
export const sendSupportMessage = (message) => {
  return tmaFetch('/api/support', {
    method: 'POST',
    body: JSON.stringify({ message })
  })
}

/**
 * Get support messages history
 */
export const getSupportHistory = () => {
  return tmaFetch('/api/support/history')
}

/**
 * Report a hostel
 */
export const reportHostel = (hostelId, reason) => {
  return tmaFetch(`/api/hostels/${hostelId}/report`, {
    method: 'POST',
    body: JSON.stringify({ reason })
  })
}
