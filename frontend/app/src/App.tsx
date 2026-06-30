import React, { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom'

import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import ProjectPage from './pages/ProjectPage'
import { getStoredSession, logout, setToken, type TokenResponse } from './lib/api'

function AppRoutes() {
  const [session, setSession] = useState<TokenResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const saved = getStoredSession()
    if (saved) {
      setToken(saved.access_token)
      setSession(saved)
    }
    setLoading(false)
  }, [])

  const handleLogin = (data: TokenResponse) => {
    setSession(data)
    navigate('/')
  }

  const handleLogout = () => {
    logout()
    setSession(null)
    navigate('/login')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
        Loading...
      </div>
    )
  }

  return (
    <Routes>
      <Route
        path="/login"
        element={session ? <Navigate to="/" replace /> : <LoginPage onLogin={handleLogin} />}
      />
      <Route
        path="/"
        element={
          session ? (
            <DashboardPage user={session.user} onLogout={handleLogout} />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path="/projects/:projectId"
        element={session ? <ProjectPage user={session.user} /> : <Navigate to="/login" replace />}
      />
      <Route path="*" element={<Navigate to={session ? '/' : '/login'} replace />} />
    </Routes>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  )
}

export default App
