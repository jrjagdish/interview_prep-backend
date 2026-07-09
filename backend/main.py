from dotenv import load_dotenv

load_dotenv()  # must run before any other imports that read os.getenv

import asyncio
import json
import time
import uuid
from contextlib import asynccontextmanager
from fastapi import WebSocket, FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from groq import AsyncGroq
import os
import jwt
from deepgram import AsyncDeepgramClient
from deepgram.listen import ListenV1Results
from cartesia import AsyncCartesia
from sqlalchemy.orm import Session
from routes import router, JWT_SECRET, JWT_ALGORITHM
from db import get_db
from models import Interview, Profile, utcnow
import interview_session
from report import generate_report, upload_report
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_URL"),
    send_default_pii=True,
    # Enable sending logs to Sentry
    enable_logs=True,
)

deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")
client = AsyncGroq(api_key=groq_api_key)
dg_client = AsyncDeepgramClient(api_key=deepgram_api_key)
Cs_client = AsyncCartesia(api_key=os.getenv("CARTESIA_API_KEY"))


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router=router)


@app.get("/")
async def get():
    return {"working good"}


FAREWELL_TEXT = (
    "That's all the time we have for today. Thank you so much for your responses "
    "— this concludes the interview."
)

# How recently audio must have arrived for the candidate to be considered
# "still speaking" when the timer runs out, and the hard cap on how long the
# watchdog will wait for them to finish before force-ending anyway.
SPEAKING_GRACE_SECONDS = 2.0
MAX_GRACE_WAIT_SECONDS = 15.0


async def _send_ctrl(websocket: WebSocket, payload: dict) -> None:
    try:
        await websocket.send_text(f"ctrl:{json.dumps(payload)}")
    except Exception:
        pass


async def _end_interview(db: Session, interview_id: str) -> None:
    messages = await interview_session.get_messages(interview_id)
    interview = await asyncio.to_thread(
        lambda: db.query(Interview).filter(Interview.id == interview_id).first()
    )
    if interview is not None and interview.status == "active":
        interview.conversation_data = messages
        interview.status = "completed"
        interview.concluded_at = utcnow()
        await asyncio.to_thread(db.commit)

        if messages:
            try:
                report_data = await generate_report(messages, interview.job_role)
                interview.score = report_data.get("total_score")
                interview.report_url = upload_report(report_data, str(interview.id))
                await asyncio.to_thread(db.commit)
            except Exception as e:
                sentry_sdk.capture_exception(e)
                print(f"report generation error: {e}")

    await interview_session.end_session(interview_id)


async def _end_with_farewell(
    websocket: WebSocket, db: Session, interview_id: str
) -> None:
    """Says a short goodbye over TTS, then persists to DB and closes the socket.
    Used for every timer-driven end so the candidate isn't just cut off."""
    await _send_ctrl(websocket, {"type": "time_up"})
    try:
        await websocket.send_text(f"ai:{FAREWELL_TEXT}")
        await interview_session.append_message(interview_id, "assistant", FAREWELL_TEXT)

        async with Cs_client.tts.websocket_connect() as tts_connection:
            ctx = tts_connection.context(
                model_id="sonic-3.5",
                voice={"mode": "id", "id": "f786b574-daa5-4673-aa0c-cbe3e8534c02"},
                output_format={
                    "container": "raw",
                    "encoding": "pcm_f32le",
                    "sample_rate": 44100,
                },
            )
            await ctx.push(FAREWELL_TEXT)
            await ctx.no_more_inputs()
            async for response in ctx.receive():
                if response.type == "chunk" and response.audio:
                    await websocket.send_bytes(response.audio)
                elif response.type == "done":
                    break
    except Exception as e:
        print(f"farewell tts error: {e}")

    await _end_interview(db, interview_id)
    try:
        await websocket.close()
    except Exception:
        pass


@app.websocket("/ws/{interview_id}")
async def websocket_endpoint(
    websocket: WebSocket, interview_id: str, db: Session = Depends(get_db)
):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4401)
        return

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("missing sub")
    except Exception:
        await websocket.close(code=4401)
        return

    try:
        uuid.UUID(interview_id)
    except ValueError:
        await websocket.close(code=4400)
        return

    interview =await asyncio.to_thread(
        (
           lambda: db.query(Interview)
            .join(Profile, Interview.profile_id == Profile.id)
            .filter(Interview.id == interview_id, Profile.user_id == user_id)
            .first()
        )
    )
    if interview is None or not await interview_session.session_exists(interview_id):
        await websocket.close(code=4404)
        return
    if interview.status != "active":
        await websocket.close(code=4409)
        return

    await websocket.accept()

    remaining = await interview_session.get_remaining_seconds(interview_id)
    if remaining <= 0:
        await _end_with_farewell(websocket, db, interview_id)
        return

    history = await interview_session.get_messages(interview_id)
    if history:
        await _send_ctrl(websocket, {"type": "history", "messages": history})

    ended_event = asyncio.Event()
    # Updated on every audio chunk received from the browser so the watchdog
    # can tell whether the candidate is still mid-sentence when time runs out.
    last_audio_at = {"t": time.monotonic()}

    async def watchdog():
        await asyncio.sleep(await interview_session.get_remaining_seconds(interview_id))
        if ended_event.is_set():
            return

        # Give a candidate who's still speaking a short grace window to finish
        # their sentence instead of yanking the mic mid-word.
        grace_deadline = time.monotonic() + MAX_GRACE_WAIT_SECONDS
        while (
            time.monotonic() - last_audio_at["t"] < SPEAKING_GRACE_SECONDS
            and time.monotonic() < grace_deadline
        ):
            await asyncio.sleep(0.5)
            if ended_event.is_set():
                return

        ended_event.set()
        await _end_with_farewell(websocket, db, interview_id)

    watchdog_task = asyncio.create_task(watchdog())

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
                    if ended_event.is_set():
                        break
                    if isinstance(message, ListenV1Results):
                        transcript = message.channel.alternatives[0].transcript
                        if transcript:

                            # Clear any leftover interrupt from a previous turn.
                            interrupt_event.clear()

                            # Step 1: Show transcript in browser.
                            await websocket.send_text(transcript)
                            await interview_session.append_message(
                                interview_id, "user", transcript
                            )

                            remaining = await interview_session.get_remaining_seconds(
                                interview_id
                            )
                            if remaining <= 0:
                                ended_event.set()
                                await _end_with_farewell(websocket, db, interview_id)
                                break

                            is_final_turn = (
                                remaining <= interview_session.WARNING_THRESHOLD_SECONDS
                            )
                            just_warned = (
                                await interview_session.mark_warned(interview_id)
                                if is_final_turn
                                else False
                            )

                            job_role = await interview_session.get_job_role(
                                interview_id
                            )
                            system_content = (
                                "You are conducting a live job interview for the role of "
                                f"{job_role or 'the position'}. Ask one focused question at a "
                                "time, listen to the candidate's answer, and follow up "
                                "naturally. Reply in plain text, no markdown."
                            )
                            if is_final_turn:
                                system_content += (
                                    " Only about a minute remains in this interview. "
                                    "Briefly acknowledge the candidate's last answer, then ask "
                                    "exactly ONE final concluding question and tell them this "
                                    "is the last question of the interview."
                                )

                            turn_history = await interview_session.get_messages(
                                interview_id
                            )
                            groq_messages = [
                                {"role": "system", "content": system_content}
                            ]
                            groq_messages.extend(
                                {"role": m["role"], "content": m["content"]}
                                for m in turn_history
                            )

                            if just_warned:
                                await _send_ctrl(websocket, {"type": "final_question"})

                            # Step 2: Stream Groq AI reply word by word.
                            stream = await client.chat.completions.create(
                                messages=groq_messages,
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

                            await interview_session.append_message(
                                interview_id, "assistant", full_response
                            )

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

                            if ended_event.is_set():
                                try:
                                    await websocket.close()
                                except Exception:
                                    pass
                                break

            listener_task = asyncio.create_task(listen_for_transcripts())

            try:
                while not ended_event.is_set():
                    # BARGE-IN: Switch from receive_bytes() to receive() so we can handle
                    # both binary audio frames and the text "interrupt" signal on one socket.
                    # Raced against ended_event so a watchdog-triggered timeout wakes this
                    # loop up immediately instead of waiting on a receive() that may never
                    # arrive if the candidate has gone quiet.
                    receive_task = asyncio.create_task(websocket.receive())
                    ended_task = asyncio.create_task(ended_event.wait())
                    done, pending = await asyncio.wait(
                        [receive_task, ended_task], return_when=asyncio.FIRST_COMPLETED
                    )
                    for task in pending:
                        task.cancel()

                    if ended_task in done:
                        break

                    message = receive_task.result()

                    if "bytes" in message and message["bytes"]:
                        # Normal audio chunk from the browser mic — forward to Deepgram.
                        last_audio_at["t"] = time.monotonic()
                        await deepgram_socket.send_media(message["bytes"])

                    elif "text" in message and message["text"] == "interrupt":
                        # Browser detected speech during TTS playback — signal the TTS task.
                        interrupt_event.set()

            finally:
                listener_task.cancel()

    except Exception as e:
        # Network drop or client-initiated close lands here. The interview is left
        # "active" in Postgres and its Redis session keeps its TTL, so the candidate
        # can reconnect to the same interview_id and resume with full history intact.
        print(f"error : {e}")
    finally:
        watchdog_task.cancel()
