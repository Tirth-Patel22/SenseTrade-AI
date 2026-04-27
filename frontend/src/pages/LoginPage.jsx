import { useState } from "react";
import api from "../api/client";

export default function LoginPage({ onLogin }) {
  const [username, setUsername] = useState("admin1");
  const [password, setPassword] = useState("StrongPass123");
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const { data } = await api.post("auth/login/", { username, password });
      localStorage.setItem("sensetrade.access", data.access);
      localStorage.setItem("sensetrade.refresh", data.refresh);
      onLogin();
    } catch {
      setError("Invalid credentials");
    }
  };

  return (
    <form onSubmit={submit} className="mx-auto mt-24 max-w-sm space-y-3 rounded-lg border border-slate-700 bg-slate-900/70 p-5">
      <h1 className="text-lg font-semibold text-slate-100">SenseTrade Login</h1>
      <input className="w-full rounded bg-slate-800 p-2 text-slate-100" value={username} onChange={(e) => setUsername(e.target.value)} />
      <input type="password" className="w-full rounded bg-slate-800 p-2 text-slate-100" value={password} onChange={(e) => setPassword(e.target.value)} />
      {error && <p className="text-sm text-rose-400">{error}</p>}
      <button className="w-full rounded bg-cyan-500 p-2 font-semibold text-slate-900">Login</button>
    </form>
  );
}
