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
}

interface AuthContextValue {
  user: AuthUser | null
  token: string | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

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
    setUser({ id: data.user_id, email: data.email, username: data.username, image_url: null, is_verified: false, pdf_url: null })
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
    setUser({ id: data.user_id, email: data.email, username: data.username, image_url: null, is_verified: false, pdf_url: null })
  }

  function logout() {
    localStorage.removeItem('auth_token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
