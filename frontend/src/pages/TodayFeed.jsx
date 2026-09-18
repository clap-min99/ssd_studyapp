import { useEffect, useState } from "react";
import { api, CATEGORY_BADGE_CLASS, CATEGORY_LABEL } from "../api/client";
import DigestView from "./DigestView";

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
  const [selectedTag, setSelectedTag] = useState(null);
  const [tagArticles, setTagArticles] = useState([]);

  useEffect(() => {
    api.getLatestDigest().then(setDigest).catch((e) => setError(e.message)).finally(() => setLoading(false));
    api.getTags().then(setTags);
  }, []);

  const changeView = (value) => {
    setView(value);
    setSelectedTag(null);
    setTagArticles([]);
  };

  const selectTag = async (tag) => {
    setSelectedTag(tag);
    setTagArticles(await api.getTagArticles(tag.slug));
  };

  const filteredTags = tags.filter((t) => t.category === view);

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
          <div className="tag-row">
            {filteredTags.map((t) => (
              <button
                key={t.slug}
                className={`pill pill-button ${selectedTag?.slug === t.slug ? "pill-accent" : CATEGORY_BADGE_CLASS[t.category] ?? "pill-neutral"}`}
                onClick={() => selectTag(t)}
              >
                {t.name}
              </button>
            ))}
          </div>

          {selectedTag && (
            <>
              <p className="status-message">{selectedTag.description}</p>
              {tagArticles.map((a) => (
                <article key={a.id} className="card">
                  <span className={`badge ${CATEGORY_BADGE_CLASS[a.category] ?? ""}`}>
                    {CATEGORY_LABEL[a.category] ?? a.category}
                  </span>
                  <h3>{a.title}</h3>
                  {a.summary && <p>{a.summary}</p>}
                  {a.insight && <p className="insight">💡 {a.insight}</p>}
                  {a.links.length > 0 && (
                    <div className="links">
                      {a.links.map((link) => (
                        <a key={link} href={link} target="_blank" rel="noreferrer">
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
    </div>
  );
}