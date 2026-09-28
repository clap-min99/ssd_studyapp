import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, CATEGORY_LABEL } from "../api/client";

const TRACKS = [
  { value: "ssd", label: "SSD/NAND" },
  { value: "automotive", label: "자동차 SW" },
];

/** 커리큘럼 챕터 목록. Tag 중 order > 0인 것만 학습 순서가 있는 챕터로 취급한다.
 *  트랙(카테고리)마다 order가 1부터 다시 시작하므로 트랙별로 나눠서 보여준다. */
export default function Chapters() {
  const [chapters, setChapters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [track, setTrack] = useState("ssd");
  const navigate = useNavigate();

  useEffect(() => {
    let active = true;
    api
      .getTags()
      .then((data) => {
        if (!active) return;
        const ordered = data.filter((t) => t.order > 0).sort((a, b) => a.order - b.order);
        setChapters(ordered);
      })
      .catch((e) => active && setError(e.message))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, []);

  const trackChapters = chapters.filter((c) => c.category === track);

  return (
    <div>
      <h1>챕터</h1>
      <p className="status-message">
        {CATEGORY_LABEL[track]}를 순서대로 공부하는 커리큘럼이에요.
      </p>

      <div className="view-switcher">
        {TRACKS.map((t) => (
          <button
            key={t.value}
            className={`pill pill-button ${track === t.value ? "pill-accent" : "pill-neutral"}`}
            onClick={() => setTrack(t.value)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {loading && <p className="status-message">불러오는 중...</p>}
      {error && <p className="status-message error">{error}</p>}

      {!loading && !error && trackChapters.length === 0 && (
        <p className="status-message">아직 이 트랙엔 챕터가 없어요.</p>
      )}

      {!loading &&
        !error &&
        trackChapters.map((c) => (
          <article
            key={c.slug}
            className="card clickable chapter-card"
            onClick={() => navigate(`/chapters/${c.slug}`)}
          >
            <span className="chapter-order-badge">{c.order}</span>
            <div className="chapter-card-body">
              <h3>{c.name}</h3>
              <p>{c.description}</p>
            </div>
          </article>
        ))}
    </div>
  );
}
