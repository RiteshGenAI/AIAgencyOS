import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import api from '../lib/api'
import type { Invoice, SentinelEvent, UserSession } from '../types'

type Props = {
  user: UserSession
}

export default function ProjectPage({ user }: Props) {
  const { projectId } = useParams()
  const [events, setEvents] = useState<SentinelEvent[]>([])
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId) return
    const run = async () => {
      setLoading(true)
      try {
        const [ev, inv] = await Promise.all([
          api.get<SentinelEvent[]>(`/sentinel-events/project/${projectId}`),
          api.get<Invoice[]>(`/invoices/project/${projectId}`),
        ])
        setEvents(ev.data)
        setInvoices(inv.data)
      } catch (err: any) {
        setError(err?.message || 'Failed to load project data')
      } finally {
        setLoading(false)
      }
    }
    void run()
  }, [projectId])

  if (loading) {
    return (
      <div className="mx-auto w-full max-w-[1440px] px-8 py-20 flex flex-col items-center justify-center space-y-4">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-cyan-600" />
        <p className="text-sm font-medium text-slate-500">Loading project...</p>
      </div>
    )
  }

  return (
    <div className="mx-auto w-full max-w-[1440px] px-8 py-10 space-y-8 bg-slate-50">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-widest text-slate-400">Project</p>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">{projectId}</h1>
          <p className="text-sm text-slate-500">Tenant: {user.tenant_id}</p>
        </div>
        <Link
          to="/projects"
          className="rounded-xl bg-white border border-slate-200 px-4 py-2.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition duration-200 shadow-sm"
        >
          ← Back to projects
        </Link>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-600 font-medium">
          {error}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-bold text-slate-900 mb-4">Sentinel Events</h3>
          <div className="space-y-3">
            {events.length === 0 && <p className="text-sm text-slate-400 py-4 text-center">No events recorded.</p>}
            {events.map((e) => (
              <div key={e.id} className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
                <div className="flex items-center justify-between mb-1">
                  <p className="font-semibold text-slate-800">{e.scan_type}</p>
                  <span
                    className={`text-[10px] font-extrabold uppercase tracking-widest px-2 py-1 rounded border ${
                      e.risk_score > 50
                        ? 'bg-rose-50 border-rose-100 text-rose-600'
                        : 'bg-emerald-50 border-emerald-100 text-emerald-600'
                    }`}
                  >
                    Risk {e.risk_score}
                  </span>
                </div>
                <p className="text-xs text-slate-500">{e.issues || 'No issues'}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-bold text-slate-900 mb-4">Invoices</h3>
          <div className="space-y-3">
            {invoices.length === 0 && <p className="text-sm text-slate-400 py-4 text-center">No invoices yet.</p>}
            {invoices.map((inv) => (
              <div key={inv.id} className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50/50 p-4">
                <div>
                  <p className="font-semibold text-slate-800">{inv.description || 'Invoice'}</p>
                  <p className="text-xs text-slate-500">{inv.status}</p>
                </div>
                <p className="text-lg font-black text-slate-900">
                  {inv.amount} {inv.currency}
                </p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}
