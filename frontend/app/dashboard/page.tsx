'use client'
import Link from 'next/link'
import { useAuth } from '@/context/AuthContext'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { ThemeToggle } from '@/components/ThemeToggle'

function DashboardContent() {
  const { user, logout } = useAuth()

  const displayName = user?.username ?? user?.email?.split('@')[0] ?? 'there'

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-[#07090f] dark:text-white">

      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -left-40 w-[500px] h-[500px] rounded-full bg-indigo-500/5 blur-[120px] dark:bg-indigo-700/15" />
        <div className="absolute -bottom-40 -right-40 w-[500px] h-[500px] rounded-full bg-violet-500/5 blur-[120px] dark:bg-violet-700/15" />
      </div>

      <header className="relative z-10 border-b backdrop-blur-xl border-slate-200 bg-white/80 dark:border-white/5 dark:bg-[#07090f]/80">
        <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="8" r="2.5" fill="white" />
                <path d="M8 2v1.5M8 12.5V14M2 8h1.5M12.5 8H14M3.76 3.76l1.06 1.06M11.18 11.18l1.06 1.06M3.76 12.24l1.06-1.06M11.18 4.82l1.06-1.06" stroke="white" strokeWidth="1.4" strokeLinecap="round" />
              </svg>
            </div>
            <span className="font-bold text-lg tracking-tight text-slate-900 dark:text-white">PrepAI</span>
          </Link>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <Link href="/profile" className="text-sm text-slate-500 hover:text-slate-900 dark:text-white/40 dark:hover:text-white transition-colors">
              Profile
            </Link>
            <button
              onClick={logout}
              className="text-sm text-slate-500 hover:text-slate-900 dark:text-white/40 dark:hover:text-white transition-colors"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      <main className="relative z-10 max-w-5xl mx-auto px-6 py-14 flex flex-col gap-12">

        <div>
          <p className="text-sm font-medium uppercase tracking-widest mb-2 text-slate-400 dark:text-white/40">Dashboard</p>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
            Welcome back,{' '}
            <span className="bg-gradient-to-r from-indigo-500 to-violet-500 bg-clip-text text-transparent">{displayName}</span>
          </h1>
          <p className="mt-2 text-sm text-slate-400 dark:text-white/40">Ready to sharpen your interview skills?</p>
        </div>

        <div className="rounded-2xl border border-indigo-500/20 bg-gradient-to-br from-indigo-500/10 to-violet-600/10 p-8 flex flex-col md:flex-row items-center justify-between gap-6">
          <div>
            <h2 className="text-xl font-semibold mb-1 text-slate-900 dark:text-white">Start a new interview</h2>
            <p className="text-sm max-w-sm text-slate-500 dark:text-white/40">
              Practice with an AI interviewer using real-time voice. Get instant responses and improve your answers.
            </p>
          </div>
          <Link
            href="/interview"
            className="shrink-0 px-8 py-3.5 rounded-xl bg-gradient-to-r from-indigo-500 to-violet-600 text-white font-semibold text-sm hover:opacity-90 transition-opacity shadow-lg shadow-indigo-500/30 whitespace-nowrap"
          >
            Start Interview →
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { label: 'Interviews Done', value: '0', icon: '🎙️' },
            { label: 'Best Score', value: '—', icon: '⭐' },
            { label: 'Plan', value: 'Free', icon: '🚀' },
          ].map(({ label, value, icon }) => (
            <div key={label} className="rounded-xl border shadow-sm px-6 py-5 flex items-center gap-4 border-slate-200 bg-white dark:border-white/8 dark:bg-white/3 dark:shadow-none">
              <span className="text-2xl">{icon}</span>
              <div>
                <p className="font-semibold text-lg leading-none text-slate-900 dark:text-white">{value}</p>
                <p className="text-xs mt-1 text-slate-400 dark:text-white/40">{label}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="grid sm:grid-cols-2 gap-4">
          <Link href="/profile" className="flex items-center gap-4 p-5 rounded-xl border shadow-sm transition-all border-slate-200 bg-white hover:shadow-md hover:border-slate-300 dark:border-white/8 dark:bg-white/3 dark:shadow-none dark:hover:bg-white/5">
            <div className="w-10 h-10 rounded-lg bg-indigo-50 flex items-center justify-center dark:bg-indigo-500/10">
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5} className="text-indigo-600 dark:text-indigo-400">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
              </svg>
            </div>
            <div>
              <p className="font-semibold text-sm text-slate-900 dark:text-white">View Profile</p>
              <p className="text-xs mt-0.5 text-slate-400 dark:text-white/40">Update your info &amp; resume</p>
            </div>
          </Link>

          <Link href="/#pricing" className="flex items-center gap-4 p-5 rounded-xl border shadow-sm transition-all border-slate-200 bg-white hover:shadow-md hover:border-slate-300 dark:border-white/8 dark:bg-white/3 dark:shadow-none dark:hover:bg-white/5">
            <div className="w-10 h-10 rounded-lg bg-violet-50 flex items-center justify-center dark:bg-violet-500/10">
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5} className="text-violet-600 dark:text-violet-400">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
              </svg>
            </div>
            <div>
              <p className="font-semibold text-sm text-slate-900 dark:text-white">Upgrade to Pro</p>
              <p className="text-xs mt-0.5 text-slate-400 dark:text-white/40">Unlimited sessions &amp; feedback</p>
            </div>
          </Link>
        </div>

        <div>
          <h3 className="text-sm font-semibold uppercase tracking-widest mb-4 text-slate-400 dark:text-white/60">Recent Interviews</h3>
          <div className="rounded-xl border shadow-sm px-6 py-10 flex flex-col items-center justify-center text-center border-slate-200 bg-white dark:border-white/8 dark:bg-white/3 dark:shadow-none">
            <p className="text-sm text-slate-400 dark:text-white/20">No interviews yet</p>
            <p className="text-xs mt-1 text-slate-400 dark:text-white/10">Your past sessions will appear here</p>
          </div>
        </div>

      </main>
    </div>
  )
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  )
}
