const steps = [
  { number: '01', title: 'Create your account', description: 'Sign up in seconds. No credit card required to start. We use Clerk for secure, frictionless authentication.', icon: (<svg width="28" height="28" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" /></svg>) },
  { number: '02', title: 'Choose your interview type', description: 'Select your target role (SWE, PM, Data Science, Design) and experience level. We tailor questions to match.', icon: (<svg width="28" height="28" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75" /></svg>) },
  { number: '03', title: 'Practice with AI', description: 'Have a real voice conversation with our AI interviewer. Interrupt, ask clarifications, and respond naturally.', icon: (<svg width="28" height="28" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z" /></svg>) },
  { number: '04', title: 'Review & improve', description: 'Get a full transcript and AI-generated feedback after each session. Track your growth across interviews.', icon: (<svg width="28" height="28" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>) },
]

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="relative py-24 px-6">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-violet-500/5 blur-[100px] dark:bg-violet-700/8" />
      </div>

      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <p className="text-violet-600 text-sm font-semibold tracking-widest uppercase mb-3 dark:text-violet-400">How It Works</p>
          <h2 className="text-4xl lg:text-5xl font-bold tracking-tight text-slate-900 dark:text-white">
            From sign-up to{' '}
            <span className="bg-gradient-to-r from-violet-500 to-purple-500 bg-clip-text text-transparent">offer letter</span>
          </h2>
          <p className="text-slate-500 text-lg mt-4 max-w-lg mx-auto dark:text-white/50">
            Four simple steps stand between you and interview confidence.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 relative">
          <div className="hidden lg:block absolute top-12 left-[12.5%] right-[12.5%] h-px bg-gradient-to-r from-transparent via-slate-200 to-transparent dark:via-white/10" />

          {steps.map((step, i) => (
            <div key={step.number} className="relative flex flex-col items-start gap-4 p-6 rounded-2xl border shadow-sm transition-colors
              border-slate-200 bg-white dark:border-white/8 dark:bg-white/3 dark:shadow-none">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500/15 to-violet-500/15 border flex items-center justify-center border-slate-200 text-slate-600 dark:border-white/10 dark:text-white/70">
                  {step.icon}
                </div>
                <span className="text-slate-200 font-bold text-2xl font-mono dark:text-white/20">{step.number}</span>
              </div>
              <div>
                <h3 className="text-slate-900 font-semibold text-base mb-2 dark:text-white">{step.title}</h3>
                <p className="text-slate-500 text-sm leading-relaxed dark:text-white/45">{step.description}</p>
              </div>
              {i < steps.length - 1 && (
                <div className="lg:hidden absolute -bottom-3 left-1/2 -translate-x-1/2 w-px h-6 bg-slate-200 dark:bg-white/10" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
