'use client'
import Link from 'next/link'
import { useUser, UserButton } from '@clerk/nextjs'
import { ThemeToggle } from '@/components/ThemeToggle'

export default function ProfilePage() {
  const { user, isLoaded } = useUser()

  const displayName =
    [user?.firstName, user?.lastName].filter(Boolean).join(' ') ||
    user?.primaryEmailAddress?.emailAddress?.split('@')[0] ||
    'User'

  const email = user?.primaryEmailAddress?.emailAddress ?? '—'
  const initials = displayName.split(' ').map((n: string) => n[0]).join('').slice(0, 2).toUpperCase()

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-[#07090f] dark:text-white">

      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -left-40 w-[500px] h-[500px] rounded-full bg-indigo-500/5 blur-[120px] dark:bg-indigo-700/15" />
        <div className="absolute -bottom-40 -right-40 w-[500px] h-[500px] rounded-full bg-violet-500/5 blur-[120px] dark:bg-violet-700/15" />
      </div>

      {/* Header */}
      <header className="relative z-10 border-b backdrop-blur-xl border-slate-200 bg-white/80 dark:border-white/5 dark:bg-[#07090f]/80">
        <div className="max-w-3xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/dashboard" className="text-slate-400 hover:text-slate-700 dark:text-white/40 dark:hover:text-white transition-colors">
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
              </svg>
            </Link>
            <span className="text-slate-900 font-semibold dark:text-white">Profile</span>
          </div>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <UserButton />
          </div>
        </div>
      </header>

      <main className="relative z-10 max-w-3xl mx-auto px-6 py-10 flex flex-col gap-8">

        {/* Avatar + name */}
        <div className="flex items-center gap-6 p-6 rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-white/8 dark:bg-white/3 dark:shadow-none">
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white text-2xl font-bold shadow-lg shadow-indigo-500/30 shrink-0">
            {isLoaded ? initials : '?'}
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-xl font-bold text-slate-900 dark:text-white truncate">{isLoaded ? displayName : '...'}</h1>
            <p className="text-slate-500 text-sm mt-0.5 dark:text-white/40 truncate">{isLoaded ? email : '...'}</p>
            <span className="inline-flex items-center gap-1.5 mt-2 px-2.5 py-1 rounded-full bg-slate-100 border border-slate-200 text-slate-500 text-xs font-medium dark:bg-white/5 dark:border-white/10 dark:text-white/40">
              <span className="w-1.5 h-1.5 rounded-full bg-slate-400 dark:bg-white/30" />
              Free Plan
            </span>
          </div>
        </div>

        {/* Stats */}
        <div>
          <h2 className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-4 dark:text-white/40">Stats</h2>
          <div className="grid grid-cols-3 gap-4">
            {[
              { label: 'Interviews Done', value: '0', icon: '🎙️' },
              { label: 'Best Score', value: '—', icon: '⭐' },
              { label: 'Practice Hours', value: '0h', icon: '⏱️' },
            ].map(({ label, value, icon }) => (
              <div key={label} className="flex flex-col items-center gap-1 p-5 rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-white/8 dark:bg-white/3 dark:shadow-none">
                <span className="text-2xl">{icon}</span>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">{value}</p>
                <p className="text-slate-400 text-xs text-center dark:text-white/40">{label}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Account info */}
        <div>
          <h2 className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-4 dark:text-white/40">Account</h2>
          <div className="rounded-2xl border border-slate-200 bg-white overflow-hidden dark:border-white/8 dark:bg-white/3">
            {[
              { label: 'Full Name', value: isLoaded ? displayName : '...' },
              { label: 'Email', value: isLoaded ? email : '...' },
              { label: 'Member Since', value: isLoaded && user?.createdAt ? new Date(user.createdAt).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : '...' },
              { label: 'Auth Provider', value: isLoaded ? (user?.externalAccounts?.[0]?.provider ?? 'Email') : '...' },
            ].map(({ label, value }, i, arr) => (
              <div key={label} className={`flex items-center justify-between px-6 py-4 ${i < arr.length - 1 ? 'border-b border-slate-100 dark:border-white/5' : ''}`}>
                <span className="text-slate-500 text-sm dark:text-white/40">{label}</span>
                <span className="text-slate-900 text-sm font-medium dark:text-white truncate max-w-[60%] text-right">{value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Plan */}
        <div>
          <h2 className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-4 dark:text-white/40">Plan</h2>
          <div className="rounded-2xl border p-6 flex items-center justify-between border-slate-200 bg-white shadow-sm dark:border-white/8 dark:bg-white/3 dark:shadow-none">
            <div>
              <p className="text-slate-900 font-semibold dark:text-white">Free Plan</p>
              <p className="text-slate-400 text-sm mt-0.5 dark:text-white/40">3 interview sessions per month</p>
            </div>
            <Link
              href="/#pricing"
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-500 to-violet-600 text-white text-sm font-semibold hover:opacity-90 transition-opacity shadow-lg shadow-indigo-500/25"
            >
              Upgrade →
            </Link>
          </div>
        </div>

        {/* Resume upload (placeholder) */}
        <div>
          <h2 className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-4 dark:text-white/40">Resume</h2>
          <div className="rounded-2xl border border-dashed p-8 flex flex-col items-center gap-3 border-slate-200 bg-white dark:border-white/10 dark:bg-white/3">
            <div className="w-12 h-12 rounded-xl bg-indigo-50 flex items-center justify-center dark:bg-indigo-500/10">
              <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5} className="text-indigo-500">
                <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12l-3-3m0 0l-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
              </svg>
            </div>
            <p className="text-slate-500 text-sm dark:text-white/40">Upload your resume for AI-tailored interview prep</p>
            <button className="px-4 py-2 rounded-lg border text-sm font-medium transition-colors border-slate-200 text-slate-600 hover:bg-slate-50 dark:border-white/10 dark:text-white/60 dark:hover:bg-white/5">
              Upload PDF
            </button>
          </div>
        </div>

      </main>
    </div>
  )
}
