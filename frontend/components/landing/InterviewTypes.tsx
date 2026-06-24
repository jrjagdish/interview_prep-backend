import Link from 'next/link'

const types = [
  {
    icon: '💻',
    title: 'Software Engineer',
    subtitle: 'Technical',
    difficulty: 'Medium',
    diffColor: 'text-amber-600 bg-amber-50 dark:text-amber-400 dark:bg-amber-400/10',
    gradient: 'from-indigo-500 to-violet-600',
    topics: ['Algorithms', 'Data Structures', 'System Design'],
  },
  {
    icon: '📊',
    title: 'Product Manager',
    subtitle: 'Strategy & Behavioral',
    difficulty: 'Medium',
    diffColor: 'text-amber-600 bg-amber-50 dark:text-amber-400 dark:bg-amber-400/10',
    gradient: 'from-violet-500 to-purple-600',
    topics: ['Product Sense', 'Metrics', 'Leadership'],
  },
  {
    icon: '📈',
    title: 'Data Science',
    subtitle: 'Technical & Analytics',
    difficulty: 'Hard',
    diffColor: 'text-red-600 bg-red-50 dark:text-red-400 dark:bg-red-400/10',
    gradient: 'from-cyan-500 to-blue-600',
    topics: ['Statistics', 'ML Concepts', 'SQL'],
  },
  {
    icon: '🎨',
    title: 'Frontend Engineer',
    subtitle: 'Technical',
    difficulty: 'Medium',
    diffColor: 'text-amber-600 bg-amber-50 dark:text-amber-400 dark:bg-amber-400/10',
    gradient: 'from-pink-500 to-rose-600',
    topics: ['React', 'CSS', 'Performance'],
  },
  {
    icon: '🏗️',
    title: 'System Design',
    subtitle: 'Architecture',
    difficulty: 'Hard',
    diffColor: 'text-red-600 bg-red-50 dark:text-red-400 dark:bg-red-400/10',
    gradient: 'from-orange-500 to-amber-600',
    topics: ['Scalability', 'Databases', 'APIs'],
  },
  {
    icon: '🧠',
    title: 'Behavioral',
    subtitle: 'STAR Method',
    difficulty: 'Easy',
    diffColor: 'text-emerald-600 bg-emerald-50 dark:text-emerald-400 dark:bg-emerald-400/10',
    gradient: 'from-emerald-500 to-teal-600',
    topics: ['Leadership', 'Teamwork', 'Problem-solving'],
  },
]

export default function InterviewTypes() {
  return (
    <section id="interview-types" className="relative py-24 px-6">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute top-1/2 right-0 w-[400px] h-[400px] rounded-full bg-indigo-500/5 blur-[100px] dark:bg-indigo-700/8" />
      </div>

      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-14">
          <p className="text-indigo-600 text-sm font-semibold tracking-widest uppercase mb-3 dark:text-indigo-400">Practice Interviews</p>
          <h2 className="text-4xl lg:text-5xl font-bold tracking-tight text-slate-900 dark:text-white">
            Try these{' '}
            <span className="bg-gradient-to-r from-indigo-500 to-violet-500 bg-clip-text text-transparent">
              interview types
            </span>
          </h2>
          <p className="text-slate-500 text-lg mt-4 max-w-xl mx-auto dark:text-white/50">
            Pick a role, jump in, and get grilled by our AI — just like the real thing.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {types.map((t) => (
            <div
              key={t.title}
              className="group flex flex-col rounded-2xl border shadow-sm p-6 transition-all duration-300
                border-slate-200 bg-white hover:shadow-lg hover:shadow-slate-200/80 hover:-translate-y-0.5
                dark:border-white/8 dark:bg-white/3 dark:shadow-none dark:hover:bg-white/5 dark:hover:border-white/12"
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${t.gradient} flex items-center justify-center text-2xl shadow-lg`}>
                  {t.icon}
                </div>
                <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${t.diffColor}`}>
                  {t.difficulty}
                </span>
              </div>

              <h3 className="text-slate-900 font-bold text-base mb-0.5 dark:text-white">{t.title}</h3>
              <p className="text-slate-400 text-xs mb-3 dark:text-white/40">{t.subtitle}</p>

              <div className="flex flex-wrap gap-1.5 mb-5">
                {t.topics.map((topic) => (
                  <span
                    key={topic}
                    className="text-xs px-2 py-0.5 rounded-full border
                      border-slate-200 text-slate-500 bg-slate-50
                      dark:border-white/10 dark:text-white/40 dark:bg-white/5"
                  >
                    {topic}
                  </span>
                ))}
              </div>

              <Link
                href="/sign-up"
                className={`mt-auto w-full py-2.5 rounded-xl text-center text-sm font-semibold text-white bg-gradient-to-r ${t.gradient} hover:opacity-90 transition-opacity`}
              >
                Start Practice →
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
