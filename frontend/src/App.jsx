import { useEffect, useState } from "react";
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
  const [sessionVersion, setSessionVersion] = useState(auth.getVersion());
  const [checkingSession, setCheckingSession] = useState(true);
  const [authError, setAuthError] = useState(null);
  const [loggingOut, setLoggingOut] = useState(false);
  const [streakVersion, setStreakVersion] = useState(0);
  useEffect(() => auth.subscribe(() => {
    setLoggedIn(auth.isLoggedIn());
    setSessionVersion(auth.getVersion());
  }), []);
  useEffect(() => {
    let active = true;
    auth.restoreSession().then(() => {
      if (active) { setLoggedIn(auth.isLoggedIn()); setCheckingSession(false); }
    }).catch((err) => { if (active) setAuthError(err.message); });
    return () => { active = false; };
  }, []);

  async function retrySession() {
    setAuthError(null);
    try {
      await auth.restoreSession();
      setLoggedIn(auth.isLoggedIn());
      setCheckingSession(false);
    } catch (err) { setAuthError(err.message); }
  }

  if (checkingSession) {
    return <div className="app"><main className="main-content">
      {authError ? <><p role="alert">{authError}</p><button onClick={retrySession}>다시 시도</button></> : <p role="status">로그인 상태 확인 중...</p>}
    </main></div>;
  }
  if (!loggedIn) {
    return (
      <div className="app">
        <main className="main-content">
          <Login onLoggedIn={() => setLoggedIn(true)} />
        </main>
      </div>
    );
  }

  async function handleLogout() {
    setLoggingOut(true);
    setAuthError(null);
    try {
      await auth.logout();
      setLoggedIn(false);
    } catch (err) { setAuthError(err.message); }
    finally { setLoggingOut(false); }
  }

  return (
    <div className="app" key={sessionVersion}>
      <main className="main-content">
        <header className="brand-header">
          <NavLink to="/" className="brand-home" aria-label="SSD Tech Log 홈">
            <Wordmark />
          </NavLink>
          <div className="topbar-right">
            <NavLink className="topbar-username" to="/account" aria-label="계정 관리">
              {auth.getUsername()}
            </NavLink>
            <button className="logout-link" onClick={handleLogout} disabled={loggingOut}>
              {loggingOut ? "로그아웃 중..." : "로그아웃"}
            </button>
          </div>
        </header>
        {authError && <p role="alert" className="status-message error">{authError}</p>}
        <div className="topbar">
          <StreakBadge refreshKey={streakVersion} />
        </div>

        <Routes>
          <Route path="/account" element={<Account onDeleted={() => setLoggedIn(false)} />} />
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
