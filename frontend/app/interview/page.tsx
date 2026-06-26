'use client'
import { useAuth } from '@/context/AuthContext'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import BotAvatar from '@/components/BotAvatar'
import { useInterview } from '@/hooks/useInterview'

const STATUS_LABEL: Record<string, { label: string; color: string }> = {
  idle:         { label: 'Starting…',    color: 'bg-yellow-400' },
  connected:    { label: 'Live',         color: 'bg-emerald-400 animate-pulse' },
  disconnected: { label: 'Disconnected', color: 'bg-red-500' },
  error:        { label: 'Error',        color: 'bg-red-500' },
}

function InterviewContent() {
  const { user, logout } = useAuth()
  const { status, transcript, aiResponse, isBotSpeaking } = useInterview()
  const { label, color } = STATUS_LABEL[status] ?? STATUS_LABEL.idle

  const displayName = user?.username ?? user?.email?.split('@')[0] ?? 'You'

  return (
    <main className="relative w-screen h-screen overflow-hidden bg-[#07090f] flex flex-col">

      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -top-32 -left-32 w-96 h-96 rounded-full bg-indigo-700/20 blur-[120px]" />
        <div className="absolute -bottom-32 -right-32 w-96 h-96 rounded-full bg-violet-700/20 blur-[120px]" />
      </div>

      <header className="relative z-10 flex items-center justify-between px-8 pt-6 pb-4">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
            <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="2.5" fill="white" />
              <path d="M8 2v1.5M8 12.5V14M2 8h1.5M12.5 8H14" stroke="white" strokeWidth="1.4" strokeLinecap="round"/>
            </svg>
          </div>
          <span className="text-white/70 text-sm font-medium tracking-widest uppercase">PrepAI</span>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10">
            <span className={`w-2 h-2 rounded-full ${color}`} />
            <span className="text-white/60 text-xs font-medium">{label}</span>
          </div>
          <button
            onClick={logout}
            className="text-white/40 hover:text-white text-xs transition-colors"
          >
            Sign out
          </button>
        </div>
      </header>

      <section className="relative z-10 flex-1 flex flex-col items-center justify-center gap-8">
        <BotAvatar isSpeaking={isBotSpeaking} />
        <p className={`text-white/40 text-sm font-medium tracking-wide transition-opacity duration-300 ${isBotSpeaking ? 'opacity-100' : 'opacity-0'}`}>
          AI is speaking…
        </p>
      </section>

      <section className="relative z-10 px-8 pb-6 flex flex-col gap-3 max-w-2xl mx-auto w-full">
        {transcript && (
          <div className="flex items-start gap-3 px-4 py-3 rounded-xl bg-white/5 border border-white/8 backdrop-blur-sm">
            <span className="text-white/40 text-xs font-semibold uppercase tracking-widest mt-0.5 shrink-0">{displayName}</span>
            <p className="text-white/80 text-sm leading-relaxed">{transcript}</p>
          </div>
        )}
        {aiResponse && (
          <div className="flex items-start gap-3 px-4 py-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 backdrop-blur-sm">
            <span className="text-indigo-400 text-xs font-semibold uppercase tracking-widest mt-0.5 shrink-0">AI</span>
            <p className="text-white/90 text-sm leading-relaxed">{aiResponse}</p>
          </div>
        )}
        {!transcript && !aiResponse && status === 'connected' && (
          <div className="text-center text-white/20 text-sm py-2">
            Start speaking to begin the interview…
          </div>
        )}
      </section>

      <div className="absolute z-20 bottom-6 right-8 flex items-center gap-2.5 px-3 py-2 rounded-xl bg-white/5 border border-white/10 backdrop-blur-sm">
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white text-xs font-bold shrink-0">
          {displayName[0].toUpperCase()}
        </div>
        <div>
          <p className="text-white text-xs font-semibold">{displayName}</p>
          <p className="text-white/40 text-xs">Candidate</p>
        </div>
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 ml-1" />
      </div>

    </main>
  )
}

export default function InterviewPage() {
  return (
    <ProtectedRoute>
      <InterviewContent />
    </ProtectedRoute>
  )
}
