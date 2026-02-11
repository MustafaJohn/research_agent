from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

load_dotenv()

app = FastAPI(title="Python Backend API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN", "60"))
CHATBOT_TOKEN_SECRET = os.getenv("CHATBOT_TOKEN_SECRET", "chatbot-secret")
CHATBOT_TOKEN_EXPIRES_MIN = int(os.getenv("CHATBOT_TOKEN_EXPIRES_MIN", "5"))
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8000")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

USERS: Dict[str, Dict] = {}
CHAT_SESSIONS: Dict[str, Dict] = {}


class SignupRequest(BaseModel):
    name: str = Field(min_length=2)
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    token: str


class ChatTokenRequest(BaseModel):
    session_id: Optional[str] = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    session_id: str
    message: str
    history: List[ChatMessage] = Field(default_factory=list)


def _create_jwt(payload: dict, secret: str, expires_minutes: int) -> str:
    data = payload.copy()
    data["exp"] = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    return jwt.encode(data, secret, algorithm="HS256")


def _decode_jwt(token: str, secret: str) -> dict:
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    payload = _decode_jwt(creds.credentials, JWT_SECRET)
    user_id = payload.get("user_id")
    if not user_id or user_id not in USERS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return USERS[user_id]


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/auth/signup")
def signup(body: SignupRequest):
    if any(u["email"] == body.email for u in USERS.values()):
        raise HTTPException(status_code=409, detail="User already exists")

    user_id = str(uuid.uuid4())
    USERS[user_id] = {
        "id": user_id,
        "name": body.name,
        "email": body.email,
        "password_hash": pwd_context.hash(body.password),
        "business_id": "demo-business",
    }
    return {"id": user_id, "name": body.name, "email": body.email}


@app.post("/api/auth/login", response_model=TokenResponse)
def login(body: LoginRequest):
    user = next((u for u in USERS.values() if u["email"] == body.email), None)
    if not user or not pwd_context.verify(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = _create_jwt(
        {
            "user_id": user["id"],
            "email": user["email"],
            "business_id": user["business_id"],
        },
        JWT_SECRET,
        JWT_EXPIRES_MIN,
    )
    return TokenResponse(token=token)


@app.post("/api/chatbot/token")
def chatbot_token(body: ChatTokenRequest, current_user: dict = Depends(get_current_user)):
    session_id = body.session_id or str(uuid.uuid4())
    CHAT_SESSIONS[session_id] = {
        "id": session_id,
        "user_id": current_user["id"],
        "business_id": current_user["business_id"],
        "started_at": datetime.now(timezone.utc).isoformat(),
    }

    token = _create_jwt(
        {
            "scope": "chat:invoke",
            "session_id": session_id,
            "user_id": current_user["id"],
            "business_id": current_user["business_id"],
        },
        CHATBOT_TOKEN_SECRET,
        CHATBOT_TOKEN_EXPIRES_MIN,
    )
    return {
        "chatbotToken": token,
        "sessionId": session_id,
        "expiresInMinutes": CHATBOT_TOKEN_EXPIRES_MIN,
    }


@app.post("/api/chatbot/message")
async def chatbot_message(body: ChatRequest, current_user: dict = Depends(get_current_user)):
    if body.session_id not in CHAT_SESSIONS:
        raise HTTPException(status_code=404, detail="Unknown chat session")

    payload = {
        "session_id": body.session_id,
        "user_id": current_user["id"],
        "business_id": current_user["business_id"],
        "message": body.message,
        "history": [m.model_dump() for m in body.history],
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(f"{AI_SERVICE_URL}/chat", json=payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"AI service error: {exc}") from exc

    return response.json()
