import { useEffect, useState } from "react";
import { api, auth, bookmarkApi, CATEGORY_BADGE_CLASS } from "../api/client";
import { Link } from "react-router-dom";
import TermDetail from "../components/TermDetail";
import ItemDetail from "../components/ItemDetail";

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
  const [selectedConcept, setSelectedConcept] = useState(null);
  const [conceptQuery, setConceptQuery] = useState("");
  const [conceptError, setConceptError] = useState(null);
  const [tagLoading, setTagLoading] = useState(false);
  const [tagError, setTagError] = useState(null);
  const [bookmarkIds, setBookmarkIds] = useState([]);
  const [bookmarksLoaded, setBookmarksLoaded] = useState(false);
  const [bookmarkError, setBookmarkError] = useState(null);
  const [savingBookmark, setSavingBookmark] = useState(null);
  const [bookmarksOnly, setBookmarksOnly] = useState(false);
  const loggedIn = auth.isLoggedIn();

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
    if (mode !== "concept") return;
    let active = true;
    Promise.all([api.getLearningItems(), api.getTags()])
      .then(([data, tagData]) => {
        if (!active) return;
        setConcepts(data);
        setTags(tagData);
        setConceptsLoaded(true);
      })
      .catch((e) => active && setConceptError(e.message));
    return () => { active = false; };
  }, [mode]);

  useEffect(() => {
    if (!selectedTag) return;
    let active = true;
    api.getTagLearningItems(selectedTag.slug)
      .then((data) => active && setTagConcepts(data))
      .catch((e) => active && setTagError(e.message))
      .finally(() => active && setTagLoading(false));
    return () => { active = false; };
  }, [selectedTag]);

  useEffect(() => {
    if (mode !== "concept" || !loggedIn) return;
    let active = true;
    bookmarkApi.getIds()
      .then((ids) => {
        if (!active) return;
        setBookmarkIds(ids);
        setBookmarksLoaded(true);
        setBookmarkError(null);
      })
      .catch((e) => active && setBookmarkError(e.message));
    return () => { active = false; };
  }, [mode, loggedIn]);

  const filtered = terms.filter(
    (t) =>
      t.term.toLowerCase().includes(query.toLowerCase()) ||
      t.meaning.toLowerCase().includes(query.toLowerCase())
  );

  const filteredTags = tags.filter((t) => t.category === conceptView);
  const searchWords = conceptQuery.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  const matchesConcept = (concept) => {
    const text = `${concept.heading ?? ""} ${concept.body ?? ""}`.toLocaleLowerCase();
    return searchWords.every((word) => text.includes(word))
      && (!bookmarksOnly || bookmarkIds.includes(concept.id));
  };
  const filteredConcepts = concepts.filter(matchesConcept);
  const filteredTagConcepts = tagConcepts.filter(matchesConcept);

  const changeConceptView = (value) => {
    setConceptView(value);
    setSelectedTag(null);
    setTagConcepts([]);
  };

  const selectConceptTag = (tag) => {
    if (selectedTag?.slug === tag.slug && !tagError) return;
    setTagLoading(true);
    setTagError(null);
    setTagConcepts([]);
    setSelectedTag(tagError ? { ...tag } : tag);
  };

  const toggleBookmark = async (concept) => {
    if (savingBookmark !== null) return;
    const saved = bookmarkIds.includes(concept.id);
    setSavingBookmark(concept.id);
    setBookmarkError(null);
    try {
      await bookmarkApi.set(concept.id, !saved);
      setBookmarkIds((ids) => saved ? ids.filter((id) => id !== concept.id) : [...ids, concept.id]);
    } catch (e) {
      setBookmarkError(e.message);
    } finally {
      setSavingBookmark(null);
    }
  };

  const renderConcept = (concept) => (
    <article key={concept.id} className="card">
      <div className="concept-card-header">
        <button className="concept-title" onClick={() => setSelectedConcept(concept)}>
          <h3>{concept.heading}</h3>
        </button>
        {loggedIn && (
          <button
            className={`pill pill-button ${bookmarkIds.includes(concept.id) ? "pill-accent" : "pill-neutral"}`}
            aria-label={`${concept.heading} 북마크 ${bookmarkIds.includes(concept.id) ? "해제" : "저장"}`}
            aria-pressed={bookmarkIds.includes(concept.id)}
            disabled={!bookmarksLoaded || savingBookmark !== null}
            onClick={() => toggleBookmark(concept)}
          >
            {savingBookmark === concept.id ? "저장 중…" : bookmarkIds.includes(concept.id) ? "★ 저장됨" : "☆ 저장"}
          </button>
        )}
      </div>
      <p className="digest-summary">{concept.body}</p>
      <button className="pill pill-button pill-neutral" onClick={() => setSelectedConcept(concept)}>
        자세히 보기
      </button>
    </article>
  );

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
          onClick={() => {
            setConceptError(null);
            setMode("concept");
          }}
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
          <input
            type="search"
            className="search-input"
            aria-label="개념 제목과 본문 검색"
            placeholder="개념 제목·본문 검색..."
            value={conceptQuery}
            onChange={(e) => setConceptQuery(e.target.value)}
          />
          {conceptError && <p className="status-message error">{conceptError}</p>}
          {loggedIn ? (
            <label className="bookmark-filter">
              <input type="checkbox" checked={bookmarksOnly} disabled={!bookmarksLoaded}
                onChange={(e) => setBookmarksOnly(e.target.checked)} />
              북마크한 개념만 보기
            </label>
          ) : (
            <p className="bookmark-hint"><Link to="/login">로그인</Link>하면 다시 공부할 개념을 북마크할 수 있어요.</p>
          )}
          {bookmarkError && <p role="alert" className="status-message error">{bookmarkError}</p>}
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
            conceptError ? null : !conceptsLoaded ? (
              <p className="status-message">불러오는 중...</p>
            ) : concepts.length === 0 ? (
              <p className="status-message">아직 모아둔 개념이 없어요.</p>
            ) : filteredConcepts.length === 0 ? (
              <p className="status-message">{bookmarksOnly ? "조건에 맞는 북마크가 없어요. 검색어나 필터를 바꿔보세요." : "검색 결과가 없어요. 다른 검색어로 찾아보세요."}</p>
            ) : (
              filteredConcepts.map(renderConcept)
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
                  {tagLoading && <p className="status-message">불러오는 중...</p>}
                  {tagError && <p className="status-message error">{tagError}</p>}
                  {!tagLoading && !tagError && filteredTagConcepts.length === 0 && (
                    <p className="status-message">
                      {tagConcepts.length === 0 ? "아직 이 태그에 모아둔 개념이 없어요." : bookmarksOnly ? "조건에 맞는 북마크가 없어요. 검색어나 필터를 바꿔보세요." : "검색 결과가 없어요. 다른 검색어로 찾아보세요."}
                    </p>
                  )}
                  {!tagLoading && !tagError && filteredTagConcepts.map(renderConcept)}
                </>
              )}
            </>
          )}
        </>
      )}

      {selectedTermId && (
        <TermDetail termId={selectedTermId} onClose={() => setSelectedTermId(null)} />
      )}
      {selectedConcept && (
        <ItemDetail
          key={selectedConcept.id}
          kind="learning-item"
          item={selectedConcept}
          onClose={() => setSelectedConcept(null)}
        />
      )}
    </div>
  );
}
