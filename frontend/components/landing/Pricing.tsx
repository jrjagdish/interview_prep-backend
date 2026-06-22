import Link from 'next/link'

const plans = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    description: 'Perfect for trying it out before your next interview.',
    cta: 'Start Free',
    href: '/sign-up',
    highlighted: false,
    features: [
      '3 AI interview sessions / month',
      'Voice-based real-time interviews',
      'Basic transcript after each session',
      'Standard question bank (50+ questions)',
      'Email support',
    ],
    missing: [
      'Detailed AI feedback report',
      'Performance analytics dashboard',
      'Custom interview configurations',
    ],
  },
  {
    name: 'Pro',
    price: '$12',
    period: '/month',
    description: 'For serious candidates who want to land the job.',
    cta: 'Start Pro',
    href: '/sign-up?plan=pro',
    highlighted: true,
    badge: 'Most Popular',
    features: [
      'Unlimited AI interview sessions',
      'Voice-based real-time interviews',
      'Full transcript + barge-in detection',
      'Detailed AI feedback on every answer',
      'Performance analytics & trends',
      '500+ role-specific questions',
      'Custom interview configurations',
      'Priority support',
    ],
    missing: [],
  },
  {
    name: 'Team',
    price: '$49',
    period: '/month',
    description: 'For hiring managers, bootcamps, and career coaches.',
    cta: 'Contact Sales',
    href: 'mailto:team@prepai.io',
    highlighted: false,
    features: [
      'Everything in Pro',
      'Up to 20 team members',
      'Admin dashboard & reporting',
      'Bulk interview scheduling',
      'Custom question banks',
      'White-label option',
      'Dedicated account manager',
      'SLA-backed support',
    ],
    missing: [],
  },
]

function CheckIcon() {
  return (
    <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5} className="text-emerald-400 shrink-0">
      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
    </svg>
  )
}

function CrossIcon() {
  return (
    <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} className="text-white/20 shrink-0">
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>
  )
}

export default function Pricing() {
  return (
    <section id="pricing" className="relative py-24 px-6">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[700px] h-[400px] rounded-full bg-indigo-700/8 blur-[100px]" />
      </div>

      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <p className="text-indigo-400 text-sm font-semibold tracking-widest uppercase mb-3">Pricing</p>
          <h2 className="text-4xl lg:text-5xl font-bold tracking-tight">
            Simple,{' '}
            <span className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
              transparent
            </span>{' '}
            pricing
          </h2>
          <p className="text-white/50 text-lg mt-4 max-w-md mx-auto">
            No hidden fees. Cancel anytime. Start free and upgrade when you're ready.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 items-start">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`relative flex flex-col rounded-2xl border p-8 ${
                plan.highlighted
                  ? 'border-indigo-500/50 bg-gradient-to-b from-indigo-500/10 to-violet-500/5 shadow-2xl shadow-indigo-500/10'
                  : 'border-white/8 bg-white/3'
              }`}
            >
              {plan.badge && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-gradient-to-r from-indigo-500 to-violet-600 text-white text-xs font-semibold shadow-lg">
                  {plan.badge}
                </div>
              )}

              <div className="mb-6">
                <h3 className="text-white font-bold text-lg mb-1">{plan.name}</h3>
                <p className="text-white/45 text-sm mb-4">{plan.description}</p>
                <div className="flex items-baseline gap-1">
                  <span className="text-white text-4xl font-bold">{plan.price}</span>
                  <span className="text-white/40 text-sm">{plan.period}</span>
                </div>
              </div>

              <Link
                href={plan.href}
                className={`w-full py-3 rounded-xl text-center text-sm font-semibold transition-opacity mb-6 ${
                  plan.highlighted
                    ? 'bg-gradient-to-r from-indigo-500 to-violet-600 text-white hover:opacity-90 shadow-lg shadow-indigo-500/30'
                    : 'border border-white/15 text-white/80 hover:bg-white/5'
                }`}
              >
                {plan.cta}
              </Link>

              <div className="flex flex-col gap-3">
                {plan.features.map((f) => (
                  <div key={f} className="flex items-start gap-2.5">
                    <CheckIcon />
                    <span className="text-white/70 text-sm">{f}</span>
                  </div>
                ))}
                {plan.missing.map((f) => (
                  <div key={f} className="flex items-start gap-2.5">
                    <CrossIcon />
                    <span className="text-white/25 text-sm">{f}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <p className="text-center text-white/30 text-sm mt-8">
          All plans include TLS encryption, GDPR-compliant data handling, and a 14-day money-back guarantee on paid plans.
        </p>
      </div>
    </section>
  )
}
