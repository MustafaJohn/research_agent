from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

import os

from langchain_openai import ChatOpenAI

app = FastAPI(title="Appointment AI Service")

APPOINTMENTS: Dict[str, Dict] = {}
LOG_FILE = Path(__file__).parent / "chat_logs.jsonl"


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    session_id: str
    user_id: str
    business_id: str
    message: str
    history: List[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    state: Dict


REQUIRED_FIELDS = ["service", "date", "time", "name", "phone"]


def _extract_state_from_history(history: List[ChatMessage]) -> Dict[str, Optional[str]]:
    state = {key: None for key in REQUIRED_FIELDS}
    for msg in history:
        text = msg.content.lower()
        if "service" in text and not state["service"]:
            state["service"] = msg.content.split(":")[-1].strip()
        if "date" in text and not state["date"]:
            state["date"] = msg.content.split(":")[-1].strip()
        if "time" in text and not state["time"]:
            state["time"] = msg.content.split(":")[-1].strip()
        if "name" in text and not state["name"]:
            state["name"] = msg.content.split(":")[-1].strip()
        if "phone" in text and not state["phone"]:
            state["phone"] = msg.content.split(":")[-1].strip()
    return state


def _mock_availability(date: str, time: str) -> bool:
    blocked_slots = {("2026-01-01", "10:00"), ("2026-01-02", "15:00")}
    return (date, time) not in blocked_slots


def _log_interaction(payload: Dict) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


def _generate_reply_with_llm(user_message: str, state: Dict[str, Optional[str]]) -> Optional[str]:
    if not os.getenv("OPENAI_API_KEY"):
        return None

    model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")
    model = ChatOpenAI(model=model_name, temperature=0)
    prompt = (
        "You are an appointment booking assistant. "
        "Given the user's latest message and extracted state, ask for only one missing field. "
        f"State: {state}. User message: {user_message}"
    )
    try:
        response = model.invoke(prompt)
        return response.content
    except Exception:
        return None


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    state = _extract_state_from_history(request.history)

    lower_msg = request.message.lower()
    for field in REQUIRED_FIELDS:
        if f"{field}:" in lower_msg:
            state[field] = request.message.split(":", 1)[1].strip()

    missing = [field for field in REQUIRED_FIELDS if not state[field]]

    if missing:
        llm_reply = _generate_reply_with_llm(request.message, state)
        reply = llm_reply or f"Please provide your {missing[0]} (example: {missing[0]}: value)."
    else:
        is_available = _mock_availability(state["date"], state["time"])
        if not is_available:
            reply = (
                "That time slot is unavailable. Please provide a different time "
                "(example: time: 11:00)."
            )
            state["time"] = None
        else:
            appointment_id = f"apt_{request.session_id[:8]}"
            APPOINTMENTS[appointment_id] = {
                "appointment_id": appointment_id,
                "session_id": request.session_id,
                "user_id": request.user_id,
                "business_id": request.business_id,
                "status": "confirmed",
                **state,
                "created_at": datetime.utcnow().isoformat()
            }
            reply = (
                f"Booked successfully! Appointment ID: {appointment_id}. "
                f"{state['service']} on {state['date']} at {state['time']}."
            )

    _log_interaction(
        {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": request.session_id,
            "user_id": request.user_id,
            "business_id": request.business_id,
            "message": request.message,
            "assistant_reply": reply,
            "state": state
        }
    )

    return ChatResponse(reply=reply, state=state)
