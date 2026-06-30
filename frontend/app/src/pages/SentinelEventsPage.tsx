import { useEffect, useState } from 'react'
import api from '../lib/api'
import type { Project, SentinelEvent, UserSession } from '../types'

type Props = {
  user: UserSession
}

export default function SentinelEventsPage({ user }: Props) {
  const [events, setEvents] = useState<SentinelEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError('')
      try {
        const { data: proj } = await api.get<Project[]>(`/projects/${user.tenant_id}`)
        const results = await Promise.all(
          proj.map((p) =>
            api.get<SentinelEvent[]>(`/sentinel-events/project/${p.id}`).catch(() => ({ data: [] as SentinelEvent[] }))
          )
        )
        setEvents(results.flatMap((r) => r.data))
      } catch (err: any) {
        setError(err?.message || 'Failed to load Sentinel events')
      } finally {
        setLoading(false)
      }
    }
    void load()
  }, [user.tenant_id])

  if (loading) {
    return (
      <div className="mx-auto w-full max-w-[1440px] px-8 py-20 flex flex-col items-center justify-center space-y-4">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-cyan-600" />
        <p className="text-sm font-medium text-slate-500">Loading Sentinel events...</p>
      </div>
    )
  }

  return (
    <div className="mx-auto w-full max-w-[1440px] px-8 py-10 space-y-8 bg-slate-50">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">Sentinel Events</h1>
        <p className="text-sm text-slate-500">Policy scans and safety checks powered by Sentinel.</p>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-600 font-medium">
          {error}
        </div>
      )}

      <div className="space-y-3">
        {events.map((e) => (
          <div
            key={e.id}
            className="rounded-2xl border border-slate-200 bg-white p-6 hover:border-cyan-200 hover:shadow-sm transition"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-3">
                <p className="font-bold text-slate-900">{e.scan_type}</p>
                <span className="text-xs text-slate-400">{e.entity_type}</span>
              </div>
              <span
                className={`text-[10px] font-extrabold uppercase tracking-widest px-2.5 py-1 rounded-md border ${
                  e.risk_score > 50
                    ? 'bg-rose-50 border-rose-100 text-rose-600'
                    : e.risk_score > 25
                    ? 'bg-amber-50 border-amber-100 text-amber-600'
                    : 'bg-emerald-50 border-emerald-100 text-emerald-600'
                }`}
              >
                Risk {e.risk_score}
              </span>
            </div>
            <p className="text-xs text-slate-500">{e.issues || 'No issues detected'}</p>
          </div>
        ))}
        {events.length === 0 && (
          <div className="rounded-2xl border border-slate-200 bg-white p-12 text-center">
            <p className="text-sm text-slate-400">No Sentinel events yet.</p>
          </div>
        )}
      </div>
    </div>
  )
}
