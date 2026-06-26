import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Route protection is handled client-side via ProtectedRoute component.
// This middleware is a pass-through kept for future server-side checks.
export function middleware(_req: NextRequest) {
  return NextResponse.next()
}

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
  ],
}
