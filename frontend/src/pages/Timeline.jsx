import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, CATEGORY_BADGE_CLASS, CATEGORY_LABEL } from "../api/client";

export default function Timeline() {
  const [digests, setDigests] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getDigestList()
      .then(setDigests)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="timeline">
      <header className="page-header">
        <h1>타임라인</h1>
      </header>
      {loading && <p className="status-message">불러오는 중...</p>}
      {error && <p className="status-message error">{error}</p>}
      {!loading && !error && digests.length === 0 && <p className="status-message">아직 쌓인 기록이 없어요.</p>}
      {!loading && !error && digests.map((d) => (
        <Link to={`/digest/${d.id}`} key={d.id} className="card timeline-item">
          <div className="timeline-date">{d.date}</div>
          <div className="timeline-meta">
            <span>{d.article_count}건의 기사</span>
            {d.categories.map((c) => (
              <span key={c} className={`badge small ${CATEGORY_BADGE_CLASS[c] ?? ""}`}>
                {CATEGORY_LABEL[c] ?? c}
              </span>
            ))}
          </div>
        </Link>
      ))}
    </div>
  );
}
