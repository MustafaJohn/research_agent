import { useState } from "react";

const API_BASE = "http://localhost:4000";

export default function AuthForm({ onLoggedIn }) {
  const [mode, setMode] = useState("login");
  const [name, setName] = useState("Demo User");
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("password123");
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    const endpoint = mode === "signup" ? "/api/auth/signup" : "/api/auth/login";
    const payload = mode === "signup" ? { name, email, password } : { email, password };

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Authentication failed");
      }

      if (mode === "signup") {
        setMode("login");
        return;
      }

      onLoggedIn(data.token);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h2>{mode === "login" ? "Login" : "Create account"}</h2>
      {mode === "signup" && (
        <label>
          Name
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
      )}
      <label>
        Email
        <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required />
      </label>
      <label>
        Password
        <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" required />
      </label>
      {error && <p className="error">{error}</p>}
      <button type="submit">{mode === "login" ? "Login" : "Sign up"}</button>
      <button type="button" className="secondary" onClick={() => setMode(mode === "login" ? "signup" : "login")}> 
        {mode === "login" ? "Need an account?" : "Already have an account?"}
      </button>
    </form>
  );
}
