import React, { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchProjectSentinelEvents, fetchProjectInvoices, type UserSession } from '../lib/api'

type Props = {
  user: UserSession
}

const ProjectPage: React.FC<Props> = ({ user }) => {
  const { projectId } = useParams()
  const [events, setEvents] = useState<any[]>([])
  const [invoices, setInvoices] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId) return
    const run = async () => {
      try {
        const [ev, inv] = await Promise.all([
          fetchProjectSentinelEvents(projectId),
          fetchProjectInvoices(projectId),
        ])
        setEvents(ev)
        setInvoices(inv)
      } catch (err: any) {
        setError(err.message || 'Failed to load project data')
      }
    }
    run()
  }, [projectId])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Project {projectId}</h1>
        <Link to="/" className="text-sm text-slate-300 hover:text-slate-100">
          Back to dashboard
        </Link>
      </div>
      <p className="text-sm text-slate-400">Tenant: {user.tenant_id}</p>
      {error && <p className="text-sm text-red-400">{error}</p>}

      <section className="space-y-2">
        <h2 className="text-xl font-semibold">Sentinel Events</h2>
        {events.length === 0 && <p className="text-sm text-slate-300">No events recorded.</p>}
        <ul className="space-y-1">
          {events.map((e) => (
            <li key={e.id} className="text-sm text-slate-200">
              <span className="font-mono text-xs text-slate-400">{e.scan_type}</span>{' '}
              risk {e.risk_score} — {e.issues || 'no issues'}
            </li>
          ))}
        </ul>
      </section>

      <section className="space-y-2">
        <h2 className="text-xl font-semibold">Invoices</h2>
        {invoices.length === 0 && <p className="text-sm text-slate-300">No invoices yet.</p>}
        <ul className="space-y-1">
          {invoices.map((inv) => (
            <li key={inv.id} className="text-sm text-slate-200">
              {inv.amount} {inv.currency} — {inv.status}
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}

export default ProjectPage
