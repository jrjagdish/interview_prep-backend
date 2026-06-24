'use client'
import Link from 'next/link'
import { useUser, UserButton } from '@clerk/nextjs'
import { useUserSync } from '@/hooks/useUserSync'

export default function DashboardPage() {
  useUserSync()
  const { user } = useUser()
  
  console.log(user)

  const displayName =
    user?.firstName ??
    user?.primaryEmailAddress?.emailAddress?.split('@')[0] ??
    'there'

  return (
    <div className="min-h-screen bg-[#07090f] text-white">

      {/* Ambient blobs */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -left-40 w-[500px] h-[500px] rounded-full bg-indigo-700/15 blur-[120px]" />
        <div className="absolute -bottom-40 -right-40 w-[500px] h-[500px] rounded-full bg-violet-700/15 blur-[120px]" />
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-white/5 backdrop-blur-xl bg-[#07090f]/80">
        <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="8" r="2.5" fill="white" />
                <path d="M8 2v1.5M8 12.5V14M2 8h1.5M12.5 8H14M3.76 3.76l1.06 1.06M11.18 11.18l1.06 1.06M3.76 12.24l1.06-1.06M11.18 4.82l1.06-1.06" stroke="white" strokeWidth="1.4" strokeLinecap="round" />
              </svg>
            </div>
            <span className="text-white font-bold text-lg tracking-tight">PrepAI</span>
          </Link>
          <UserButton />
        </div>
      </header>

      {/* Main */}
      <main className="relative z-10 max-w-5xl mx-auto px-6 py-14 flex flex-col gap-12">

        {/* Welcome */}
        <div>
          <p className="text-white/40 text-sm font-medium uppercase tracking-widest mb-2">Dashboard</p>
          <h1 className="text-3xl font-bold text-white">
            Welcome back, <span className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">{displayName}</span>
          </h1>
          <p className="text-white/40 mt-2 text-sm">Ready to sharpen your interview skills?</p>
        </div>

        {/* Start Interview CTA */}
        <div className="rounded-2xl border border-indigo-500/20 bg-gradient-to-br from-indigo-500/10 to-violet-600/10 p-8 flex flex-col md:flex-row items-center justify-between gap-6">
          <div>
            <h2 className="text-xl font-semibold text-white mb-1">Start a new interview</h2>
            <p className="text-white/40 text-sm max-w-sm">
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

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { label: 'Interviews Done', value: '0', icon: '🎙️' },
            { label: 'Best Score', value: '—', icon: '⭐' },
            { label: 'Plan', value: 'Free', icon: '🚀' },
          ].map(({ label, value, icon }) => (
            <div
              key={label}
              className="rounded-xl border border-white/8 bg-white/3 px-6 py-5 flex items-center gap-4"
            >
              <span className="text-2xl">{icon}</span>
              <div>
                <p className="text-white font-semibold text-lg leading-none">{value}</p>
                <p className="text-white/40 text-xs mt-1">{label}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Recent interviews placeholder */}
        <div>
          <h3 className="text-white/60 text-sm font-semibold uppercase tracking-widest mb-4">Recent Interviews</h3>
          <div className="rounded-xl border border-white/8 bg-white/3 px-6 py-10 flex flex-col items-center justify-center text-center">
            <p className="text-white/20 text-sm">No interviews yet</p>
            <p className="text-white/10 text-xs mt-1">Your past sessions will appear here</p>
          </div>
        </div>

      </main>
    </div>
  )
}
