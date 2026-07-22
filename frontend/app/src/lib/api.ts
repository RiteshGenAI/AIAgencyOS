import type { TokenResponse } from '../types'

const isDev = (import.meta as any).env?.DEV
const baseURL = (import.meta as any).env?.VITE_API_BASE_URL || (isDev ? 'http://localhost:8000/api/v1' : '/api/v1')

export function setToken(token: string | null) {
  if (token) {
    localStorage.setItem('token', token)
  } else {
    localStorage.removeItem('token')
    localStorage.removeItem('session')
  }
}

export function getStoredSession(): TokenResponse | null {
  const saved = localStorage.getItem('session')
  if (!saved) return null
  try {
    return JSON.parse(saved) as TokenResponse
  } catch {
    localStorage.removeItem('session')
    localStorage.removeItem('token')
    return null
  }
}

async function request(path: string, options: RequestInit = {}) {
  const token = localStorage.getItem('token')
  const headers: Record<string, string> = {
    ...((options.headers as Record<string, string>) || {}),
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const url = `${baseURL}${path}`

  let response: Response
  try {
    response = await fetch(url, { ...options, headers })
  } catch (err: any) {
    const error: any = new Error(err.message || 'Network error')
    error.response = { status: 0, data: { detail: 'Network error or server unreachable' } }
    throw error
  }

  if (response.status === 401) {
    setToken(null)
    localStorage.removeItem('session')
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  const contentType = response.headers.get('content-type')
  const data = contentType && contentType.includes('application/json') ? await response.json() : await response.text()

  if (!response.ok) {
    const error: any = new Error(data?.detail || 'Request failed')
    error.response = { status: response.status, data }
    throw error
  }

  return { data }
}

const api = {
  get: <T = any>(url: string, options?: RequestInit) =>
    request(url, { method: 'GET', ...options }) as Promise<{ data: T }>,
  post: <T = any>(url: string, body?: any, options?: RequestInit) =>
    request(url, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
      headers: body ? { 'Content-Type': 'application/json' } : {},
      ...options,
    }) as Promise<{ data: T }>,
  put: <T = any>(url: string, body?: any, options?: RequestInit) =>
    request(url, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
      headers: body ? { 'Content-Type': 'application/json' } : {},
      ...options,
    }) as Promise<{ data: T }>,
  delete: <T = any>(url: string, options?: RequestInit) =>
    request(url, { method: 'DELETE', ...options }) as Promise<{ data: T }>,
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const response = await fetch(`${baseURL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })

  const contentType = response.headers.get('content-type')
  const data = contentType && contentType.includes('application/json') ? await response.json() : await response.text()

  if (!response.ok) {
    throw new Error(data?.detail || 'Login failed')
  }

  return data as TokenResponse
}

export default api
