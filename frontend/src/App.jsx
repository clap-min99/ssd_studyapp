import { NavLink, Route, Routes } from "react-router-dom";
import TodayFeed from "./pages/TodayFeed";
import Timeline from "./pages/Timeline";
import DigestDetail from "./pages/DigestDetail";
import Glossary from "./pages/Glossary";
import Review from "./pages/Review";
import "./App.css";

export default function App() {
  return (
    <div className="app">
      <main className="main-content">
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
