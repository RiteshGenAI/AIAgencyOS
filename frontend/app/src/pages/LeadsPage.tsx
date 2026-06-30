import { useEffect, useState } from 'react'
import api from '../lib/api'
import type { Lead, UserSession } from '../types'

type Props = {
  user: UserSession
}

export default function LeadsPage({ user }: Props) {
  const [leads, setLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [creating, setCreating] = useState(false)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [notes, setNotes] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const { data } = await api.get<Lead[]>(`/leads/${user.tenant_id}`)
      setLeads(data)
    } catch (err: any) {
      setError(err?.message || 'Failed to load leads')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [user.tenant_id])

  const create = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      await api.post('/leads/', {
        tenant_id: user.tenant_id,
        name,
        email: email || null,
        phone: phone || null,
        notes: notes || null,
        source: 'web',
        raw_text: `${name} ${email} ${phone} ${notes}`,
      })
      setName('')
      setEmail('')
      setPhone('')
      setNotes('')
      setCreating(false)
      await load()
    } catch (err: any) {
      setError(err?.message || 'Failed to create lead')
    }
  }

  if (loading) {
    return (
      <div className="mx-auto w-full max-w-[1440px] px-8 py-20 flex flex-col items-center justify-center space-y-4">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-cyan-600" />
        <p className="text-sm font-medium text-slate-500">Loading leads...</p>
      </div>
    )
  }

  return (
    <div className="mx-auto w-full max-w-[1440px] px-8 py-10 space-y-8 bg-slate-50">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">Leads</h1>
          <p className="text-sm text-slate-500">Track and manage sales leads.</p>
        </div>
        <button
          onClick={() => setCreating(!creating)}
          className="rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 px-4 py-2.5 text-xs font-semibold text-white hover:brightness-105 shadow-md shadow-cyan-600/10 transition duration-200"
        >
          {creating ? 'Cancel' : 'Add Lead'}
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-600 font-medium">
          {error}
        </div>
      )}

      {creating && (
        <form onSubmit={create} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
          <h3 className="text-lg font-bold text-slate-900">New Lead</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">Name</label>
              <input
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30 outline-none transition"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">Email</label>
              <input
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30 outline-none transition"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                type="email"
              />
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">Phone</label>
              <input
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30 outline-none transition"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">Notes</label>
              <input
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30 outline-none transition"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </div>
          </div>
          <button
            type="submit"
            className="rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 px-6 py-2.5 text-xs font-semibold text-white hover:brightness-105 transition duration-200"
          >
            Add Lead
          </button>
        </form>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {leads.map((l) => (
          <div
            key={l.id}
            className="rounded-2xl border border-slate-200 bg-white p-5 hover:border-cyan-200 hover:shadow-sm transition"
          >
            <div className="flex items-center justify-between mb-2">
              <p className="font-bold text-slate-900">{l.name}</p>
              <span
                className={`text-[10px] font-extrabold uppercase tracking-widest px-2 py-1 rounded-md border ${
                  l.status === 'new'
                    ? 'bg-cyan-50 border-cyan-100 text-cyan-600'
                    : l.status === 'qualified'
                    ? 'bg-emerald-50 border-emerald-100 text-emerald-600'
                    : 'bg-slate-100 border-slate-200 text-slate-600'
                }`}
              >
                {l.status}
              </span>
            </div>
            {l.email && <p className="text-xs text-slate-500">{l.email}</p>}
            {l.phone && <p className="text-xs text-slate-500">{l.phone}</p>}
            {l.notes && <p className="text-xs text-slate-500 mt-2 line-clamp-2">{l.notes}</p>}
          </div>
        ))}
        {leads.length === 0 && !creating && (
          <div className="rounded-2xl border border-slate-200 bg-white p-12 text-center sm:col-span-2 lg:col-span-3">
            <p className="text-sm text-slate-400">No leads yet.</p>
          </div>
        )}
      </div>
    </div>
  )
}
