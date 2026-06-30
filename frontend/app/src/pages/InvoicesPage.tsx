import { useEffect, useState } from 'react'
import api from '../lib/api'
import type { Invoice, Project, UserSession } from '../types'

type Props = {
  user: UserSession
}

export default function InvoicesPage({ user }: Props) {
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [creating, setCreating] = useState(false)
  const [projectId, setProjectId] = useState('')
  const [amount, setAmount] = useState('')
  const [currency, setCurrency] = useState('USD')
  const [description, setDescription] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const { data: proj } = await api.get<Project[]>(`/projects/${user.tenant_id}`)
      setProjects(proj)
      const results = await Promise.all(
        proj.map((p) => api.get<Invoice[]>(`/invoices/project/${p.id}`).catch(() => ({ data: [] as Invoice[] })))
      )
      setInvoices(results.flatMap((r) => r.data))
    } catch (err: any) {
      setError(err?.message || 'Failed to load invoices')
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
      await api.post('/invoices/', {
        tenant_id: user.tenant_id,
        project_id: projectId,
        amount: Number(amount),
        currency,
        description: description || null,
      })
      setProjectId('')
      setAmount('')
      setCurrency('USD')
      setDescription('')
      setCreating(false)
      await load()
    } catch (err: any) {
      setError(err?.message || 'Failed to create invoice')
    }
  }

  if (loading) {
    return (
      <div className="mx-auto w-full max-w-[1440px] px-8 py-20 flex flex-col items-center justify-center space-y-4">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-cyan-600" />
        <p className="text-sm font-medium text-slate-500">Loading invoices...</p>
      </div>
    )
  }

  return (
    <div className="mx-auto w-full max-w-[1440px] px-8 py-10 space-y-8 bg-slate-50">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">Invoices</h1>
          <p className="text-sm text-slate-500">Create and track client invoices.</p>
        </div>
        <button
          onClick={() => setCreating(!creating)}
          className="rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 px-4 py-2.5 text-xs font-semibold text-white hover:brightness-105 shadow-md shadow-cyan-600/10 transition duration-200"
        >
          {creating ? 'Cancel' : 'Create Invoice'}
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-600 font-medium">
          {error}
        </div>
      )}

      {creating && (
        <form onSubmit={create} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
          <h3 className="text-lg font-bold text-slate-900">New Invoice</h3>
          <div className="grid gap-4 sm:grid-cols-3">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">Project</label>
              <select
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30 outline-none transition"
                value={projectId}
                onChange={(e) => setProjectId(e.target.value)}
                required
              >
                <option value="">Select project</option>
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">Amount</label>
              <input
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30 outline-none transition"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                type="number"
                step="0.01"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">Currency</label>
              <input
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30 outline-none transition"
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                required
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">Description</label>
            <input
              className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30 outline-none transition"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <button
            type="submit"
            className="rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 px-6 py-2.5 text-xs font-semibold text-white hover:brightness-105 transition duration-200"
          >
            Create Invoice
          </button>
        </form>
      )}

      <div className="space-y-3">
        {invoices.map((inv) => (
          <div
            key={inv.id}
            className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white p-6 hover:border-cyan-200 hover:shadow-sm transition"
          >
            <div>
              <p className="font-bold text-slate-900">{inv.description || 'Invoice'}</p>
              <p className="text-xs text-slate-500 mt-1">Project: {inv.project_id}</p>
            </div>
            <div className="text-right">
              <p className="text-lg font-black text-slate-900">
                {inv.amount} {inv.currency}
              </p>
              <span
                className={`text-[10px] font-extrabold uppercase tracking-widest px-2 py-1 rounded-md border ${
                  inv.status === 'paid'
                    ? 'bg-emerald-50 border-emerald-100 text-emerald-600'
                    : inv.status === 'overdue'
                    ? 'bg-rose-50 border-rose-100 text-rose-600'
                    : 'bg-amber-50 border-amber-100 text-amber-600'
                }`}
              >
                {inv.status}
              </span>
            </div>
          </div>
        ))}
        {invoices.length === 0 && !creating && (
          <div className="rounded-2xl border border-slate-200 bg-white p-12 text-center">
            <p className="text-sm text-slate-400">No invoices yet.</p>
          </div>
        )}
      </div>
    </div>
  )
}
