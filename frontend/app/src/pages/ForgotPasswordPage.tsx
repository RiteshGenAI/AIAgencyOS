import { useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../lib/api'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)
    try {
      const data = await api.forgotPassword(email)
      setSuccess(data.message)
      setEmail('')
    } catch (err: any) {
      setError(err?.message || 'Failed to request password reset')
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
            Reset password
          </h2>
          <p className="mt-2 text-sm text-slate-500">Enter your email and we'll send you a reset link.</p>
        </div>

        {error && (
          <div className="mb-4 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-600 font-medium">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-4 rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-600 font-medium">
            {success}
          </div>
        )}

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
        </div>

        <button
          type="submit"
          disabled={loading}
          className="mt-6 w-full rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 py-3 font-semibold text-white shadow-lg shadow-cyan-600/10 hover:shadow-cyan-600/25 hover:brightness-105 active:scale-[0.99] transition duration-200 disabled:opacity-50"
        >
          {loading ? 'Sending...' : 'Send reset link'}
        </button>

        <p className="mt-6 text-center text-xs text-slate-400">
          <Link to="/login" className="text-cyan-600 hover:underline">
            Back to login
          </Link>
        </p>
      </form>
    </div>
  )
}
