import { useState, useEffect } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import api from '../lib/api'

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const tokenFromQuery = searchParams.get('token') || ''
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    if (!tokenFromQuery) return
    setLoading(true)
    api.verifyEmail(tokenFromQuery)
      .then((data) => {
        setSuccess(data.message)
        setTimeout(() => navigate('/dashboard'), 2000)
      })
      .catch((err: any) => {
        setError(err?.message || 'Failed to verify email')
      })
      .finally(() => {
        setLoading(false)
      })
  }, [tokenFromQuery, navigate])

  return (
    <div className="relative flex min-h-screen items-center justify-center px-6 overflow-hidden bg-slate-50">
      <div className="absolute top-1/4 left-1/4 -z-10 h-72 w-72 rounded-full bg-cyan-100 blur-3xl opacity-60" />
      <div className="absolute bottom-1/4 right-1/4 -z-10 h-72 w-72 rounded-full bg-indigo-100 blur-3xl opacity-60" />

      <div className="relative w-full max-w-md rounded-2xl border border-slate-200/80 bg-white p-8 shadow-2xl text-center">
        <h2 className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-600 bg-clip-text text-3xl font-extrabold tracking-tight text-transparent">
          Verify your email
        </h2>

        {loading && (
          <p className="mt-6 text-sm font-medium text-slate-500">Verifying...</p>
        )}

        {error && (
          <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-600 font-medium">
            {error}
          </div>
        )}

        {success && (
          <div className="mt-4 rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-600 font-medium">
            {success}
          </div>
        )}

        {!tokenFromQuery && !loading && (
          <p className="mt-4 text-sm text-slate-500">
            If you have a verification token, use the link from your email.
          </p>
        )}

        <p className="mt-6 text-xs text-slate-400">
          <Link to="/login" className="text-cyan-600 hover:underline">
            Back to login
          </Link>
        </p>
      </div>
    </div>
  )
}
