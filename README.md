# AI Interview Prep

A live, voice-based mock interview app. The candidate talks over a WebSocket; audio is
transcribed with Deepgram, an interview question/response is generated with Groq (Llama
3.3), and spoken back with Cartesia TTS. Interviews are timed, resumable after a
disconnect (state cached in Redis), and scored into a report at the end.

## Structure

```
deepgram/
├── backend/            FastAPI app
│   ├── main.py          App entrypoint, CORS, the /ws/{interview_id} interview socket
│   ├── routes.py        REST API: auth, profile, resume upload, interviews
│   ├── interview_session.py  Redis-backed session state (messages, timer, warnings)
│   ├── report.py        Post-interview scoring + report generation/upload
│   ├── models.py        SQLAlchemy models: User, Profile, Interview
│   ├── db.py             DB session/engine setup
│   ├── config.py        Cloudinary configuration
│   ├── redis_client.py  Redis client setup
│   ├── migrations/       Alembic migrations
│   └── requirements.txt
│
└── frontend/            Next.js (App Router) app
    ├── app/
    │   ├── page.tsx           Landing page
    │   ├── sign-in/, sign-up/ Auth pages
    │   ├── dashboard/         Past interviews list
    │   ├── profile/           Resume upload / profile
    │   └── interview/         Live interview UI (mic capture, transcript, TTS playback)
    ├── components/            UI components (landing sections, avatars, theme, auth guard)
    ├── context/AuthContext.tsx  Client-side auth state (JWT in localStorage)
    ├── hooks/                 useInterview, useInterviews, useUserSync
    └── lib/api.ts             Backend API client
```

## Stack

- **Backend**: FastAPI, SQLAlchemy + Alembic, PostgreSQL, Redis, JWT auth (bcrypt-hashed
  passwords), Cloudinary (resume/report uploads), Sentry
- **AI/voice**: Deepgram (speech-to-text), Groq / Llama 3.3 (interview dialogue),
  Cartesia (text-to-speech)
- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis
- API keys: [Deepgram](https://console.deepgram.com/), [Groq](https://console.groq.com/),
  [Cartesia](https://cartesia.ai/), [Cloudinary](https://cloudinary.com/), and optionally
  [Sentry](https://sentry.io/)

## Setup

### Backend

```bash
cd backend
python -m venv ../venv
../venv/Scripts/activate        # Windows
pip install -r requirements.txt

cp .env.example .env            # then fill in DATABASE_URL, JWT_SECRET, etc.
# also set DEEPGRAM_API_KEY, GROQ_API_KEY, CARTESIA_API_KEY,
# CLOUD_NAME / CLOUDINARY_API_KEY / CLOUDINARY_API_SECRET, SENTRY_URL (optional)

alembic upgrade head             # run DB migrations
uvicorn main:app --reload --port 8000
```

Backend env vars (see `backend/.env.example`):

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET` | Secret used to sign auth tokens |
| `REDIS_URL` | Redis connection (interview session cache), defaults to `localhost:6379/0` |
| `INTERVIEW_DURATION_SECONDS` | Hard cap on interview length (default 300s) |
| `DEEPGRAM_API_KEY` | Speech-to-text |
| `GROQ_API_KEY` | Interview question/response generation |
| `CARTESIA_API_KEY` | Text-to-speech |
| `CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` | Resume/report uploads |
| `SENTRY_URL` | Error tracking (optional) |

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Auth is plain email/password (JWT issued by the backend, stored client-side) — see
`context/AuthContext.tsx`. The `.env.local.example` file still lists Clerk keys from an
earlier iteration; they're unused and can be ignored.

## Running the app

1. Start PostgreSQL and Redis locally.
2. Start the backend: `uvicorn main:app --reload --port 8000` (from `backend/`).
3. Start the frontend: `npm run dev` (from `frontend/`).
4. Visit `http://localhost:3000`, register an account, and start an interview from
   `/interview`.

## How an interview works

1. `POST /api/interviews/start` creates an `Interview` row and a Redis session
   (`interview_session.py`), returning an `interview_id` and duration.
2. The frontend opens `ws://.../ws/{interview_id}?token=<jwt>`.
3. Mic audio streams to the backend, which forwards it to Deepgram for transcription.
4. Each transcript is appended to the Redis-cached conversation and sent to Groq for the
   next interviewer turn, streamed back to the browser and spoken via Cartesia TTS
   (with barge-in support if the candidate starts talking over the AI).
5. A per-interview watchdog ends the session when time runs out (with a grace period and
   spoken farewell), persists the transcript to Postgres, and generates a scored report
   (`report.py`) uploaded to Cloudinary.
6. Past interviews and reports are listed via `GET /api/interviews` and
   `GET /api/interviews/{id}`.
