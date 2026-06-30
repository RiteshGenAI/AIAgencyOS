export type UserSession = {
  id: string
  tenant_id: string
  email: string
  role: string
}

export type TokenResponse = {
  access_token: string
  token_type: string
  user: UserSession
}

export type Project = {
  id: string
  tenant_id: string
  name: string
  description: string | null
  status: string
  created_at: string
  updated_at: string
}

export type Lead = {
  id: string
  tenant_id: string
  project_id: string | null
  name: string
  email: string | null
  phone: string | null
  status: string
  notes: string | null
  created_at: string
  updated_at: string
}

export type Invoice = {
  id: string
  tenant_id: string
  project_id: string | null
  amount: number
  currency: string
  status: string
  due_date: string | null
  description: string | null
  created_at: string
  updated_at: string
}

export type SentinelEvent = {
  id: string
  tenant_id: string
  project_id: string | null
  scan_type: string
  risk_score: number
  issues: string | null
  payload: any
  created_at: string
}

export type WorkflowRun = {
  id: string
  project_id: string
  workflow_type: string
  status: string
  result: any
  created_at: string
}
