'use client'
import Link from 'next/link'
import { useState } from 'react'
import { useAuth } from '@/context/AuthContext'
import { ThemeToggle } from '@/components/ThemeToggle'

export default function Navbar() {
  const [open, setOpen] = useState(false)
  const { user, logout } = useAuth()
  const isSignedIn = !!user

  return (
    <nav className="fixed top-0 inset-x-0 z-50 border-b backdrop-blur-xl border-slate-200 bg-white/80 dark:border-white/5 dark:bg-[#07090f]/80">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">

        <Link href="/" className="flex items-center gap-2.5 shrink-0">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="2.5" fill="white" />
              <path d="M8 2v1.5M8 12.5V14M2 8h1.5M12.5 8H14M3.76 3.76l1.06 1.06M11.18 11.18l1.06 1.06M3.76 12.24l1.06-1.06M11.18 4.82l1.06-1.06" stroke="white" strokeWidth="1.4" strokeLinecap="round"/>
            </svg>
          </div>
          <span className="font-bold text-lg tracking-tight text-slate-900 dark:text-white">PrepAI</span>
        </Link>

        <div className="hidden md:flex items-center gap-8">
          {[['#features', 'Features'], ['#how-it-works', 'How It Works'], ['#pricing', 'Pricing']].map(([href, label]) => (
            <a key={href} href={href} className="text-sm font-medium transition-colors duration-200 text-slate-500 hover:text-slate-900 dark:text-white/50 dark:hover:text-white">
              {label}
            </a>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <ThemeToggle />

          {!isSignedIn ? (
            <>
              <Link href="/sign-in" className="hidden md:block text-sm font-medium transition-colors px-3 py-1.5 text-slate-500 hover:text-slate-900 dark:text-white/60 dark:hover:text-white">
                Sign In
              </Link>
              <Link href="/sign-up" className="px-4 py-2 rounded-lg bg-gradient-to-r from-indigo-500 to-violet-600 text-white text-sm font-semibold hover:opacity-90 transition-opacity shadow-lg shadow-indigo-500/25">
                Get Started
              </Link>
            </>
          ) : (
            <>
              <Link href="/dashboard" className="px-4 py-2 rounded-lg bg-gradient-to-r from-indigo-500 to-violet-600 text-white text-sm font-semibold hover:opacity-90 transition-opacity shadow-lg shadow-indigo-500/25">
                Dashboard
              </Link>
              <button
                onClick={logout}
                className="text-sm font-medium text-slate-500 hover:text-slate-900 dark:text-white/60 dark:hover:text-white transition-colors"
              >
                Sign out
              </button>
            </>
          )}

          <button onClick={() => setOpen(!open)} className="md:hidden p-1 text-slate-500 hover:text-slate-900 dark:text-white/60 dark:hover:text-white">
            <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              {open
                ? <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                : <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />}
            </svg>
          </button>
        </div>
      </div>

      {open && (
        <div className="md:hidden border-t px-6 py-4 flex flex-col gap-4 border-slate-200 bg-white dark:border-white/5 dark:bg-[#07090f]">
          {[['#features', 'Features'], ['#how-it-works', 'How It Works'], ['#pricing', 'Pricing']].map(([href, label]) => (
            <a key={href} href={href} onClick={() => setOpen(false)} className="text-sm font-medium transition-colors text-slate-500 hover:text-slate-900 dark:text-white/60 dark:hover:text-white">
              {label}
            </a>
          ))}
          {!isSignedIn && (
            <Link href="/sign-in" className="text-sm font-medium text-slate-500 hover:text-slate-900 dark:text-white/60 dark:hover:text-white">Sign In</Link>
          )}
        </div>
      )}
    </nav>
  )
}
