import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { marked } from "marked";
import { api } from "../api/client";
import TermDetail from "../components/TermDetail";

const TABS = [
  { key: "lesson", label: "레슨" },
  { key: "terms", label: "관련 용어" },
  { key: "articles", label: "실제 사례" },
];

export default function ChapterDetail() {
  const { slug } = useParams();
  const navigate = useNavigate();

  const [chapter, setChapter] = useState(null);
  const [terms, setTerms] = useState([]);
  const [articles, setArticles] = useState([]);
  const [error, setError] = useState(null);
  const [tab, setTab] = useState("lesson");
  const [selectedTermId, setSelectedTermId] = useState(null);

  useEffect(() => {
    let active = true;
    setChapter(null);
    setError(null);
    setTab("lesson");

    Promise.all([
      api.getTagDetail(slug),
      api.getTagTerms(slug),
      api.getTagArticles(slug),
    ])
      .then(([chapterData, termsData, articlesData]) => {
        if (!active) return;
        setChapter(chapterData);
        setTerms(termsData);
        setArticles(articlesData);
      })
      .catch((e) => active && setError(e.message));

    return () => {
      active = false;
    };
  }, [slug]);

  const lessonHtml = useMemo(() => {
    if (!chapter?.lesson_body) return "";
    return marked.parse(chapter.lesson_body);
  }, [chapter?.lesson_body]);

  if (error) return <p className="status-message error">{error}</p>;
  if (!chapter) return <p className="status-message">불러오는 중...</p>;

  return (
    <div>
      <button className="pill pill-button pill-neutral" onClick={() => navigate("/chapters")}>
        ← 챕터 목록
      </button>

      <div className="chapter-header">
        <span className="chapter-order-badge">{chapter.order}</span>
        <div>
          <h1 style={{ marginBottom: 4 }}>{chapter.name}</h1>
          <p className="chapter-description">{chapter.description}</p>
        </div>
      </div>

      {chapter.prerequisite_slug && (
        <button
          className="chapter-prereq"
          onClick={() => navigate(`/chapters/${chapter.prerequisite_slug}`)}
        >
          ↳ 먼저 보면 좋은 챕터: <strong>{chapter.prerequisite_name}</strong>
        </button>
      )}

      <div className="view-switcher" style={{ marginTop: 18 }}>
        {TABS.map((t) => (
          <button
            key={t.key}
            className={`pill pill-button ${tab === t.key ? "pill-accent" : "pill-neutral"}`}
            onClick={() => setTab(t.key)}
          >
            {t.label}
            {t.key === "terms" && ` (${terms.length})`}
            {t.key === "articles" && ` (${articles.length})`}
          </button>
        ))}
      </div>

      {tab === "lesson" &&
        (chapter.lesson_body ? (
          <div className="lesson-content" dangerouslySetInnerHTML={{ __html: lessonHtml }} />
        ) : (
          <p className="status-message">레슨 콘텐츠는 아직 준비 중이에요.</p>
        ))}

      {tab === "terms" &&
        (terms.length === 0 ? (
          <p className="status-message">아직 연결된 용어가 없어요.</p>
        ) : (
          terms.map((t) => (
            <article
              key={t.id}
              className="card term-card clickable"
              onClick={() => setSelectedTermId(t.id)}
            >
              <h3>{t.term}</h3>
              <p>{t.meaning}</p>
            </article>
          ))
        ))}

      {tab === "articles" &&
        (articles.length === 0 ? (
          <p className="status-message">아직 이 챕터에 태그된 기사가 없어요.</p>
        ) : (
          articles.map((a) => (
            <article key={a.id} className="card">
              <h3>{a.title}</h3>
              <p>{a.summary}</p>
            </article>
          ))
        ))}

      {chapter.next_slug ? (
        <button
          className="btn-primary chapter-next-btn"
          onClick={() => navigate(`/chapters/${chapter.next_slug}`)}
        >
          다음 챕터: {chapter.next_name} →
        </button>
      ) : (
        <button className="btn-secondary chapter-next-btn" onClick={() => navigate("/chapters")}>
          마지막 챕터예요 — 목록으로
        </button>
      )}

      {selectedTermId && (
        <TermDetail termId={selectedTermId} onClose={() => setSelectedTermId(null)} />
      )}
    </div>
  );
}
