import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchProjects, type UserSession } from '../lib/api'

type Props = {
  user: UserSession
  onLogout: () => void
}

const DashboardPage: React.FC<Props> = ({ user, onLogout }) => {
  const [projects, setProjects] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const run = async () => {
      try {
        const data = await fetchProjects(user.tenant_id)
        setProjects(data)
      } catch (err: any) {
        setError(err.message || 'Failed to load projects')
      }
    }
    run()
  }, [user.tenant_id])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 space-y-6">
      <header className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">AI Agency OS Dashboard</h1>
          <p className="text-sm text-slate-400">
            {user.email} · {user.role}
          </p>
        </div>
        <button
          type="button"
          onClick={onLogout}
          className="text-sm text-slate-300 hover:text-slate-100"
        >
          Sign out
        </button>
      </header>

      <section className="space-y-2">
        <h2 className="text-xl font-semibold">Projects</h2>
        {error && <p className="text-sm text-red-400">{error}</p>}
        <div className="space-y-2">
          {projects.map((p) => (
            <Link
              key={p.id}
              to={`/projects/${p.id}`}
              className="block rounded bg-slate-900 border border-slate-700 p-3 hover:border-emerald-500"
            >
              {p.name} <span className="text-xs text-slate-400">({p.status})</span>
            </Link>
          ))}
          {!error && projects.length === 0 && (
            <p className="text-sm text-slate-400">No projects yet for this tenant.</p>
          )}
        </div>
      </section>
    </div>
  )
}

export default DashboardPage
