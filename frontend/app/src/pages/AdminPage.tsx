import { useEffect, useState } from 'react'
import api from '../lib/api'

type AdminUser = {
  id: string
  tenant_id: string
  email: string
  role: string
  is_active: boolean
}

type Props = {
  currentUserId: string
}

const ROLES = ['owner', 'manager', 'member', 'client'] as const
type Role = (typeof ROLES)[number]

function roleBadgeClasses(role: string) {
  switch (role) {
    case 'owner':
      return 'bg-indigo-100 text-indigo-700 border-indigo-200'
    case 'manager':
      return 'bg-cyan-100 text-cyan-700 border-cyan-200'
    case 'member':
      return 'bg-emerald-100 text-emerald-700 border-emerald-200'
    case 'client':
      return 'bg-slate-100 text-slate-700 border-slate-200'
    default:
      return 'bg-slate-100 text-slate-700 border-slate-200'
  }
}

export default function AdminPage({ currentUserId }: Props) {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [pendingId, setPendingId] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await api.get<AdminUser[]>('/admin/users')
      setUsers(res.data)
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to load users')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const changeRole = async (userId: string, newRole: Role) => {
    setPendingId(userId)
    try {
      await api.put(`/admin/users/${userId}/role?new_role=${encodeURIComponent(newRole)}`)
      await load()
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to change role')
    } finally {
      setPendingId(null)
    }
  }

  const deactivate = async (userId: string) => {
    if (!confirm('Deactivate this user? They will no longer be able to log in.')) return
    setPendingId(userId)
    try {
      await api.delete(`/admin/users/${userId}`)
      await load()
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to deactivate user')
    } finally {
      setPendingId(null)
    }
  }

  return (
    <div className="mx-auto w-full max-w-[1200px] px-6 py-10 lg:px-10">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">User Management</h1>
        <p className="mt-1 text-sm text-slate-500">
          Manage user accounts, roles, access states, and system authorizations.
        </p>
      </div>

      {error && (
        <div className="mb-6 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm font-medium text-rose-700">
          {error}
        </div>
      )}

      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="px-6 py-4 font-bold">User</th>
                <th className="px-6 py-4 font-bold">Tenant</th>
                <th className="px-6 py-4 font-bold">Role</th>
                <th className="px-6 py-4 font-bold">Status</th>
                <th className="px-6 py-4 font-bold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading && (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                    Loading users…
                  </td>
                </tr>
              )}
              {!loading && users.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                    No users found.
                  </td>
                </tr>
              )}
              {!loading &&
                users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-50/60 transition">
                    <td className="px-6 py-4">
                      <div className="font-semibold text-slate-900">{u.email}</div>
                      <div className="text-xs text-slate-400">{u.id}</div>
                    </td>
                    <td className="px-6 py-4 text-slate-600">{u.tenant_id}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center rounded-md border px-2 py-1 text-[10px] font-extrabold uppercase tracking-widest ${roleBadgeClasses(u.role)}`}
                      >
                        {u.role}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {u.is_active ? (
                        <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-700">
                          <span className="h-2 w-2 rounded-full bg-emerald-500" /> Active
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500">
                          <span className="h-2 w-2 rounded-full bg-slate-400" /> Inactive
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-end gap-2">
                        <select
                          aria-label="Change role"
                          disabled={pendingId === u.id || u.id === currentUserId}
                          value={u.role}
                          onChange={(e) => changeRole(u.id, e.target.value as Role)}
                          className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30 outline-none"
                        >
                          {ROLES.map((r) => (
                            <option key={r} value={r}>
                              {r}
                            </option>
                          ))}
                        </select>
                        <button
                          onClick={() => deactivate(u.id)}
                          disabled={pendingId === u.id || !u.is_active || u.id === currentUserId}
                          className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-1.5 text-xs font-semibold text-rose-700 hover:bg-rose-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-40 transition"
                          title={u.id === currentUserId ? 'You cannot deactivate your own account' : undefined}
                        >
                          {u.id === currentUserId ? 'Current user' : u.is_active ? 'Deactivate' : 'Deactivated'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
