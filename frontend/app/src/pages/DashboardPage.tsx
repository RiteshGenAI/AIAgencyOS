import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../lib/api'
import type { Project, Lead, Invoice, SentinelEvent, UserSession } from '../types'

type Props = {
  user: UserSession
}

export default function DashboardPage({ user }: Props) {
  const [projects, setProjects] = useState<Project[]>([])
  const [leads, setLeads] = useState<Lead[]>([])
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [events, setEvents] = useState<SentinelEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError('')
      try {
        const [p, l] = await Promise.all([
          api.get<Project[]>(`/projects/${user.tenant_id}?skip=0&limit=50`),
          api.get<Lead[]>(`/leads/${user.tenant_id}?skip=0&limit=50`),
        ])
        setProjects(p.data)
        setLeads(l.data)

        // Stage 2: invoices and Sentinel events are scoped to individual projects.
        // Mirror the aggregation pattern used by InvoicesPage and SentinelEventsPage.
        const projectList = p.data
        const [invResults, evtResults] = await Promise.all([
          Promise.all(
            projectList.map((project) =>
              api.get<Invoice[]>(`/invoices/project/${project.id}`).catch(() => ({ data: [] as Invoice[] }))
            )
          ),
          Promise.all(
            projectList.map((project) =>
              api.get<SentinelEvent[]>(`/sentinel-events/project/${project.id}`).catch(() => ({ data: [] as SentinelEvent[] }))
            )
          ),
        ])
        setInvoices(invResults.flatMap((r) => r.data))
        setEvents(evtResults.flatMap((r) => r.data))
      } catch (err: any) {
        setError(err?.message || 'Failed to load dashboard data')
      } finally {
        setLoading(false)
      }
    }
    void load()
  }, [user.tenant_id])

  const totalInvoiceAmount = invoices.reduce((sum, inv) => sum + Number(inv.amount), 0)
  const flaggedEvents = events.filter((e) => e.risk_score > 50).length

  if (loading) {
    return (
      <div className="mx-auto w-full max-w-[1440px] px-8 py-20 flex flex-col items-center justify-center space-y-4">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-cyan-600" />
        <p className="text-sm font-medium text-slate-500">Loading your agency dashboard...</p>
      </div>
    )
  }

  return (
    <div className="mx-auto w-full max-w-[1440px] px-8 py-10 space-y-8 bg-slate-50">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">Dashboard</h1>
          <p className="text-sm text-slate-500">Overview of your agency projects, leads, invoices, and Sentinel activity.</p>
        </div>
        <div className="flex gap-3">
          <Link
            to="/projects"
            className="rounded-xl bg-white border border-slate-200 px-4 py-2.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition duration-200 shadow-sm"
          >
            View Projects
          </Link>
          <Link
            to="/workflows"
            className="rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 px-4 py-2.5 text-xs font-semibold text-white hover:brightness-105 shadow-md shadow-cyan-600/10 transition duration-200"
          >
            Run Workflow
          </Link>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-600 font-medium">
          {error}
        </div>
      )}

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 relative overflow-hidden group hover:border-cyan-200 transition duration-300 shadow-sm">
          <div className="absolute top-0 right-0 h-24 w-24 -mr-8 -mt-8 rounded-full bg-cyan-100/40 blur-2xl group-hover:bg-cyan-100/70 transition duration-300" />
          <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Projects</p>
          <p className="mt-4 text-3xl font-black text-slate-900 tracking-tight">{projects.length}</p>
          <div className="mt-2 text-xs font-medium text-slate-500">Active agency projects</div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 relative overflow-hidden group hover:border-indigo-200 transition duration-300 shadow-sm">
          <div className="absolute top-0 right-0 h-24 w-24 -mr-8 -mt-8 rounded-full bg-indigo-100/40 blur-2xl group-hover:bg-indigo-100/70 transition duration-300" />
          <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Leads</p>
          <p className="mt-4 text-3xl font-black text-slate-900 tracking-tight">{leads.length}</p>
          <div className="mt-2 text-xs font-medium text-slate-500">Tracked leads</div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 relative overflow-hidden group hover:border-emerald-200 transition duration-300 shadow-sm">
          <div className="absolute top-0 right-0 h-24 w-24 -mr-8 -mt-8 rounded-full bg-emerald-100/40 blur-2xl group-hover:bg-emerald-100/70 transition duration-300" />
          <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Invoiced</p>
          <p className="mt-4 text-3xl font-black text-slate-900 tracking-tight">
            ${totalInvoiceAmount.toFixed(2)}
          </p>
          <div className="mt-2 text-xs font-medium text-slate-500">Total invoice value</div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 relative overflow-hidden group hover:border-rose-200 transition duration-300 shadow-sm">
          <div className="absolute top-0 right-0 h-24 w-24 -mr-8 -mt-8 rounded-full bg-rose-100/40 blur-2xl group-hover:bg-rose-100/70 transition duration-300" />
          <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Sentinel Alerts</p>
          <p className={`mt-4 text-3xl font-black tracking-tight ${flaggedEvents > 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
            {flaggedEvents}
          </p>
          <div className="mt-2 text-xs font-medium text-slate-500">High-risk policy events</div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-slate-900">Recent Projects</h3>
            <Link to="/projects" className="text-xs font-semibold text-cyan-600 hover:underline">
              View all →
            </Link>
          </div>
          <div className="space-y-3">
            {projects.slice(0, 5).map((p) => (
              <Link
                key={p.id}
                to={`/projects/${p.id}`}
                className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50/50 p-4 hover:border-cyan-200 transition"
              >
                <div>
                  <p className="font-semibold text-slate-800">{p.name}</p>
                  <p className="text-xs text-slate-500">{p.description || 'No description'}</p>
                </div>
                <span
                  className={`text-[10px] font-extrabold uppercase tracking-widest px-2 py-1 rounded border ${
                    p.status === 'active'
                      ? 'bg-emerald-50 border-emerald-100 text-emerald-600'
                      : 'bg-slate-100 border-slate-200 text-slate-600'
                  }`}
                >
                  {p.status}
                </span>
              </Link>
            ))}
            {projects.length === 0 && (
              <p className="text-sm text-slate-400 py-4 text-center">No projects yet.</p>
            )}
          </div>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-slate-900">Recent Sentinel Events</h3>
            <Link to="/sentinel-events" className="text-xs font-semibold text-cyan-600 hover:underline">
              View all →
            </Link>
          </div>
          <div className="space-y-3">
            {events.slice(0, 5).map((e) => (
              <div
                key={e.id}
                className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50/50 p-4"
              >
                <div>
                  <p className="font-semibold text-slate-800">{e.scan_type}</p>
                  <p className="text-xs text-slate-500">{e.issues || 'No issues'}</p>
                </div>
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
            ))}
            {events.length === 0 && (
              <p className="text-sm text-slate-400 py-4 text-center">No Sentinel events yet.</p>
            )}
          </div>
        </section>
      </div>
    </div>
  )
}
