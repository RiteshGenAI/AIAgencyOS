import { useState, useEffect, useCallback, lazy, Suspense } from 'react'
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import { setToken } from './lib/api'
import type { TokenResponse, UserSession } from './types'

const LoginPage = lazy(() => import('./pages/LoginPage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const ProjectPage = lazy(() => import('./pages/ProjectPage'))
const ProjectsPage = lazy(() => import('./pages/ProjectsPage'))
const LeadsPage = lazy(() => import('./pages/LeadsPage'))
const InvoicesPage = lazy(() => import('./pages/InvoicesPage'))
const WorkflowsPage = lazy(() => import('./pages/WorkflowsPage'))
const SentinelEventsPage = lazy(() => import('./pages/SentinelEventsPage'))
const AdminPage = lazy(() => import('./pages/AdminPage'))
const ForgotPasswordPage = lazy(() => import('./pages/ForgotPasswordPage'))
const ResetPasswordPage = lazy(() => import('./pages/ResetPasswordPage'))
const VerifyEmailPage = lazy(() => import('./pages/VerifyEmailPage'))

function App() {
  const [user, setUser] = useState<UserSession | null>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  const logout = useCallback(() => {
    setUser(null)
    setToken(null)
    navigate('/login')
  }, [navigate])

  useEffect(() => {
    const savedSession = localStorage.getItem('session')
    if (savedSession) {
      try {
        const parsed: TokenResponse = JSON.parse(savedSession)
        setToken(parsed.access_token)
        setUser(parsed.user)
      } catch {
        setToken(null)
        localStorage.removeItem('session')
      }
    }
    setLoading(false)
  }, [])

  const handleLogin = (data: TokenResponse) => {
    setToken(data.access_token)
    setUser(data.user)
    localStorage.setItem('session', JSON.stringify(data))
    navigate('/dashboard')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900 flex items-center justify-center">
        <div className="animate-pulse text-slate-500">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col lg:flex-row">
      {user && <Sidebar user={user} onLogout={logout} />}
      <div className={`flex-1 min-w-0 ${user ? 'pt-16 lg:pt-0 lg:pl-64' : ''}`}>
        <Suspense
          fallback={
            <div className="mx-auto w-full max-w-[1440px] px-8 py-20 flex flex-col items-center justify-center space-y-4">
              <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-cyan-600" />
              <p className="text-sm font-medium text-slate-500">Loading page...</p>
            </div>
          }
        >
          <Routes>
            <Route
              path="/login"
              element={user ? <Navigate to="/dashboard" /> : <LoginPage onLogin={handleLogin} />}
            />
            <Route
              path="/forgot-password"
              element={user ? <Navigate to="/dashboard" /> : <ForgotPasswordPage />}
            />
            <Route
              path="/reset-password"
              element={user ? <Navigate to="/dashboard" /> : <ResetPasswordPage />}
            />
            <Route
              path="/verify-email"
              element={user ? <Navigate to="/dashboard" /> : <VerifyEmailPage />}
            />
            <Route
              path="/dashboard"
              element={user ? <DashboardPage user={user} /> : <Navigate to="/login" />}
            />
            <Route
              path="/projects"
              element={user ? <ProjectsPage user={user} /> : <Navigate to="/login" />}
            />
            <Route
              path="/projects/:projectId"
              element={user ? <ProjectPage user={user} /> : <Navigate to="/login" />}
            />
            <Route
              path="/leads"
              element={user ? <LeadsPage user={user} /> : <Navigate to="/login" />}
            />
            <Route
              path="/invoices"
              element={user ? <InvoicesPage user={user} /> : <Navigate to="/login" />}
            />
            <Route
              path="/workflows"
              element={user ? <WorkflowsPage user={user} /> : <Navigate to="/login" />}
            />
            <Route
              path="/sentinel-events"
              element={user ? <SentinelEventsPage user={user} /> : <Navigate to="/login" />}
            />
            <Route
              path="/admin"
              element={
                user
                  ? user.role === 'owner'
                    ? <AdminPage currentUserId={user.id} />
                    : <Navigate to="/dashboard" />
                  : <Navigate to="/login" />
              }
            />
            <Route path="/" element={<Navigate to={user ? '/dashboard' : '/login'} />} />
          </Routes>
        </Suspense>
      </div>
    </div>
  )
}

export default App
