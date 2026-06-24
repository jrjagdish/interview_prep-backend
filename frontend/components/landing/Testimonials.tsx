const testimonials = [
  { name: 'Arjun Mehta', role: 'Software Engineer', company: 'Google', avatar: 'AM', color: '#6366f1', stars: 5, text: "I had 3 FAANG interviews lined up and was terrified of the behavioral rounds. Two weeks with PrepAI and I felt like a completely different person. The AI actually pushes back when your answer is vague — exactly what real interviewers do." },
  { name: 'Priya Sharma', role: 'Product Manager', company: 'Meta', avatar: 'PS', color: '#8b5cf6', stars: 5, text: "The barge-in feature is genius. In real interviews, the interviewer sometimes interrupts you mid-answer. PrepAI trains you to handle that gracefully. I landed my PM role at Meta after 3 weeks of practice." },
  { name: 'Ravi Krishnan', role: 'Data Scientist', company: 'Amazon', avatar: 'RK', color: '#06b6d4', stars: 5, text: "I used to hate talking about my projects. The instant feedback showed me I was being too technical and losing the interviewer. PrepAI helped me find the right balance. Got the DS role at Amazon with a 40% comp increase." },
  { name: 'Sneha Patel', role: 'Frontend Engineer', company: 'Stripe', avatar: 'SP', color: '#10b981', stars: 5, text: "The 24/7 availability is a huge deal. I was practicing at midnight before an 8 AM interview. The AI never complains, never rushes you. It just adapts to your pace. Worth every penny of the Pro subscription." },
  { name: 'Kiran Reddy', role: 'UX Designer', company: 'Figma', avatar: 'KR', color: '#f59e0b', stars: 5, text: "As a designer, I was skeptical about an AI interview coach. But the voice-first experience is super natural. The AI asked smart follow-ups on my portfolio work that I wasn't prepared for — and that caught me before the real interview did." },
  { name: 'Deepika Nair', role: 'Backend Engineer', company: 'Uber', avatar: 'DN', color: '#ec4899', stars: 5, text: "The role-specific questions are incredibly relevant. For a backend SWE role, it asked about system design, scalability tradeoffs, and API design patterns. Felt like talking to a senior engineer. I was completely prepared." },
]

function Stars({ count }: { count: number }) {
  return (
    <div className="flex gap-0.5">
      {Array.from({ length: count }).map((_, i) => (
        <svg key={i} width="14" height="14" viewBox="0 0 24 24" fill="currentColor" className="text-amber-400">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>
      ))}
    </div>
  )
}

export default function Testimonials() {
  return (
    <section className="relative py-24 px-6">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute top-0 right-1/4 w-[400px] h-[400px] rounded-full bg-violet-500/5 blur-[100px] dark:bg-violet-700/8" />
      </div>

      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <p className="text-purple-600 text-sm font-semibold tracking-widest uppercase mb-3 dark:text-purple-400">Testimonials</p>
          <h2 className="text-4xl lg:text-5xl font-bold tracking-tight text-slate-900 dark:text-white">
            Used by candidates at{' '}
            <span className="bg-gradient-to-r from-purple-500 to-pink-500 bg-clip-text text-transparent">top companies</span>
          </h2>
          <p className="text-slate-500 text-lg mt-4 max-w-md mx-auto dark:text-white/50">
            Real stories from candidates who practiced with PrepAI and got the offer.
          </p>
        </div>

        <div className="columns-1 md:columns-2 lg:columns-3 gap-5 space-y-5">
          {testimonials.map((t) => (
            <div key={t.name} className="break-inside-avoid p-6 rounded-2xl border shadow-sm transition-colors
              border-slate-200 bg-white hover:shadow-md hover:bg-slate-50
              dark:border-white/8 dark:bg-white/3 dark:shadow-none dark:hover:bg-white/[0.04]">
              <Stars count={t.stars} />
              <p className="text-slate-600 text-sm leading-relaxed mt-3 mb-5 dark:text-white/65">"{t.text}"</p>
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0" style={{ backgroundColor: t.color }}>
                  {t.avatar}
                </div>
                <div>
                  <p className="text-slate-900 text-sm font-semibold dark:text-white">{t.name}</p>
                  <p className="text-slate-400 text-xs dark:text-white/40">{t.role} · {t.company}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
