import { useState } from "react";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";

export default function App() {
  const [authed, setAuthed] = useState(
    !!localStorage.getItem("sensetrade.access") || !!localStorage.getItem("sensetrade.refresh")
  );

  return authed ? <DashboardPage /> : <LoginPage onLogin={() => setAuthed(true)} />;
}
