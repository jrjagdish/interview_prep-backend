'use client'
import { useEffect, useRef } from 'react'
import { useUser } from '@clerk/nextjs'

export function useUserSync() {
  const { user, isLoaded } = useUser()
  const synced = useRef(false)

  useEffect(() => {
    if (!isLoaded || !user || synced.current) return
    synced.current = true

    const payload = {
      clerkId: user.id,
      email: user.primaryEmailAddress?.emailAddress ?? '',
      firstName: user.firstName ?? '',
      lastName: user.lastName ?? '',
      imageUrl: user.imageUrl,
      provider: user.primaryEmailAddress?.verification?.strategy ?? 'email',
      createdAt: user.createdAt,
    }

    fetch(`${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'}/api/users/sync`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).catch((err) => console.error('[useUserSync] failed:', err))
  }, [isLoaded, user])
}
