from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.ai.websocket import interview_socket
from app.ai.websocket import interview_socket
from app.db.init import init_db
from app.routes import auth, adminroutes, guest,interviewroute



app = FastAPI(title="Interview Preparation App")
@app.on_event("startup")
def on_startup():
    init_db()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000","http://127.0.0.1:8000","http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.websocket("/ws/interview")
async def interview(ws: WebSocket):
    await interview_socket(ws)
app.include_router(auth.router)
app.include_router(adminroutes.router)
app.include_router(guest.router)

app.include_router(interviewroute.router)
@app.get("/")
def read_root():
    return {"message": "Welcome to the Interview Preparation App!"}



