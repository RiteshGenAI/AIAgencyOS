import type { TokenResponse, UserSession } from '../types'

const baseURL = '/api/v1'

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
    throw new Error(err.message || 'Network error')
  }

  if (response.status === 401) {
    setToken(null)
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  const contentType = response.headers.get('content-type')
  const data =
    contentType && contentType.includes('application/json')
      ? await response.json()
      : await response.text()

  if (!response.ok) {
    const detail = typeof data === 'object' && data?.detail ? data.detail : data
    throw new Error(detail || response.statusText)
  }

  return data
}

function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const payload = token.split('.')[1]
    return JSON.parse(atob(payload))
  } catch {
    return null
  }
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const body = new URLSearchParams({ username: email, password })
  const response = await fetch(`${baseURL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  })

  if (!response.ok) {
    const text = await response.text()
    let message = text
    try {
      const parsed = JSON.parse(text)
      message = parsed.detail || JSON.stringify(parsed)
    } catch {
      // keep raw text
    }
    throw new Error(message || response.statusText)
  }

  const tokenData = await response.json()
  const claims = decodeJwtPayload(tokenData.access_token) || {}
  const session: TokenResponse = {
    access_token: tokenData.access_token,
    token_type: tokenData.token_type || 'bearer',
    user: {
      id: String(claims.sub || ''),
      tenant_id: String(claims.tenant_id || ''),
      email,
      role: String(claims.role || 'member'),
    },
  }

  setToken(session.access_token)
  localStorage.setItem('session', JSON.stringify(session))
  return session
}

export function logout() {
  setToken(null)
}

export async function fetchProjects(tenantId: string) {
  return request(`/projects/${tenantId}`)
}

export async function fetchProjectSentinelEvents(projectId: string) {
  return request(`/sentinel-events/project/${projectId}`)
}

export async function fetchProjectInvoices(projectId: string) {
  return request(`/invoices/project/${projectId}`)
}

export type { UserSession, TokenResponse }
