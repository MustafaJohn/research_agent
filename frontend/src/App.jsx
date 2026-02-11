import { useState } from "react";
import AuthForm from "./components/AuthForm";
import ChatWindow from "./components/ChatWindow";

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("demo_jwt") || "");

  function handleLoggedIn(nextToken) {
    localStorage.setItem("demo_jwt", nextToken);
    setToken(nextToken);
  }

  function handleLogout() {
    localStorage.removeItem("demo_jwt");
    setToken("");
  }

  return (
    <main className="container">
      <h1>AI Appointment Booking Demo</h1>
      {!token ? (
        <AuthForm onLoggedIn={handleLoggedIn} />
      ) : (
        <>
          <button className="logout" onClick={handleLogout}>Logout</button>
          <ChatWindow token={token} />
        </>
      )}
    </main>
  );
}
