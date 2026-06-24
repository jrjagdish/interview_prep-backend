const features = [
  {
    icon: (<svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z" /></svg>),
    title: 'Real-time Voice Interviews',
    description: 'Speak naturally with our AI interviewer powered by state-of-the-art speech recognition. No typing — just talk.',
    iconBg: 'bg-indigo-50 dark:bg-indigo-500/10',
    iconColor: 'text-indigo-600 dark:text-indigo-400',
  },
  {
    icon: (<svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" /></svg>),
    title: 'Instant AI Feedback',
    description: 'Receive detailed feedback on your answers, communication clarity, technical accuracy, and areas for improvement.',
    iconBg: 'bg-violet-50 dark:bg-violet-500/10',
    iconColor: 'text-violet-600 dark:text-violet-400',
  },
  {
    icon: (<svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" /></svg>),
    title: 'Performance Analytics',
    description: 'Track your progress across sessions. See trends in your confidence, response quality, and technical competence over time.',
    iconBg: 'bg-cyan-50 dark:bg-cyan-500/10',
    iconColor: 'text-cyan-600 dark:text-cyan-400',
  },
  {
    icon: (<svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 00.75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 00-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0112 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 01-.673-.38m0 0A2.18 2.18 0 013 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 013.413-.387m7.5 0V5.25A2.25 2.25 0 0013.5 3h-3a2.25 2.25 0 00-2.25 2.25v.894m7.5 0a48.667 48.667 0 00-7.5 0M12 12.75h.008v.008H12v-.008z" /></svg>),
    title: 'Role-Specific Questions',
    description: 'Prepare for Software Engineer, Product Manager, Data Science, or Design interviews with curated question banks.',
    iconBg: 'bg-emerald-50 dark:bg-emerald-500/10',
    iconColor: 'text-emerald-600 dark:text-emerald-400',
  },
  {
    icon: (<svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>),
    title: '24/7 Availability',
    description: 'Practice at 3 AM before a morning interview. Your AI interviewer never sleeps and is always ready when you are.',
    iconBg: 'bg-orange-50 dark:bg-orange-500/10',
    iconColor: 'text-orange-600 dark:text-orange-400',
  },
  {
    icon: (<svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" /></svg>),
    title: 'Barge-in Detection',
    description: 'Interrupt the AI mid-sentence just like a real interview. Our advanced voice detection handles natural conversation flow.',
    iconBg: 'bg-pink-50 dark:bg-pink-500/10',
    iconColor: 'text-pink-600 dark:text-pink-400',
  },
]

export default function Features() {
  return (
    <section id="features" className="relative py-24 px-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <p className="text-indigo-600 text-sm font-semibold tracking-widest uppercase mb-3 dark:text-indigo-400">Features</p>
          <h2 className="text-4xl lg:text-5xl font-bold tracking-tight text-slate-900 dark:text-white">
            Everything you need to{' '}
            <span className="bg-gradient-to-r from-indigo-500 to-violet-500 bg-clip-text text-transparent">prepare</span>
          </h2>
          <p className="text-slate-500 text-lg mt-4 max-w-xl mx-auto dark:text-white/50">
            A complete interview practice suite built for serious job seekers.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map((f) => (
            <div key={f.title} className="group relative p-6 rounded-2xl border shadow-sm transition-all duration-300
              border-slate-200 bg-white hover:shadow-md hover:shadow-slate-200/80
              dark:border-white/8 dark:bg-white/3 dark:shadow-none dark:hover:bg-white/5 dark:hover:border-white/12">
              <div className={`w-11 h-11 rounded-xl ${f.iconBg} ${f.iconColor} flex items-center justify-center mb-4`}>
                {f.icon}
              </div>
              <h3 className="text-slate-900 font-semibold text-base mb-2 dark:text-white">{f.title}</h3>
              <p className="text-slate-500 text-sm leading-relaxed dark:text-white/45">{f.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
