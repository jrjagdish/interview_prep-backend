'use client'
import { useEffect, useRef } from 'react'
import { useAuth } from '@clerk/nextjs'

export function useUserSync() {
  const { getToken, userId } = useAuth()
  const synced = useRef(false)

  useEffect(() => {
    // If Clerk isn't initialized, no user ID exists, or we already synced, jump out
    if (!getToken || !userId || synced.current) return

    // 1. Create a quick internal async function inside the effect
    const syncUser = async () => {
      try {
        synced.current = true // Set ref immediately to prevent race conditions from double execution

        // 2. Await the token safely
        const token = await getToken();

        // 3. Fire the request with the actual string token
        const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
        
        await fetch(`${baseUrl}/api/users/sync`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`, 
            'Content-Type': 'application/json',
          },
        })
      } catch (err) {
        console.error('[useUserSync] failed:', err)
        synced.current = false // Reset on true network failure so it can retry if necessary
      }
    }

    // 4. Trigger the operation
    syncUser()
  }, [getToken, userId])
}