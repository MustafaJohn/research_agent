import { useState } from "react";

const API_BASE = "http://localhost:4000";

export default function ChatWindow({ token }) {
  const [sessionId, setSessionId] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hi! I can book appointments. Start by sending `service: haircut` (or any service)."
    }
  ]);
  const [input, setInput] = useState("");
  const [error, setError] = useState("");

  async function ensureSession() {
    if (sessionId) {
      return sessionId;
    }

    const response = await fetch(`${API_BASE}/api/chatbot/token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({})
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Unable to create chat session");
    }
    setSessionId(data.sessionId);
    return data.sessionId;
  }

  async function sendMessage(e) {
    e.preventDefault();
    if (!input.trim()) {
      return;
    }

    const userMessage = { role: "user", content: input.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setError("");

    try {
      const sid = await ensureSession();
      const response = await fetch(`${API_BASE}/api/chatbot/message`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          sessionId: sid,
          message: userMessage.content,
          history: messages
        })
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Chat request failed");
      }

      setMessages((prev) => [...prev, { role: "assistant", content: data.reply }]);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card chat-card">
      <h2>Appointment Assistant</h2>
      <div className="chat-window">
        {messages.map((msg, idx) => (
          <div key={`${msg.role}-${idx}`} className={`bubble ${msg.role}`}>
            <strong>{msg.role === "assistant" ? "Bot" : "You"}:</strong> {msg.content}
          </div>
        ))}
      </div>
      {error && <p className="error">{error}</p>}
      <form className="composer" onSubmit={sendMessage}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Try: date: 2026-01-03"
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
