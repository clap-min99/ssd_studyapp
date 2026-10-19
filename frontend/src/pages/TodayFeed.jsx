import { useEffect, useState } from "react";
import { api, CATEGORY_BADGE_CLASS, CATEGORY_LABEL } from "../api/client";
import DigestView from "./DigestView";
import ItemDetail from "../components/ItemDetail";
import { isSafeWebUrl } from "../components/safeUrl.js";

const VIEWS = [
  { value: "", label: "오늘" },
  { value: "ssd", label: "SSD/NAND" },
  { value: "automotive", label: "자동차 SW" },
];

export default function TodayFeed() {
  const [digest, setDigest] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const [view, setView] = useState("");
  const [tags, setTags] = useState([]);
  const [tagsError, setTagsError] = useState(null);
  const [selectedTag, setSelectedTag] = useState(null);
  const [tagArticles, setTagArticles] = useState([]);
  const [articlesLoading, setArticlesLoading] = useState(false);
  const [articlesError, setArticlesError] = useState(null);
  const [selectedArticle, setSelectedArticle] = useState(null);

  const filteredTags = tags.filter((t) => t.category === view);
  const activeTag = filteredTags.find((t) => t.slug === selectedTag) ?? filteredTags[0];
  const activeSlug = activeTag?.slug;

  useEffect(() => {
    api.getLatestDigest().then(setDigest).catch((e) => setError(e.message)).finally(() => setLoading(false));
    api.getTags().then(setTags).catch((e) => setTagsError(e.message));
  }, []);

  useEffect(() => {
    if (!activeSlug) return;
    let active = true;
    setTagArticles([]);
    setArticlesLoading(true);
    setArticlesError(null);
    api.getTagArticles(activeSlug)
      .then((data) => active && setTagArticles(data))
      .catch((e) => active && setArticlesError(e.message))
      .finally(() => active && setArticlesLoading(false));
    return () => { active = false; };
  }, [activeSlug]);

  const changeView = (value) => {
    if (value === view) return;
    setView(value);
    setSelectedTag(null);
    setTagArticles([]);
    setSelectedArticle(null);
  };

  const selectTag = (tag) => {
    setSelectedTag(tag.slug);
    setSelectedArticle(null);
  };

  return (
    <div>
      <div className="view-switcher">
        {VIEWS.map((v) => (
          <button
            key={v.value}
            className={`pill pill-button ${view === v.value ? "pill-accent" : "pill-neutral"}`}
            onClick={() => changeView(v.value)}
          >
            {v.label}
          </button>
        ))}
      </div>

      {view === "" && (
        <>
          {loading && <p className="status-message">불러오는 중...</p>}
          {error && <p className="status-message error">{error}</p>}
          {!loading && !error && digest && <DigestView digest={digest} />}
          {!loading && !error && !digest && <p className="status-message">아직 저장된 다이제스트가 없어요.</p>}
        </>
      )}

      {view !== "" && (
        <div>
          {tagsError && <p className="status-message error">{tagsError}</p>}
          <div className="tag-row">
            {filteredTags.map((t) => (
              <button
                key={t.slug}
                className={`pill pill-button ${activeSlug === t.slug ? "pill-accent" : CATEGORY_BADGE_CLASS[t.category] ?? "pill-neutral"}`}
                onClick={() => selectTag(t)}
              >
                {t.name}
              </button>
            ))}
          </div>

          {activeTag && (
            <>
              <p className="status-message">{activeTag.description}</p>
              {articlesLoading && <p className="status-message">불러오는 중...</p>}
              {articlesError && <p className="status-message error">{articlesError}</p>}
              {tagArticles.map((a) => (
                <article key={a.id} className="card clickable" onClick={() => setSelectedArticle(a)}>
                  <span className={`badge ${CATEGORY_BADGE_CLASS[a.category] ?? ""}`}>
                    {CATEGORY_LABEL[a.category] ?? a.category}
                  </span>
                  <h3>{a.title}</h3>
                  {a.summary && <p>{a.summary}</p>}
                  {a.insight && <p className="insight">💡 {a.insight}</p>}
                  {a.links.length > 0 && (
                    <div className="links">
                      {a.links.filter(isSafeWebUrl).map((link) => (
                        <a key={link} href={link} target="_blank" rel="noreferrer" onClick={(e) => e.stopPropagation()}>
                          원문 링크
                        </a>
                      ))}
                    </div>
                  )}
                </article>
              ))}
            </>
          )}
        </div>
      )}
      {selectedArticle && (
        <ItemDetail
          key={selectedArticle.id}
          kind="article"
          item={selectedArticle}
          onClose={() => setSelectedArticle(null)}
        />
      )}
    </div>
  );
}
