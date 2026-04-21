const BASE = '/api'

// credentials: 'include' ensures cookies are sent with every request.
// For same-origin requests (our setup) this is the default, but explicit is clearer.
const opts = { credentials: 'include' }

export async function ensureSession() {
  const res = await fetch(`${BASE}/session`, opts)
  if (res.ok) return res.json()
  // No session cookie yet — create one. The browser stores the Set-Cookie automatically.
  const created = await fetch(`${BASE}/session`, { ...opts, method: 'POST' })
  return created.json()
}

export async function fetchTopics() {
  const res = await fetch(`${BASE}/topics`, opts)
  return res.json()
}

export async function fetchTopic(slug) {
  const res = await fetch(`${BASE}/topics/${slug}`, opts)
  return res.json()
}

export async function visitTopic(slug) {
  const res = await fetch(`${BASE}/session/visit/${slug}`, { ...opts, method: 'POST' })
  return res.json()
}

export async function completeTopic(slug) {
  const res = await fetch(`${BASE}/session/complete/${slug}`, { ...opts, method: 'POST' })
  return res.json()
}
