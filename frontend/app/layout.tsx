import { ClerkProvider } from '@clerk/nextjs'
import type { Metadata } from 'next'
// @ts-ignore: side-effect import of global CSS without type declarations
import './globals.css'

export const metadata: Metadata = {
  title: 'PrepAI — AI Interview Practice',
  description: 'Practice realistic voice interviews with AI. Get instant feedback and land your dream job.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  )
}
