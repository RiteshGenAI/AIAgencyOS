import { useState } from 'react'
import { login } from '../lib/api'
import type { TokenResponse } from '../types'

type Props = {
  onLogin: (data: TokenResponse) => void
}

export default function LoginPage({ onLogin }: Props) {
  const [email, setEmail] = useState('admin@agency.local')
  const [password, setPassword] = useState('admin1234')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await login(email, password)
      onLogin(data)
    } catch (err: any) {
      setError(err?.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center px-6 overflow-hidden bg-slate-50">
      <div className="absolute top-1/4 left-1/4 -z-10 h-72 w-72 rounded-full bg-cyan-100 blur-3xl opacity-60" />
      <div className="absolute bottom-1/4 right-1/4 -z-10 h-72 w-72 rounded-full bg-indigo-100 blur-3xl opacity-60" />

      <form
        onSubmit={submit}
        className="relative w-full max-w-md rounded-2xl border border-slate-200/80 bg-white p-8 shadow-2xl transition hover:border-slate-300 duration-300"
      >
        <div className="mb-8 text-center">
          <h2 className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-600 bg-clip-text text-3xl font-extrabold tracking-tight text-transparent">
            Welcome back
          </h2>
          <p className="mt-2 text-sm text-slate-500">Sign in to your AI Agency OS account</p>
        </div>

        <div className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
              Email Address
            </label>
            <input
              id="email"
              name="email"
              autoComplete="email"
              className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30 outline-none transition duration-200"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@domain.com"
              type="email"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
              Password
            </label>
            <input
              id="password"
              name="password"
              autoComplete="current-password"
              type="password"
              className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30 outline-none transition duration-200"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>
        </div>

        {error && (
          <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-600 font-medium">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="mt-6 w-full rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 py-3 font-semibold text-white shadow-lg shadow-cyan-600/10 hover:shadow-cyan-600/25 hover:brightness-105 active:scale-[0.99] transition duration-200 disabled:opacity-50"
        >
          {loading ? 'Signing in...' : 'Sign In'}
        </button>

        <p className="mt-6 text-center text-xs text-slate-400">
          Administrator account required. Contact your systems team to register.
        </p>
      </form>
    </div>
  )
}
