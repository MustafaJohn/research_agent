from __future__ import annotations

import requests
import streamlit as st

API_BASE = "http://localhost:7000"

st.set_page_config(page_title="Appointment Chatbot Demo", page_icon="🤖", layout="centered")
st.title("🤖 AI Appointment Booking Demo")


def init_state() -> None:
    defaults = {
        "token": "",
        "session_id": "",
        "messages": [
            {
                "role": "assistant",
                "content": "Hi! I can help book an appointment. Start with `service: haircut`.",
            }
        ],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def signup(name: str, email: str, password: str) -> str:
    resp = requests.post(
        f"{API_BASE}/api/auth/signup",
        json={"name": name, "email": email, "password": password},
        timeout=15,
    )
    if resp.status_code >= 400:
        return resp.json().get("detail", "Signup failed")
    return "Signup successful. Please log in."


def login(email: str, password: str) -> str:
    resp = requests.post(
        f"{API_BASE}/api/auth/login",
        json={"email": email, "password": password},
        timeout=15,
    )
    if resp.status_code >= 400:
        return resp.json().get("detail", "Login failed")
    st.session_state.token = resp.json()["token"]
    return "Login successful"


def ensure_chat_session() -> str:
    if st.session_state.session_id:
        return st.session_state.session_id
    resp = requests.post(
        f"{API_BASE}/api/chatbot/token",
        headers={"Authorization": f"Bearer {st.session_state.token}"},
        json={},
        timeout=15,
    )
    resp.raise_for_status()
    session_id = resp.json()["sessionId"]
    st.session_state.session_id = session_id
    return session_id


def send_message(text: str) -> str:
    session_id = ensure_chat_session()
    resp = requests.post(
        f"{API_BASE}/api/chatbot/message",
        headers={"Authorization": f"Bearer {st.session_state.token}"},
        json={
            "session_id": session_id,
            "message": text,
            "history": st.session_state.messages,
        },
        timeout=30,
    )
    if resp.status_code >= 400:
        return f"Error: {resp.json().get('detail', 'chat failed')}"
    return resp.json().get("reply", "No reply")


init_state()

if not st.session_state.token:
    st.subheader("Authentication")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email", value="demo@example.com", key="login_email")
        password = st.text_input("Password", value="password123", type="password", key="login_password")
        if st.button("Login"):
            st.info(login(email, password))

    with tab2:
        name = st.text_input("Name", value="Demo User", key="signup_name")
        s_email = st.text_input("Email", value="demo@example.com", key="signup_email")
        s_password = st.text_input("Password", value="password123", type="password", key="signup_password")
        if st.button("Create account"):
            st.info(signup(name, s_email, s_password))

else:
    if st.button("Logout"):
        st.session_state.token = ""
        st.session_state.session_id = ""
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hi! I can help book an appointment. Start with `service: haircut`.",
            }
        ]
        st.rerun()

    st.subheader("Chat")
    for m in st.session_state.messages:
        speaker = "You" if m["role"] == "user" else "Assistant"
        st.markdown(f"**{speaker}:** {m['content']}")

    user_input = st.text_input("Your message", placeholder="Try: date: 2026-01-03")
    if st.button("Send") and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        assistant_reply = send_message(user_input.strip())
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
        st.rerun()
