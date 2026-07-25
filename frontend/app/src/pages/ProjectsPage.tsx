import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../lib/api'
import type { Project, UserSession, Client } from '../types'

type Props = {
  user: UserSession
}

export default function ProjectsPage({ user }: Props) {
  const [projects, setProjects] = useState<Project[]>([])
  const [clients, setClients] = useState<Client[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [creatingProject, setCreatingProject] = useState(false)
  const [name, setName] = useState('')
  const [clientId, setClientId] = useState('')
  const [newClientName, setNewClientName] = useState('')
  const [creatingClient, setCreatingClient] = useState(false)

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const [{ data: proj }, { data: cli }] = await Promise.all([
        api.get<Project[]>(`/projects/${user.tenant_id}`),
        api.get<Client[]>(`/clients/${user.tenant_id}`),
      ])
      setProjects(proj)
      setClients(cli)
    } catch (err: any) {
      setError(err?.message || 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [user.tenant_id])

  const resetForm = () => {
    setName('')
    setClientId('')
    setNewClientName('')
    setCreatingClient(false)
    setCreatingProject(false)
    setError('')
  }

  const createClient = async (e?: React.FormEvent) => {
    e?.preventDefault()
    if (!newClientName.trim()) return
    setError('')
    try {
      const { data } = await api.post<Client>('/clients/', {
        tenant_id: user.tenant_id,
        name: newClientName,
      })
      setClients((prev) => [...prev, data])
      setClientId(data.reference_id)
      setNewClientName('')
      setCreatingClient(false)
      if (clients.length === 0) {
        setCreatingProject(true)
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to create client')
    }
  }

  const create = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      await api.post('/projects/', {
        tenant_id: user.tenant_id,
        client_id: clientId,
        name,
      })
      setName('')
      setClientId('')
      setCreatingProject(false)
      setCreatingClient(false)
      await load()
    } catch (err: any) {
      setError(err?.message || 'Failed to create project')
    }
  }

  const startCreate = () => {
    if (clients.length === 0) {
      setCreatingClient(true)
    } else {
      setCreatingProject(true)
    }
  }

  if (loading) {
    return (
      <div className="mx-auto w-full max-w-[1440px] px-8 py-20 flex flex-col items-center justify-center space-y-4">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-cyan-600" />
        <p className="text-sm font-medium text-slate-500">Loading projects...</p>
      </div>
    )
  }

  return (
    <div className="mx-auto w-full max-w-[1440px] px-8 py-10 space-y-8 bg-slate-50">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">Projects</h1>
          <p className="text-sm text-slate-500">Manage agency projects and client work.</p>
        </div>
        <button
          onClick={creatingProject ? resetForm : startCreate}
          className="rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 px-4 py-2.5 text-xs font-semibold text-white hover:brightness-105 shadow-md shadow-cyan-600/10 transition duration-200"
        >
          {creatingProject ? 'Cancel' : 'Create Project'}
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-600 font-medium">
          {error}
        </div>
      )}

      {!creatingProject && creatingClient && clients.length === 0 && (
        <form onSubmit={createClient} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
          <h3 className="text-lg font-bold text-slate-900">Create Client First</h3>
          <p className="text-sm text-slate-500">You need to create a client before adding a project.</p>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">Client Name</label>
            <input
              className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30 outline-none transition"
              value={newClientName}
              onChange={(e) => setNewClientName(e.target.value)}
              placeholder="Client name"
              required
            />
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
              className="rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:brightness-105 transition"
            >
              Create Client
            </button>
            <button
              type="button"
              onClick={resetForm}
              className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {creatingProject && clients.length > 0 && (
        <form onSubmit={create} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
          <h3 className="text-lg font-bold text-slate-900">New Project</h3>
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
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">Client</label>
              <select
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30 outline-none transition"
                value={clientId}
                onChange={(e) => setClientId(e.target.value)}
                required
              >
                <option value="">Select client</option>
                {clients.map((c) => (
                  <option key={c.id} value={c.reference_id}>
                    {c.reference_id} - {c.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {!creatingClient ? (
            <div className="flex gap-3 pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setCreatingClient(true)}
                className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
              >
                + New Client
              </button>
            </div>
          ) : (
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 space-y-3">
              <h4 className="text-sm font-bold text-slate-900">New Client</h4>
              <input
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30 outline-none transition"
                value={newClientName}
                onChange={(e) => setNewClientName(e.target.value)}
                placeholder="Client name"
                required
              />
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={createClient}
                  className="rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:brightness-105 transition"
                >
                  Create Client
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setCreatingClient(false)
                    setNewClientName('')
                  }}
                  className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          <button
            type="submit"
            className="rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 px-6 py-2.5 text-xs font-semibold text-white hover:brightness-105 transition duration-200"
          >
            Create
          </button>
        </form>
      )}

      <div className="space-y-3">
        {projects.map((p) => (
          <Link
            key={p.id}
            to={`/projects/${p.id}`}
            className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white p-6 hover:border-cyan-200 hover:shadow-sm transition"
          >
            <div>
              <p className="font-bold text-slate-900">{p.name}</p>
              <p className="text-xs text-slate-500 mt-1">{p.description || 'No description'}</p>
            </div>
            <span
              className={`text-[10px] font-extrabold uppercase tracking-widest px-2.5 py-1 rounded-md border ${
                p.status === 'active'
                  ? 'bg-emerald-50 border-emerald-100 text-emerald-600'
                  : 'bg-slate-100 border-slate-200 text-slate-600'
              }`}
            >
              {p.status}
            </span>
          </Link>
        ))}
        {projects.length === 0 && !creatingProject && !creatingClient && (
          <div className="rounded-2xl border border-slate-200 bg-white p-12 text-center">
            <p className="text-sm text-slate-400">No projects yet.</p>
            <button
              onClick={startCreate}
              className="mt-3 text-xs font-bold text-cyan-600 hover:underline"
            >
              Create your first project →
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
