import { SignIn } from '@clerk/nextjs'
import Link from 'next/link'

export default function SignInPage() {
  return (
    <div className="min-h-screen bg-[#07090f] flex flex-col items-center justify-center px-4 relative overflow-hidden">

      {/* Ambient blobs */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-[400px] h-[400px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-indigo-700/15 blur-[100px]" />
        <div className="absolute bottom-1/4 right-1/4 w-[300px] h-[300px] translate-x-1/2 translate-y-1/2 rounded-full bg-violet-700/15 blur-[100px]" />
      </div>

      {/* Logo link */}
      <Link href="/" className="relative z-10 flex items-center gap-2.5 mb-8">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <circle cx="8" cy="8" r="2.5" fill="white" />
            <path d="M8 2v1.5M8 12.5V14M2 8h1.5M12.5 8H14" stroke="white" strokeWidth="1.4" strokeLinecap="round"/>
          </svg>
        </div>
        <span className="text-white font-bold text-lg">PrepAI</span>
      </Link>

      {/* Clerk SignIn component */}
      <div className="relative z-10">
        <SignIn
          fallbackRedirectUrl="/interview"
          appearance={{
            variables: {
              colorPrimary: '#6366f1',
              colorBackground: '#0d1117',
              colorInputBackground: '#161b22',
              colorInputText: '#e6edf3',
              colorText: '#e6edf3',
              colorTextSecondary: '#7d8590',
              colorNeutral: '#30363d',
              borderRadius: '0.75rem',
              fontFamily: 'inherit',
            },
            elements: {
              card: 'shadow-2xl shadow-black/50 border border-white/10',
              headerTitle: 'text-white font-bold',
              headerSubtitle: 'text-white/50',
              socialButtonsBlockButton: 'border border-white/10 bg-white/5 hover:bg-white/10 text-white transition-colors',
              formFieldInput: 'bg-[#161b22] border-white/10 text-white placeholder:text-white/30 focus:border-indigo-500',
              formButtonPrimary: 'bg-gradient-to-r from-indigo-500 to-violet-600 hover:opacity-90 transition-opacity shadow-lg shadow-indigo-500/20',
              footerActionLink: 'text-indigo-400 hover:text-indigo-300',
              identityPreviewEditButton: 'text-indigo-400',
              dividerLine: 'bg-white/10',
              dividerText: 'text-white/30',
            },
          }}
        />
      </div>
    </div>
  )
}
