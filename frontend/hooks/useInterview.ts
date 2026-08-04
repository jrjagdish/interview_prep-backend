'use client'
import { useState, useEffect, useRef, useCallback } from 'react'
import { useAuth } from '@/context/AuthContext'
import { apiFetch } from '@/lib/api'

export type Status = 'idle' | 'connected' | 'disconnected' | 'error' | 'ended'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const WS_URL = API_URL.replace(/^http/, 'ws')

interface StartInterviewResponse {
  interview_id: string
  duration_seconds: number
}

export function useInterview(jobRole?: string) {
  const { token } = useAuth()
  const [status, setStatus] = useState<Status>('idle')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [transcript, setTranscript] = useState('')
  const [aiResponse, setAiResponse] = useState('')
  // true while Cartesia TTS audio is queued or playing — drives the wave animation
  const [isBotSpeaking, setIsBotSpeaking] = useState(false)
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null)
  const [isFinalQuestion, setIsFinalQuestion] = useState(false)

  const audioCtxRef = useRef<AudioContext | null>(null)
  const audioQueueRef = useRef<ArrayBuffer[]>([])
  const isPlayingRef = useRef(false)
  const currentSourceRef = useRef<AudioBufferSourceNode | null>(null)
  const socketRef = useRef<WebSocket | null>(null)
  const countdownRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // ── barge-in state ──────────────────────────────────────────────
  const VOLUME_THRESHOLD = 0.04
  const INTERRUPT_DELAY_MS = 1000
  const GRACE_PERIOD_MS = 300
  const speechStartRef = useRef<number | null>(null)
  const lastAboveRef = useRef<number | null>(null)

  const updateSpeakingState = useCallback(() => {
    const active = isPlayingRef.current || audioQueueRef.current.length > 0
    setIsBotSpeaking(active)
  }, [])

  const stopAudio = useCallback(() => {
    audioQueueRef.current = []
    if (currentSourceRef.current) {
      currentSourceRef.current.onended = null
      try { currentSourceRef.current.stop() } catch (_) {}
      currentSourceRef.current = null
    }
    isPlayingRef.current = false
    speechStartRef.current = null
    lastAboveRef.current = null
    setIsBotSpeaking(false)
  }, [])

  const playNextChunk = useCallback(() => {
    if (isPlayingRef.current || audioQueueRef.current.length === 0) return
    const ctx = audioCtxRef.current
    if (!ctx) return

    isPlayingRef.current = true
    setIsBotSpeaking(true)

    const buffer = audioQueueRef.current.shift()!
    const float32 = new Float32Array(buffer)
    const audioBuf = ctx.createBuffer(1, float32.length, 44100)
    audioBuf.copyToChannel(float32, 0)

    const source = ctx.createBufferSource()
    source.buffer = audioBuf
    source.connect(ctx.destination)
    currentSourceRef.current = source

    source.onended = () => {
      currentSourceRef.current = null
      isPlayingRef.current = false
      updateSpeakingState()
      playNextChunk()
    }
    source.start()
  }, [updateSpeakingState])

  const stopCountdown = useCallback(() => {
    if (countdownRef.current) {
      clearInterval(countdownRef.current)
      countdownRef.current = null
    }
  }, [])

  const endSession = useCallback(() => {
    const socket = socketRef.current
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send('end_session')
    }
  }, [])

  const handleCtrlMessage = useCallback((raw: string) => {
    let payload: { type: string; messages?: { role: string; content: string }[] }
    try {
      payload = JSON.parse(raw)
    } catch {
      return
    }

    if (payload.type === 'time_up') {
      setStatus('ended')
      setIsFinalQuestion(false)
      stopCountdown()
      socketRef.current?.close()
    } else if (payload.type === 'final_question') {
      setIsFinalQuestion(true)
    } else if (payload.type === 'history' && payload.messages) {
      const lastUser = [...payload.messages].reverse().find((m) => m.role === 'user')
      const lastAi = [...payload.messages].reverse().find((m) => m.role === 'assistant')
      if (lastUser) setTranscript(lastUser.content)
      if (lastAi) setAiResponse(lastAi.content)
    }
  }, [stopCountdown])

  // ── main effect: mic + websocket setup ─────────────────────────
  useEffect(() => {
    if (!token) return

    let mediaRecorder: MediaRecorder
    let analyser: AnalyserNode
    let intervalId: ReturnType<typeof setInterval>
    let socket: WebSocket
    let cancelled = false
    const authToken = token

    async function init() {
      let startData: StartInterviewResponse
      try {
        startData = await apiFetch<StartInterviewResponse>(
          '/api/interviews/start',
          authToken,
          { method: 'POST', body: JSON.stringify({ job_role: jobRole ?? null }) }
        )
      } catch (err) {
        if (cancelled) return
        setErrorMessage(err instanceof Error ? err.message : 'Could not start interview')
        setStatus('error')
        return
      }
      if (cancelled) return

      setTimeRemaining(startData.duration_seconds)
      countdownRef.current = setInterval(() => {
        setTimeRemaining((prev) => (prev === null ? null : Math.max(0, prev - 1)))
      }, 1000)

      // AudioContext must be created after a user gesture; creating it here is
      // fine because the hook mounts only after the user visits the page.
      audioCtxRef.current = new (window.AudioContext || (window as any).webkitAudioContext)()
      const ctx = audioCtxRef.current

      let stream: MediaStream
      try {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      } catch {
        setStatus('error')
        return
      }

      // ── MediaRecorder — sends 250ms audio chunks to backend ──
      mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })

      // ── AnalyserNode — measures mic volume for barge-in ──────
      analyser = ctx.createAnalyser()
      analyser.fftSize = 512
      const volumeData = new Uint8Array(analyser.frequencyBinCount)
      const micSrc = ctx.createMediaStreamSource(stream)
      micSrc.connect(analyser) // NOT connected to destination — avoids echo

      // ── WebSocket ─────────────────────────────────────────────
      socket = new WebSocket(
        `${WS_URL}/ws/${startData.interview_id}?token=${encodeURIComponent(authToken)}`
      )
      socketRef.current = socket

      socket.onopen = () => {
        setStatus('connected')
        mediaRecorder.addEventListener('dataavailable', (e) => {
          if (e.data.size > 0 && socket.readyState === WebSocket.OPEN) {
            socket.send(e.data)
          }
        })
        mediaRecorder.start(250)
      }

      socket.onclose = () => setStatus((prev) => (prev === 'ended' ? prev : 'disconnected'))
      socket.onerror = () => setStatus('error')

      socket.onmessage = (msg) => {
        if (msg.data instanceof Blob) {
          // Binary = TTS audio chunk from Cartesia
          msg.data.arrayBuffer().then((buf) => {
            audioQueueRef.current.push(buf)
            setIsBotSpeaking(true)
            playNextChunk()
          })
        } else {
          const text: string = msg.data
          if (!text) return
          if (text === 'stop_audio') { stopAudio(); return }
          if (text.startsWith('ctrl:')) { handleCtrlMessage(text.slice(5)); return }
          if (text.startsWith('ai:')) {
            setAiResponse((prev) => prev + text.slice(3))
          } else {
            // New transcript = new turn: clear previous responses
            setTranscript(text)
            setAiResponse('')
            setIsFinalQuestion(false)
          }
        }
      }

      // ── Barge-in VAD poll every 50ms ──────────────────────────
      intervalId = setInterval(() => {
        analyser.getByteTimeDomainData(volumeData)
        let sum = 0
        for (let i = 0; i < volumeData.length; i++) {
          const s = (volumeData[i] - 128) / 128
          sum += s * s
        }
        const rms = Math.sqrt(sum / volumeData.length)
        const ttsActive = isPlayingRef.current || audioQueueRef.current.length > 0
        const now = Date.now()

        if (rms > VOLUME_THRESHOLD) {
          lastAboveRef.current = now
          if (ttsActive) {
            if (!speechStartRef.current) {
              speechStartRef.current = now
            } else if (now - speechStartRef.current >= INTERRUPT_DELAY_MS) {
              if (socket.readyState === WebSocket.OPEN) {
                stopAudio()
                socket.send('interrupt')
              }
            }
          }
        } else {
          if (lastAboveRef.current && now - lastAboveRef.current > GRACE_PERIOD_MS) {
            speechStartRef.current = null
            lastAboveRef.current = null
          }
        }
      }, 50)
    }

    init()

    return () => {
      cancelled = true
      clearInterval(intervalId)
      stopCountdown()
      socketRef.current?.close()
      audioCtxRef.current?.close()
    }
  }, [token, jobRole, playNextChunk, stopAudio, stopCountdown, handleCtrlMessage])

  return { status, errorMessage, transcript, aiResponse, isBotSpeaking, timeRemaining, isFinalQuestion, endSession }
}
