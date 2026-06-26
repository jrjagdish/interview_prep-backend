'use client'
import { useState, FormEvent } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'

export default function SignInPage() {
  const { login } = useAuth()
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      router.replace('/dashboard')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#07090f] flex flex-col items-center justify-center px-4 relative overflow-hidden">

      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-[400px] h-[400px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-indigo-700/15 blur-[100px]" />
        <div className="absolute bottom-1/4 right-1/4 w-[300px] h-[300px] translate-x-1/2 translate-y-1/2 rounded-full bg-violet-700/15 blur-[100px]" />
      </div>

      <Link href="/" className="relative z-10 flex items-center gap-2.5 mb-8">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <circle cx="8" cy="8" r="2.5" fill="white" />
            <path d="M8 2v1.5M8 12.5V14M2 8h1.5M12.5 8H14" stroke="white" strokeWidth="1.4" strokeLinecap="round"/>
          </svg>
        </div>
        <span className="text-white font-bold text-lg">PrepAI</span>
      </Link>

      <div className="relative z-10 w-full max-w-sm">
        <div className="rounded-2xl border border-white/10 bg-[#0d1117] shadow-2xl shadow-black/50 p-8">
          <h1 className="text-white font-bold text-xl mb-1">Welcome back</h1>
          <p className="text-white/50 text-sm mb-6">Sign in to your account</p>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-white/60 text-xs font-medium">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="px-4 py-2.5 rounded-xl bg-[#161b22] border border-white/10 text-white placeholder:text-white/30 focus:outline-none focus:border-indigo-500 text-sm transition-colors"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-white/60 text-xs font-medium">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                className="px-4 py-2.5 rounded-xl bg-[#161b22] border border-white/10 text-white placeholder:text-white/30 focus:outline-none focus:border-indigo-500 text-sm transition-colors"
              />
            </div>

            {error && (
              <p className="text-red-400 text-xs px-1">{error}</p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="mt-1 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-violet-600 text-white font-semibold text-sm hover:opacity-90 transition-opacity shadow-lg shadow-indigo-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing in…' : 'Sign In'}
            </button>
          </form>

          <p className="text-center text-white/30 text-xs mt-6">
            Don&apos;t have an account?{' '}
            <Link href="/sign-up" className="text-indigo-400 hover:text-indigo-300 transition-colors">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
