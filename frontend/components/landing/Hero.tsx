import Link from 'next/link'

export default function Hero() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center px-6 pt-24 pb-16 overflow-hidden">

      {/* Ambient blobs */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-indigo-700/15 blur-[120px]" />
        <div className="absolute top-3/4 right-1/4 w-[400px] h-[400px] translate-x-1/2 -translate-y-1/2 rounded-full bg-violet-700/15 blur-[120px]" />
        <div className="absolute top-1/2 left-1/2 w-[300px] h-[300px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-indigo-600/8 blur-[80px]" />
      </div>

      {/* Subtle grid */}
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.015)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.015)_1px,transparent_1px)] bg-[size:64px_64px]" />

      <div className="relative z-10 max-w-6xl mx-auto w-full grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">

        {/* Left — copy */}
        <div className="flex flex-col items-start gap-6">
          {/* Badge */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
            <span className="text-indigo-300 text-xs font-semibold tracking-wide uppercase">AI-Powered Interview Practice</span>
          </div>

          {/* Headline */}
          <h1 className="text-5xl lg:text-6xl font-bold leading-[1.1] tracking-tight">
            Ace Your Next<br />
            <span className="bg-gradient-to-r from-indigo-400 via-violet-400 to-purple-400 bg-clip-text text-transparent">
              Interview
            </span>{' '}with AI
          </h1>

          <p className="text-white/55 text-lg leading-relaxed max-w-lg">
            Practice realistic voice interviews with an AI interviewer. Get instant feedback on your answers, communication style, and confidence — on demand, 24/7.
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row gap-3 mt-2">
            <Link href="/sign-up" className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-indigo-500 to-violet-600 text-white font-semibold text-base hover:opacity-90 transition-opacity shadow-xl shadow-indigo-500/30 text-center">
              Start for Free →
            </Link>
            <a href="#how-it-works" className="px-6 py-3.5 rounded-xl border border-white/10 text-white/70 hover:text-white hover:border-white/20 font-medium text-base transition-all text-center">
              See how it works
            </a>
          </div>

          {/* Social proof */}
          <div className="flex items-center gap-4 mt-2">
            <div className="flex -space-x-2">
              {['#6366f1','#8b5cf6','#a855f7','#06b6d4'].map((color, i) => (
                <div key={i} className="w-8 h-8 rounded-full border-2 border-[#07090f] flex items-center justify-center text-xs font-bold text-white" style={{ backgroundColor: color }}>
                  {['S','A','R','K'][i]}
                </div>
              ))}
            </div>
            <p className="text-white/40 text-sm">
              <span className="text-white/70 font-semibold">2,400+</span> candidates practiced this week
            </p>
          </div>
        </div>

        {/* Right — UI mockup */}
        <div className="relative flex items-center justify-center lg:justify-end">
          <div className="relative w-full max-w-md">
            {/* Glow behind card */}
            <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/20 to-violet-500/20 blur-2xl rounded-3xl scale-95" />

            {/* Mock interview card */}
            <div className="relative rounded-2xl border border-white/10 bg-[#0d1117] overflow-hidden shadow-2xl">
              {/* Mock header */}
              <div className="flex items-center justify-between px-5 py-4 border-b border-white/5">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-red-500" />
                  <div className="w-2 h-2 rounded-full bg-yellow-500" />
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                </div>
                <span className="text-white/40 text-xs font-medium">AI Interview — Software Engineer</span>
                <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-emerald-400 text-xs font-medium">Live</span>
                </div>
              </div>

              {/* Mock bot area */}
              <div className="flex flex-col items-center py-8 gap-4 relative">
                <div className="absolute inset-0 bg-indigo-700/5" />
                {/* Bot circle */}
                <div className="relative">
                  <div className="absolute inset-0 rounded-full bg-indigo-500/20 blur-xl scale-150" />
                  <div className="relative w-20 h-20 rounded-full bg-gradient-to-br from-indigo-500 via-violet-500 to-purple-600 flex items-center justify-center shadow-lg">
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                      <rect x="8" y="12" width="16" height="14" rx="4" fill="white" fillOpacity="0.9"/>
                      <rect x="12" y="6" width="8" height="8" rx="4" fill="white" fillOpacity="0.9"/>
                      <circle cx="13" cy="18" r="1.5" fill="#6366f1"/>
                      <circle cx="19" cy="18" r="1.5" fill="#6366f1"/>
                      <rect x="13" y="21" width="6" height="1.5" rx="0.75" fill="#6366f1"/>
                    </svg>
                  </div>
                  {/* Wave rings */}
                  <div className="absolute inset-0 rounded-full border border-indigo-500/30 scale-125 animate-ping opacity-50" />
                  <div className="absolute inset-0 rounded-full border border-violet-500/20 scale-150 animate-ping opacity-30" style={{ animationDelay: '0.4s' }} />
                </div>
                <p className="text-indigo-300 text-xs font-medium animate-pulse z-10">AI is speaking…</p>
              </div>

              {/* Mock transcript */}
              <div className="px-4 pb-4 flex flex-col gap-2.5">
                <div className="flex gap-2.5 px-3 py-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/15">
                  <span className="text-indigo-400 text-xs font-bold uppercase tracking-wider mt-0.5 shrink-0">AI</span>
                  <p className="text-white/80 text-xs leading-relaxed">Tell me about a challenging project you've worked on and how you handled it.</p>
                </div>
                <div className="flex gap-2.5 px-3 py-2.5 rounded-xl bg-white/5 border border-white/8">
                  <span className="text-white/40 text-xs font-bold uppercase tracking-wider mt-0.5 shrink-0">You</span>
                  <p className="text-white/70 text-xs leading-relaxed">Sure — at my last role I led a migration of our monolith to microservices…</p>
                </div>

                {/* Mic bar */}
                <div className="flex items-center gap-2 mt-1">
                  <div className="flex items-end gap-0.5 h-5">
                    {[3,5,8,5,3,6,4,7,5,3].map((h, i) => (
                      <div key={i} className="w-1 rounded-full bg-indigo-400/60 animate-pulse" style={{ height: `${h * 2}px`, animationDelay: `${i * 0.1}s` }} />
                    ))}
                  </div>
                  <span className="text-white/30 text-xs">Listening…</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
