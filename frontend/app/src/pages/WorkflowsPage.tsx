import { useEffect, useState } from 'react'
import api from '../lib/api'
import type { Project, UserSession } from '../types'

type Props = {
  user: UserSession
}

export default function WorkflowsPage({ user }: Props) {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [running, setRunning] = useState(false)
  const [projectId, setProjectId] = useState('')
  const [prompt, setPrompt] = useState('')
  const [result, setResult] = useState<any>(null)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const { data } = await api.get<Project[]>(`/projects/${user.tenant_id}`)
        setProjects(data)
      } catch (err: any) {
        setError(err?.message || 'Failed to load projects')
      } finally {
        setLoading(false)
      }
    }
    void load()
  }, [user.tenant_id])

  const runWorkflow = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setResult(null)
    setRunning(true)
    try {
      const project = projects.find((p) => p.id === projectId)
      const { data } = await api.post(`/workflows/${projectId}/landing-page`, {
        tenant_id: user.tenant_id,
        client_id: project?.tenant_id || user.tenant_id,
        project_id: projectId,
        policy_id: 'default',
        brief_text: prompt,
      })
      setResult(data)
    } catch (err: any) {
      setError(err?.message || 'Failed to run workflow')
    } finally {
      setRunning(false)
    }
  }

  if (loading) {
    return (
      <div className="mx-auto w-full max-w-[1440px] px-8 py-20 flex flex-col items-center justify-center space-y-4">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-cyan-600" />
        <p className="text-sm font-medium text-slate-500">Loading workflows...</p>
      </div>
    )
  }

  return (
    <div className="mx-auto w-full max-w-[1440px] px-8 py-10 space-y-8 bg-slate-50">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">Workflows</h1>
        <p className="text-sm text-slate-500">Run agent workflows against a project.</p>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-600 font-medium">
          {error}
        </div>
      )}

      <form onSubmit={runWorkflow} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
        <h3 className="text-lg font-bold text-slate-900">Run Landing Page Copy Workflow</h3>
        <div className="grid gap-4 sm:grid-cols-2">
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
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">Prompt</label>
            <input
              className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30 outline-none transition"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Write landing page copy for..."
              required
            />
          </div>
        </div>
        <button
          type="submit"
          disabled={running}
          className="rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 px-6 py-2.5 text-xs font-semibold text-white hover:brightness-105 transition duration-200 disabled:opacity-50"
        >
          {running ? 'Running...' : 'Run Workflow'}
        </button>
      </form>

      {result && (
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-bold text-slate-900 mb-4">Workflow Result</h3>
          <pre className="rounded-xl bg-slate-50 p-4 text-xs text-slate-700 overflow-auto max-h-[500px]">
            {JSON.stringify(result, null, 2)}
          </pre>
        </section>
      )}
    </div>
  )
}
