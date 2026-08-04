'use client'
import { useState } from 'react'
import { useAuth } from '@/context/AuthContext'
import { apiFetch } from '@/lib/api'

const FREE_CREDIT_BONUS = 3

export function ClaimCreditsModal({ onClose }: { onClose: () => void }) {
  const { user, token, setUser } = useAuth()
  const [isClaiming, setIsClaiming] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleClaim() {
    setIsClaiming(true)
    setError(null)
    try {
      const data = await apiFetch<{ available_interviews: number }>(
        '/api/profile/claim-credit',
        token,
        { method: 'POST' }
      )
      if (user) {
        setUser({ ...user, available_interviews: data.available_interviews })
      }
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not claim credits')
    } finally {
      setIsClaiming(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
      <div className="relative w-full max-w-sm rounded-2xl border border-indigo-500/20 bg-[#0d1017] p-7 shadow-2xl shadow-indigo-500/10">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-white/30 hover:text-white text-sm"
          aria-label="Dismiss"
        >
          ✕
        </button>

        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-2xl mb-4">
          🎁
        </div>

        <h2 className="text-lg font-bold text-white mb-1">You've got free interview credits!</h2>
        <p className="text-sm text-white/50 mb-6">
          Claim {FREE_CREDIT_BONUS} free interview credits to practice with the AI interviewer, on us.
        </p>

        {error && <p className="text-red-400 text-xs mb-4">{error}</p>}

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2.5 rounded-xl border border-white/10 text-white/60 text-sm font-medium hover:bg-white/5 transition-colors"
          >
            Maybe later
          </button>
          <button
            onClick={handleClaim}
            disabled={isClaiming}
            className="flex-1 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-violet-600 text-white text-sm font-semibold hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {isClaiming ? 'Claiming…' : 'Claim credits'}
          </button>
        </div>
      </div>
    </div>
  )
}
