

const BASE_URL = '/api'
const API_KEY = 'dev-secret-change-in-prod'

const headers = {
  'Content-Type': 'application/json',
  'X-API-Key': API_KEY,
}

export async function fetchDashboardStats() {
  const res = await fetch(`${BASE_URL}/dashboard/stats`, { headers })
  if (!res.ok) throw new Error(`Stats error: ${res.status}`)
  return res.json()
}

export async function fetchEmployees() {
  const res = await fetch(`${BASE_URL}/employees`, { headers })
  if (!res.ok) throw new Error(`Employees error: ${res.status}`)
  return res.json()
}

export async function fetchExplanation(anonId) {
  const res = await fetch(`${BASE_URL}/explain/${anonId}`, { headers })
  if (!res.ok) throw new Error(`Explain error: ${res.status}`)
  return res.json()
}

export async function predictEmployee(features) {
  const res = await fetch(`${BASE_URL}/predict`, {
    method: 'POST',
    headers,
    body: JSON.stringify(features),
  })
  if (!res.ok) throw new Error(`Predict error: ${res.status}`)
  return res.json()
}

export async function fetchMetrics() {
  const res = await fetch(`${BASE_URL}/metrics`, { headers })
  if (!res.ok) throw new Error(`Metrics error: ${res.status}`)
  return res.json()
}