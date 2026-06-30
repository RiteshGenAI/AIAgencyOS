import React, { useState } from 'react'
import type { TokenResponse } from '../lib/api'
import { login } from '../lib/api'

type Props = {
  onLogin: (session: TokenResponse) => void
}

const LoginPage: React.FC<Props> = ({ onLogin }) => {
  const [email, setEmail] = useState('admin@agency.local')
  const [password, setPassword] = useState('admin1234')
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    try {
      const session = await login(email, password)
      onLogin(session)
    } catch (err: any) {
      setError(String(err.message || err || 'Login failed'))
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm space-y-4 bg-slate-900 p-6 rounded-lg border border-slate-700"
      >
        <h1 className="text-xl font-semibold">AI Agency OS</h1>
        <p className="text-sm text-slate-400">Sign in with your agency account.</p>
        {error && <p className="text-sm text-red-400">{error}</p>}
        <input
          className="w-full rounded bg-slate-800 border border-slate-700 p-2"
          placeholder="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          className="w-full rounded bg-slate-800 border border-slate-700 p-2"
          placeholder="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button
          type="submit"
          className="w-full bg-emerald-500 text-slate-950 font-semibold rounded py-2 hover:bg-emerald-400"
        >
          Sign in
        </button>
      </form>
    </div>
  )
}

export default LoginPage
