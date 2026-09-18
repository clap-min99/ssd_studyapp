import { useState } from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import TodayFeed from "./pages/TodayFeed";
import Timeline from "./pages/Timeline";
import DigestDetail from "./pages/DigestDetail";
// import Categories from './pages/Categories';
import Glossary from "./pages/Glossary";
import Review from "./pages/Review";
import Login from "./pages/Login";
import StreakBadge from "./components/StreakBadge";
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
          <StreakBadge />
          <div className="topbar-right">
            <span className="topbar-username">{auth.getUsername()}</span>
            <button className="logout-link" onClick={handleLogout}>
              로그아웃
            </button>
          </div>
        </div>

        <Routes>
          <Route path="/" element={<TodayFeed />} />
          <Route path="/timeline" element={<Timeline />} />
          <Route path="/digest/:id" element={<DigestDetail />} />
          <Route path="/glossary" element={<Glossary />} />
          <Route path="/review" element={<Review />} />
          <Route path="/categories" element={<Categories />} />
        </Routes>
      </main>

      <nav className="bottom-nav">
        <NavLink to="/" end className="nav-item">
          <span className="nav-icon">📰</span>
          오늘
        </NavLink>
        <NavLink to="/timeline" className="nav-item">
          <span className="nav-icon">🗂️</span>
          타임라인
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
