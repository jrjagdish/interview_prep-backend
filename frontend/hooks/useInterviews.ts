'use client'
import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '@/context/AuthContext'
import { apiFetch } from '@/lib/api'

export interface InterviewSummary {
  id: string
  job_role: string | null
  status: string
  score: number | null
  report_url: string | null
  created_at: string
  concluded_at: string | null
}

export function useInterviews() {
  const { token } = useAuth()
  const [interviews, setInterviews] = useState<InterviewSummary[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    if (!token) {
      setInterviews([])
      setIsLoading(false)
      return
    }
    setIsLoading(true)
    try {
      const data = await apiFetch<InterviewSummary[]>('/api/interviews', token)
      setInterviews(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load interviews')
    } finally {
      setIsLoading(false)
    }
  }, [token])

  useEffect(() => {
    refresh()
  }, [refresh])

  const completed = interviews.filter((i) => i.status === 'completed')
  const bestScore = completed.reduce<number | null>((best, i) => {
    if (i.score == null) return best
    return best === null ? i.score : Math.max(best, i.score)
  }, null)

  return { interviews, completed, bestScore, isLoading, error, refresh }
}
