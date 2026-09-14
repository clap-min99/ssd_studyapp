import { useState } from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import TodayFeed from "./pages/TodayFeed";
import Timeline from "./pages/Timeline";
import DigestDetail from "./pages/DigestDetail";
import Glossary from "./pages/Glossary";
import Review from "./pages/Review";
import Login from "./pages/Login";
import { auth } from "./api/client";
import "./App.css";

export default function App() {
  const [loggedIn, setLoggedIn] = useState(auth.isLoggedIn());

  if (!loggedIn) {
    return (
      <div className="app">
        <main className="main-content">
          <Login onLoggedIn={() => setLoggedIn(true)} />
        </main>
      </div>
    );
  }

  function handleLogout() {
    auth.logout();
    setLoggedIn(false);
  }

  return (
    <div className="app">
      <main className="main-content">
        <div className="topbar">
          <span className="topbar-username">{auth.getUsername()}</span>
          <button className="logout-link" onClick={handleLogout}>
            로그아웃
          </button>
        </div>

        <Routes>
          <Route path="/" element={<TodayFeed />} />
          <Route path="/timeline" element={<Timeline />} />
          <Route path="/digest/:id" element={<DigestDetail />} />
          <Route path="/glossary" element={<Glossary />} />
          <Route path="/review" element={<Review />} />
        </Routes>
      </main>

      <nav className="bottom-nav">
        <NavLink to="/" end className="nav-item">
          오늘
        </NavLink>
        <NavLink to="/timeline" className="nav-item">
          타임라인
        </NavLink>
        <NavLink to="/glossary" className="nav-item">
          용어사전
        </NavLink>
        <NavLink to="/review" className="nav-item">
          복습
        </NavLink>
      </nav>
    </div>
  );
}
