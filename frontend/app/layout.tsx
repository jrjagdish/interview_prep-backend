import type { Metadata } from 'next'
// @ts-ignore: side-effect import of global CSS without type declarations
import './globals.css'
import { ThemeProvider } from '@/components/ThemeProvider'
import { AuthProvider } from '@/context/AuthContext'

export const metadata: Metadata = {
  title: 'PrepAI — AI Interview Practice',
  description: 'Practice realistic voice interviews with AI. Get instant feedback and land your dream job.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>
        <AuthProvider>
          <ThemeProvider>
            {children}
          </ThemeProvider>
        </AuthProvider>
      </body>
    </html>
  )
}
