# backend/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or your mobile app’s domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    buddy_id: str
    message: str

@app.get("/")
def home():
    return {"status": "Build-A-Buddy backend running"}

@app.post("/chat")
def chat(req: ChatRequest):
    # temporary stub — will connect to ML logic later
    reply = f"Your buddy ({req.buddy_id}) says: '{req.message[::-1]}'"
    return {"reply": reply}
