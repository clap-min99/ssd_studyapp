import { useEffect, useState } from "react";
import { api, CATEGORY_BADGE_CLASS } from "../api/client";
import TermDetail from "../components/TermDetail";

const FAMILIARITY_LABEL = {
  new: "처음 봄",
  familiar: "익숙함",
  mastered: "설명 가능",
};

const CONCEPT_VIEWS = [
  { value: "", label: "전체" },
  { value: "ssd", label: "SSD/NAND" },
  { value: "automotive", label: "자동차 SW" },
];

export default function Glossary() {
  const [mode, setMode] = useState("term"); // "term" | "concept"

  // --- 용어 ---
  const [terms, setTerms] = useState([]);
  const [query, setQuery] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedTermId, setSelectedTermId] = useState(null);

  // --- 개념: 전체 목록 ---
  const [concepts, setConcepts] = useState([]);
  const [conceptsLoaded, setConceptsLoaded] = useState(false);

  // --- 개념: 카테고리/태그 필터 ---
  const [conceptView, setConceptView] = useState(""); // "" | "ssd" | "automotive"
  const [tags, setTags] = useState([]);
  const [selectedTag, setSelectedTag] = useState(null);
  const [tagConcepts, setTagConcepts] = useState([]);

  useEffect(() => {
    let active = true;
    api
      .getTerms()
      .then((data) => active && setTerms(data))
      .catch((e) => active && setError(e.message))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (mode === "concept" && !conceptsLoaded) {
      api.getLearningItems().then((data) => {
        setConcepts(data);
        setConceptsLoaded(true);
      });
    }
    if (mode === "concept" && tags.length === 0) {
      api.getTags().then(setTags);
    }
  }, [mode, conceptsLoaded, tags.length]);

  const filtered = terms.filter(
    (t) =>
      t.term.toLowerCase().includes(query.toLowerCase()) ||
      t.meaning.toLowerCase().includes(query.toLowerCase())
  );

  const filteredTags = tags.filter((t) => t.category === conceptView);

  const changeConceptView = (value) => {
    setConceptView(value);
    setSelectedTag(null);
    setTagConcepts([]);
  };

  const selectConceptTag = async (tag) => {
    setSelectedTag(tag);
    setTagConcepts(await api.getTagLearningItems(tag.slug));
  };

  return (
    <div className="glossary">
      <h1>{mode === "term" ? "용어 사전" : "개념 모음"}</h1>

      <div className="view-switcher">
        <button
          className={`pill pill-button ${mode === "term" ? "pill-accent" : "pill-neutral"}`}
          onClick={() => setMode("term")}
        >
          용어
        </button>
        <button
          className={`pill pill-button ${mode === "concept" ? "pill-accent" : "pill-neutral"}`}
          onClick={() => setMode("concept")}
        >
          개념
        </button>
      </div>

      {mode === "term" && (
        <>
          <input
            className="search-input"
            placeholder="용어 검색..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          {loading && <p className="status-message">불러오는 중...</p>}
          {error && <p className="status-message error">{error}</p>}
          {!loading && !error && filtered.length === 0 && (
            <p className="status-message">검색 결과가 없어요.</p>
          )}
          {!loading &&
            !error &&
            filtered.map((t) => (
              <article
                key={t.id}
                className="card term-card clickable"
                onClick={() => setSelectedTermId(t.id)}
              >
                <div className="term-card-header">
                  <h3>{t.term}</h3>
                  <span className="badge small">{FAMILIARITY_LABEL[t.familiarity]}</span>
                </div>
                <p>{t.meaning}</p>
                {t.first_seen_date && (
                  <p className="term-source">처음 나온 날: {t.first_seen_date}</p>
                )}
              </article>
            ))}
        </>
      )}

      {mode === "concept" && (
        <>
          <div className="view-switcher">
            {CONCEPT_VIEWS.map((v) => (
              <button
                key={v.value}
                className={`pill pill-button ${conceptView === v.value ? "pill-accent" : "pill-neutral"}`}
                onClick={() => changeConceptView(v.value)}
              >
                {v.label}
              </button>
            ))}
          </div>

          {conceptView === "" ? (
            !conceptsLoaded ? (
              <p className="status-message">불러오는 중...</p>
            ) : concepts.length === 0 ? (
              <p className="status-message">아직 모아둔 개념이 없어요.</p>
            ) : (
              concepts.map((c) => (
                <article key={c.id} className="card">
                  <h3>{c.heading}</h3>
                  <p>{c.body}</p>
                </article>
              ))
            )
          ) : (
            <>
              <div className="tag-row">
                {filteredTags.map((t) => (
                  <button
                    key={t.slug}
                    className={`pill pill-button ${
                      selectedTag?.slug === t.slug ? "pill-accent" : CATEGORY_BADGE_CLASS[t.category] ?? "pill-neutral"
                    }`}
                    onClick={() => selectConceptTag(t)}
                  >
                    {t.name}
                  </button>
                ))}
              </div>

              {selectedTag && (
                <>
                  <p className="status-message">{selectedTag.description}</p>
                  {tagConcepts.map((c) => (
                    <article key={c.id} className="card">
                      <h3>{c.heading}</h3>
                      <p>{c.body}</p>
                    </article>
                  ))}
                </>
              )}
            </>
          )}
        </>
      )}

      {selectedTermId && (
        <TermDetail termId={selectedTermId} onClose={() => setSelectedTermId(null)} />
      )}
    </div>
  );
}