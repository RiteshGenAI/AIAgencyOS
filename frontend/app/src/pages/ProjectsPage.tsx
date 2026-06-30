import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../lib/api'
import type { Project, UserSession } from '../types'

type Props = {
  user: UserSession
}

export default function ProjectsPage({ user }: Props) {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [creating, setCreating] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [clientId, setClientId] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const { data } = await api.get<Project[]>(`/projects/${user.tenant_id}`)
      setProjects(data)
    } catch (err: any) {
      setError(err?.message || 'Failed to load projects')
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
      await api.post('/projects/', {
        tenant_id: user.tenant_id,
        client_id: clientId || 'default-client',
        name,
        description,
      })
      setName('')
      setDescription('')
      setClientId('')
      setCreating(false)
      await load()
    } catch (err: any) {
      setError(err?.message || 'Failed to create project')
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
          onClick={() => setCreating(!creating)}
          className="rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 px-4 py-2.5 text-xs font-semibold text-white hover:brightness-105 shadow-md shadow-cyan-600/10 transition duration-200"
        >
          {creating ? 'Cancel' : 'Create Project'}
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-600 font-medium">
          {error}
        </div>
      )}

      {creating && (
        <form
          onSubmit={create}
          className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4"
        >
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
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">Client ID</label>
              <input
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30 outline-none transition"
                value={clientId}
                onChange={(e) => setClientId(e.target.value)}
                placeholder="default-client"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">Description</label>
            <textarea
              className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30 outline-none transition"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
            />
          </div>
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
        {projects.length === 0 && !creating && (
          <div className="rounded-2xl border border-slate-200 bg-white p-12 text-center">
            <p className="text-sm text-slate-400">No projects yet.</p>
            <button
              onClick={() => setCreating(true)}
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
