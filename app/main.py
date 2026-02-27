# from fastapi import FastAPI, WebSocket
# from fastapi.middleware.cors import CORSMiddleware
# from app.ai.websocket import interview_socket
# from app.ai.websocket import interview_socket
# from app.db.init import init_db
# from app.routes import auth, adminroutes, guest,interviewroute


# app = FastAPI(title="Interview Preparation App")
# @app.on_event("startup")
# def on_startup():
#     init_db()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "http://127.0.0.1:3000","http://127.0.0.1:8000","http://localhost:5173"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# @app.websocket("/ws/interview")
# async def interview(ws: WebSocket):
#     await interview_socket(ws)
# app.include_router(auth.router)
# app.include_router(adminroutes.router)
# app.include_router(guest.router)

# app.include_router(interviewroute.router)
# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the Interview Preparation App!"}
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import io
import httpx
import speech_recognition as sr
from gtts import gTTS
import requests
from app.core.config import settings
from pydub import AudioSegment


async def transcribe_audio(audio_bytes: bytes) -> str:
    if len(audio_bytes) < 100:  # Ignore tiny "noise" packets
        return ""

    async with httpx.AsyncClient() as client:
        try:
            # We use 'detect_language' and 'nova-2' for best results
            response = await client.post(
                "https://api.deepgram.com/v1/listen",
                headers={
                    "Authorization": f"Token {settings.DEEPGRAM_API_KEY}",
                    "Content-Type": "audio/webm",  # Most browsers use webm
                },
                params={"model": "nova-2", "smart_format": "true", "language": "en"},
                content=audio_bytes,
            )

            if response.status_code != 200:
                print(f"Deepgram Error: {response.status_code} - {response.text}")
                return ""

            res_json = response.json()
            transcript = res_json["results"]["channels"][0]["alternatives"][0][
                "transcript"
            ]
            return transcript

        except Exception as e:
            print(f"STT Exception: {e}")
            return ""


# def speak(text: str) -> bytes:
#     if not text.strip():
#         return b""
        
#     try:
#         url = "https://api.cartesia.ai/tts/bytes"
        
#         headers = {
#             "Authorization": f"Bearer {settings.CARTESIA_API_KEY}",
#             "Cartesia-Version": "2024-06-10",
#             "Content-Type": "application/json"
#         }
        
#         # This is a standard, widely available voice ID (Baritone/Guy)
#         # Using a fixed public ID is the "default" way for their REST API
#         payload = {
#             "transcript": text,
#             "model_id": "sonic-3",
#             "voice": {
#                 "mode": "id",
#                 "id": "6ccbfb76-1fc6-48f7-b71d-91ac6298247b" 
#             },
#             "output_format": {
#                 "container": "mp3",
#                 "sample_rate": 44100
#             }
#         }

#         r = requests.post(url, headers=headers, json=payload)
        
#         if r.status_code == 200:
#             print(f"Success: Generated {len(r.content)} bytes")
#             return r.content
#         else:
#             print(f"Cartesia Error {r.status_code}: {r.text}")
#             return b""

#     except Exception as e:
#         print(f"Exception in speak: {e}")
#         return b""


# app = FastAPI()



recongizer = sr.Recognizer()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()





# @app.websocket("/ws/{client_id}")
# async def websocket_endpoint(websocket: WebSocket, client_id: int):
#     await manager.connect(websocket)
#     try:
#         while True:
#             data = await websocket.receive_bytes()

#             text = await transcribe_audio(data)
#             await manager.send_personal_message(f"You said: {text}", websocket)
#             response_text = f"Echo: {text}"
#             audio_bytes = speak(response_text)

#             await websocket.send_bytes(audio_bytes)
#             await manager.broadcast(f"Client #{client_id} says: {text}")
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
#         await manager.broadcast(f"Client #{client_id} left the chat")

import io
import httpx
import asyncio
import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from app.core.config import settings

app = FastAPI()

# 1. Faster Async TTS Function
async def speak_async(text: str) -> bytes:
    if not text.strip():
        return b""
    
    # Using httpx.AsyncClient is significantly faster than requests.post
    async with httpx.AsyncClient() as client:
        try:
            url = "https://api.cartesia.ai/tts/bytes"
            headers = {
                "Authorization": f"Bearer {settings.CARTESIA_API_KEY}",
                "Cartesia-Version": "2024-06-10",
                "Content-Type": "application/json"
            }
            payload = {
                "transcript": text,
                "model_id": "sonic-english", # Sonic is their fastest model
                "voice": {
                    "mode": "id",
                    "id": "6ccbfb76-1fc6-48f7-b71d-91ac6298247b" 
                },
                "output_format": {
                    "container": "mp3",
                    "sample_rate": 44100
                }
            }

            # We don't use a timeout to prevent closing the connection early
            response = await client.post(url, headers=headers, json=payload, timeout=None)
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"Cartesia Error {response.status_code}: {response.text}")
                return b""
        except Exception as e:
            print(f"Exception in speak: {e}")
            return b""

# ... keep your ConnectionManager and get route the same ...
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Audio Chat</title>
        <style>
            body { font-family: sans-serif; margin: 20px; line-height: 1.6; }
            .recording { color: red; font-weight: bold; animation: blink 1s infinite; }
            @keyframes blink { 50% { opacity: 0; } }
            #messages { list-style-type: none; padding: 0; }
            #messages li { background: #f4f4f4; margin: 5px 0; padding: 10px; border-radius: 5px; }
            button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Audio WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        
        <button id="recordBtn">Start Recording</button>
        <p id="status">Status: Idle</p>

        <ul id='messages'></ul>

        <script>
            const client_id = Date.now();
            document.querySelector("#ws-id").textContent = client_id;
            
            // 1. Establish WebSocket
            const ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.binaryType = "arraybuffer"; 

            let mediaRecorder;
            let audioChunks = []; 
            const recordBtn = document.getElementById("recordBtn");
            const statusLabel = document.getElementById("status");

            // 2. Handle incoming data from FastAPI
            ws.onmessage = function(event) {
    if (event.data instanceof ArrayBuffer) {
        console.log("Audio bytes received. Size:", event.data.byteLength);
        
        // If the byte size is very small (like < 500), it's probably an error message, not audio
        if (event.data.byteLength < 500) {
            console.error("Received data is too small to be audio. Check server logs.");
            return;
        }

        const blob = new Blob([event.data], { type: 'audio/mpeg' });
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        
        audio.play().then(() => {
            console.log("Playback started successfully");
        }).catch(e => {
            console.error("Playback failed. This usually happens if you haven't clicked the page yet.", e);
        });
    }else {
                    const messages = document.getElementById('messages');
                    const message = document.createElement('li');
                    message.textContent = event.data;
                    messages.appendChild(message);
                }
            };

            // 3. Audio Capture Logic (Record -> Stop -> Send)
            async function toggleRecording() {
                if (mediaRecorder && mediaRecorder.state === "recording") {
                    // STOPPING
                    mediaRecorder.stop();
                    recordBtn.textContent = "Start Recording";
                    statusLabel.textContent = "Status: Processing...";
                    statusLabel.classList.remove("recording");
                } else {
                    // STARTING
                    try {
                        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                        mediaRecorder = new MediaRecorder(stream);
                        audioChunks = [];

                        mediaRecorder.ondataavailable = (event) => {
                            if (event.data.size > 0) {
                                audioChunks.push(event.data);
                            }
                        };

                        mediaRecorder.onstop = () => {
                            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                            console.log("Sending audio blob, size:", audioBlob.size);
                            
                            if (ws.readyState === WebSocket.OPEN) {
                                ws.send(audioBlob);
                            }
                        };

                        mediaRecorder.start(); 
                        recordBtn.textContent = "Stop & Send";
                        statusLabel.textContent = "Status: Recording...";
                        statusLabel.classList.add("recording");
                    } catch (err) {
                        console.error("Error accessing microphone:", err);
                        alert("Could not access microphone.");
                    }
                }
            }

            // Bind the function to the button
            recordBtn.onclick = toggleRecording;

            ws.onopen = () => console.log("WebSocket connected");
            ws.onclose = () => {
                statusLabel.textContent = "Status: Disconnected";
                recordBtn.disabled = true;
            };
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            # 1. Receive data
            data = await websocket.receive_bytes()

            # 2. Transcribe
            text = await transcribe_audio(data)
            
            if text.strip():
                # 3. Parallel Execution: Start TTS and Broadcast simultaneously
                # This saves the time it takes for the broadcast to finish
                audio_task = asyncio.create_task(speak_async(text))
                
                # Update the UI immediately with text
                await manager.send_personal_message(f"You said: {text}", websocket)
                
                # Wait for audio to be ready
                audio_bytes = await audio_task
                
                if audio_bytes:
                    await websocket.send_bytes(audio_bytes)
                
                # Broadcast in the background to not slow down the current user
                asyncio.create_task(manager.broadcast(f"Client #{client_id} says: {text}"))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")