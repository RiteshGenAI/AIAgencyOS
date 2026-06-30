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
