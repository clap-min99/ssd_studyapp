import { useState } from "react";
import { NavLink, Route, Routes, useLocation } from "react-router-dom";
import TodayFeed from "./pages/TodayFeed";
import Timeline from "./pages/Timeline";
import DigestDetail from "./pages/DigestDetail";
import Chapters from "./pages/Chapters";
import ChapterDetail from "./pages/ChapterDetail";
import LessonDetail from "./pages/LessonDetail";
import Glossary from "./pages/Glossary";
import Review from "./pages/Review";
import Login from "./pages/Login";
import Account from "./pages/Account";
import Privacy from './pages/Privacy';
import StreakBadge from "./components/StreakBadge";
import Wordmark from "./components/Wordmark";
import { auth } from "./api/client";
import "./App.css";

export default function App() {
  const location = useLocation();
  const [loggedIn, setLoggedIn] = useState(auth.isLoggedIn());
  const [streakVersion, setStreakVersion] = useState(0);
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
        <header className="brand-header">
          <NavLink to="/" className="brand-home" aria-label="SSD Tech Log 홈">
            <Wordmark />
          </NavLink>
          <div className="topbar-right">
            <NavLink className="topbar-username" to="/account" aria-label="계정 관리">
              {auth.getUsername()}
            </NavLink>
            <button className="logout-link" onClick={handleLogout}>
              로그아웃
            </button>
          </div>
        </header>
        <div className="topbar">
          <StreakBadge refreshKey={streakVersion} />
        </div>

        <Routes>
          <Route path="/account" element={<Account onDeleted={handleLogout} />} />
          <Route path="/" element={<TodayFeed />} />
          <Route path="/timeline" element={<Timeline />} />
          <Route path="/digest/:id" element={<DigestDetail />} />
          <Route path="/chapters" element={<Chapters />} />
          <Route path="/chapters/:slug" element={<ChapterDetail />} />
          <Route path="/chapters/:slug/lessons/:lessonId" element={<LessonDetail />} />
          <Route path="/glossary" element={<Glossary />} />
          <Route path="/privacy" element={<Privacy />} />
          <Route path="/review" element={<Review onAnswered={() => setStreakVersion((v) => v + 1)} />} />
        </Routes>
      </main>

      <nav className="bottom-nav">
        <NavLink to="/" end className={`nav-item${location.pathname.startsWith("/digest/") ? " active" : ""}`}>
          <span className="nav-icon">📰</span>
          오늘
        </NavLink>
        <NavLink to="/chapters" className="nav-item">
          <span className="nav-icon">📚</span>
          챕터
        </NavLink>
        <NavLink to="/glossary" className="nav-item">
          <span className="nav-icon">📖</span>
          용어사전
        </NavLink>
        <NavLink to="/review" className="nav-item">
          <span className="nav-icon">🔁</span>
          복습
        </NavLink>
          {/* <NavLink to="/categories" className="nav-item">
          <span className="nav-icon">🏷️</span>
          카테고리
        </NavLink> */}
      </nav>
    </div>
  );
}
