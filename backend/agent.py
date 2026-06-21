import asyncio
from fastapi import WebSocket, FastAPI
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from groq import AsyncGroq
import os
from deepgram import AsyncDeepgramClient
from deepgram.listen import ListenV1Results
from cartesia import AsyncCartesia

load_dotenv()
deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")
client = AsyncGroq(api_key=groq_api_key)
dg_client = AsyncDeepgramClient(api_key=deepgram_api_key)
Cs_client = AsyncCartesia(api_key=os.getenv("CARTESIA_API_KEY"))

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Live Transcription</title>
    </head>
    <body>
        <h1>Transcribe Audio With FastAPI</h1>
        <p id="status">Connection status will go here</p>
        <h2>What you spoke:</h2>
        <p id="transcript"></p>
        <h2>AI Response:</h2>
        <p id="ai-response"></p>

        <script>
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)()
    const audioQueue = []
    let isPlaying = false
    let currentSource = null
    
    // BARGE-IN CONFIGURATION
    const VOLUME_THRESHOLD = 0.04;      // Back to your original responsive threshold
    const INTERRUPT_DELAY_MS = 1000;    // Needs 1 second of total speech activity
    const GRACE_PERIOD_MS = 300;        // How long user can pause mid-sentence without resetting the timer

    let speechStartTimestamp = null;    // When the user started talking
    let lastTimeAboveThreshold = null;  // Last time we heard audio above the threshold

    function stopAudio() {
        audioQueue.length = 0
        if (currentSource) {
            currentSource.onended = null
            try { currentSource.stop() } catch (_) {}
            currentSource = null
        }
        isPlaying = false
        resetBargeInTrackers()
    }

    function resetBargeInTrackers() {
        speechStartTimestamp = null;
        lastTimeAboveThreshold = null;
    }

    function playNextChunk() {
        if (isPlaying || audioQueue.length === 0) return
        isPlaying = true
        const buffer = audioQueue.shift()
        const float32Array = new Float32Array(buffer)
        const audioBuffer = audioCtx.createBuffer(1, float32Array.length, 44100)
        audioBuffer.copyToChannel(float32Array, 0)
        const source = audioCtx.createBufferSource()
        source.buffer = audioBuffer
        source.connect(audioCtx.destination)
        currentSource = source
        source.onended = () => {
            currentSource = null
            isPlaying = false
            playNextChunk()
        }
        source.start()
    }

    navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
        if (!MediaRecorder.isTypeSupported('audio/webm'))
            return alert('Browser not supported')

        const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
        const socket = new WebSocket('ws://localhost:8000/ws')

        const analyser = audioCtx.createAnalyser()
        analyser.fftSize = 512
        const volumeData = new Uint8Array(analyser.frequencyBinCount)
        const micSource = audioCtx.createMediaStreamSource(stream)
        micSource.connect(analyser)

        setInterval(() => {
            analyser.getByteTimeDomainData(volumeData)
            let sum = 0
            for (let i = 0; i < volumeData.length; i++) {
                const sample = (volumeData[i] - 128) / 128
                sum += sample * sample
            }
            const rms = Math.sqrt(sum / volumeData.length)
            const ttsActive = isPlaying || audioQueue.length > 0
            const now = Date.now()

            if (rms > VOLUME_THRESHOLD) {
                lastTimeAboveThreshold = now; // Keep track of the last active audio frame
                
                if (ttsActive) {
                    if (!speechStartTimestamp) {
                        speechStartTimestamp = now;
                    } else if (now - speechStartTimestamp >= INTERRUPT_DELAY_MS) {
                        // Confirmed: User has been talking long enough
                        if (socket.readyState === 1) {
                            stopAudio()
                            socket.send("interrupt")
                        }
                    }
                }
            } else {
                // If it's quiet, check if we have exceeded the grace period
                if (lastTimeAboveThreshold && (now - lastTimeAboveThreshold > GRACE_PERIOD_MS)) {
                    // It has been dead silent for more than 300ms, reset the trackers
                    resetBargeInTrackers();
                }
            }
        }, 50)

        socket.onopen = () => {
            document.querySelector('#status').textContent = 'Connected'
            mediaRecorder.addEventListener('dataavailable', async (event) => {
                if (event.data.size > 0 && socket.readyState == 1) {
                    socket.send(event.data)
                }
            })
            mediaRecorder.start(250)
        }

        socket.onmessage = (message) => {
            if (message.data instanceof Blob) {
                message.data.arrayBuffer().then(buffer => {
                    audioQueue.push(buffer)
                    playNextChunk()
                })
            } else {
                const received = message.data
                if (!received) return

                if (received === 'stop_audio') {
                    stopAudio()
                    return
                }

                if (received.startsWith('ai:')) {
                    document.querySelector('#ai-response').textContent += received.slice(3)
                } else {
                    document.querySelector('#transcript').textContent += ' ' + received
                }
            }
        }

        socket.onclose = () => { console.log({ event: 'onclose' }) }
        socket.onerror = (error) => { console.log({ event: 'onerror', error }) }
    })
</script>
    </body>
</html>

"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        # BARGE-IN: asyncio.Event shared between the receive loop and the TTS task.
        # The receive loop sets it when "interrupt" arrives; the TTS task checks it
        # and cancels the Cartesia context when it sees the event is set.
        interrupt_event = asyncio.Event()

        async with dg_client.listen.v1.connect(
            model="nova-2",
            punctuate=True,
            interim_results=False,
            endpointing=500,
        ) as deepgram_socket:

            async def listen_for_transcripts():
                async for message in deepgram_socket:
                    if isinstance(message, ListenV1Results):
                        transcript = message.channel.alternatives[0].transcript
                        if transcript:

                            # Clear any leftover interrupt from a previous turn.
                            interrupt_event.clear()

                            # Step 1: Show transcript in browser.
                            await websocket.send_text(transcript)

                            # Step 2: Stream Groq AI reply word by word.
                            stream = await client.chat.completions.create(
                                messages=[
                                    {
                                        "role": "system",
                                        "content": "You are a helpful assistant. Reply in plain text, no markdown.",
                                    },
                                    {"role": "user", "content": transcript},
                                ],
                                model="llama-3.3-70b-versatile",
                                temperature=0.5,
                                stream=True,
                            )

                            full_response = ""
                            async for chunk in stream:
                                content = chunk.choices[0].delta.content
                                if content is not None:
                                    full_response += content
                                    await websocket.send_text(f"ai:{content}")

                            if not full_response:
                                continue

                            # Step 3: Call Cartesia TTS with the full response.
                            async with Cs_client.tts.websocket_connect() as tts_connection:
                                ctx = tts_connection.context(
                                    model_id="sonic-3.5",
                                    voice={
                                        "mode": "id",
                                        "id": "f786b574-daa5-4673-aa0c-cbe3e8534c02",
                                    },
                                    output_format={
                                        "container": "raw",
                                        "encoding": "pcm_f32le",
                                        "sample_rate": 44100,
                                    },
                                )
                                await ctx.push(full_response)
                                await ctx.no_more_inputs()

                                # BARGE-IN: Stream TTS audio to browser while also watching
                                # for an interrupt signal from the receive loop.
                                # We race two tasks: one streams audio, the other waits for
                                # the interrupt event. Whichever finishes first wins.
                                async def stream_audio():
                                    async for response in ctx.receive():
                                        if response.type == "chunk" and response.audio:
                                            await websocket.send_bytes(response.audio)
                                        elif response.type == "done":
                                            break

                                async def wait_for_interrupt():
                                    await interrupt_event.wait()

                                audio_task = asyncio.create_task(stream_audio())
                                interrupt_task = asyncio.create_task(
                                    wait_for_interrupt()
                                )

                                # Wait for either TTS to finish OR an interrupt to arrive.
                                done, pending = await asyncio.wait(
                                    [audio_task, interrupt_task],
                                    return_when=asyncio.FIRST_COMPLETED,
                                )

                                # Cancel whichever task didn't finish.
                                for task in pending:
                                    task.cancel()

                                # BARGE-IN: If interrupted, cancel the Cartesia context so it
                                # stops generating audio server-side, and tell the browser to
                                # drop any audio chunks already in the queue.
                                if interrupt_task in done:
                                    await ctx.cancel()
                                    await websocket.send_text("stop_audio")
                                    interrupt_event.clear()

            listener_task = asyncio.create_task(listen_for_transcripts())

            try:
                while True:
                    # BARGE-IN: Switch from receive_bytes() to receive() so we can handle
                    # both binary audio frames and the text "interrupt" signal on one socket.
                    message = await websocket.receive()

                    if "bytes" in message and message["bytes"]:
                        # Normal audio chunk from the browser mic — forward to Deepgram.
                        await deepgram_socket.send_media(message["bytes"])

                    elif "text" in message and message["text"] == "interrupt":
                        # Browser detected speech during TTS playback — signal the TTS task.
                        interrupt_event.set()

            finally:
                listener_task.cancel()

    except Exception as e:
        print(f"error : {e}")
