'use client'
import { createContext, useContext, useEffect, useState, ReactNode } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export interface AuthUser {
  id: string
  email: string
  username: string | null
  image_url: string | null
  is_verified: boolean
  pdf_url : string | null
  is_pro: boolean
  available_interviews: number
}

interface AuthContextValue {
  user: AuthUser | null
  token: string | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
  setUser: (user: AuthUser | null) => void
  justLoggedIn: boolean
  consumeJustLoggedIn: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [justLoggedIn, setJustLoggedIn] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem('auth_token')
    if (stored) {
      setToken(stored)
      fetchMe(stored)
    } else {
      setIsLoading(false)
    }
  }, [])

  async function fetchMe(t: string) {
    try {
      const res = await fetch(`${API_URL}/api/users/me`, {
        headers: { Authorization: `Bearer ${t}` },
      })
      if (res.ok) {
        setUser(await res.json())
      } else {
        localStorage.removeItem('auth_token')
        setToken(null)
      }
    } finally {
      setIsLoading(false)
    }
  }

  async function login(email: string, password: string) {
    const res = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail ?? 'Login failed')
    }
    const data = await res.json()
    localStorage.setItem('auth_token', data.access_token)
    setToken(data.access_token)
    await fetchMe(data.access_token)
    setJustLoggedIn(true)
  }

  async function register(username: string, email: string, password: string) {
    const res = await fetch(`${API_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail ?? 'Registration failed')
    }
    const data = await res.json()
    localStorage.setItem('auth_token', data.access_token)
    setToken(data.access_token)
    await fetchMe(data.access_token)
    setJustLoggedIn(true)
  }

  function logout() {
    localStorage.removeItem('auth_token')
    setToken(null)
    setUser(null)
    setJustLoggedIn(false)
  }

  async function refreshUser() {
    if (token) await fetchMe(token)
  }

  function consumeJustLoggedIn() {
    setJustLoggedIn(false)
  }

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, register, logout, refreshUser, setUser, justLoggedIn, consumeJustLoggedIn }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
