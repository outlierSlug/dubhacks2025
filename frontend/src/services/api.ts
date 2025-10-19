const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

// Player/User API
export async function signupUser(data: {
  username: string
  password: string
  id: number
  fname: string
  lname: string
  rating: number
  email: string
  phone: string
  bday: string // ISO date string
  gender: number // 1=male, 2=female, 3=other
}) {
  const res = await fetch(`${API_BASE}/api/players`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Signup failed')
  }
  return res.json()
}

export async function loginUser(username: string, password: string) {
  const res = await fetch(
    `${API_BASE}/api/players?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
  )
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Login failed')
  }
  return res.json()
}

// Booking/Event API
export async function createEvent(data: {
  id: number
  start_time: string // ISO datetime
  max_players: number
  gender: number
  court: number
  description: string
}) {
  const res = await fetch(`${API_BASE}/api/events`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Event creation failed')
  }
  return res.json()
}

export async function getMyEvents(playerId: number) {
  const res = await fetch(`${API_BASE}/api/events/mine/${playerId}`)
  if (!res.ok) throw new Error('Failed to fetch my events')
  return res.json()
}

export async function getAllEvents() {
  const res = await fetch(`${API_BASE}/api/events`)
  if (!res.ok) throw new Error('Failed to fetch events')
  return res.json()
}

export async function addPlayerToEvent(eventId: number, playerId: number) {
  const res = await fetch(`${API_BASE}/api/events/${eventId}/add_player`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ player_id: playerId }),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Failed to join event')
  }
  return res.json()
}

export async function removePlayerFromEvent(eventId: number, playerId: number) {
  const res = await fetch(`${API_BASE}/api/events/${eventId}/remove_player`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ player_id: playerId }),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Failed to cancel booking')
  }
  return res.json()
}

export async function getRecommendations(playerId: number) {
  const res = await fetch(`${API_BASE}/api/recommendations/${playerId}`)
  if (!res.ok) throw new Error('Failed to get recommendations')
  return res.json()
}