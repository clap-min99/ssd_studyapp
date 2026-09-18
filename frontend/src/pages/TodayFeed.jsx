import { useEffect, useState } from "react";
import { api } from "../api/client";
import DigestView from "./DigestView";

const CATEGORY_LABELS = { ssd: "SSD/NAND", automotive: "자동차 SW" };

export default function TodayFeed() {
  const [digest, setDigest] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const [tags, setTags] = useState([]);
  const [category, setCategory] = useState("");
  const [selectedTag, setSelectedTag] = useState(null);
  const [tagArticles, setTagArticles] = useState([]);

  useEffect(() => {
    api.getLatestDigest().then(setDigest).catch((e) => setError(e.message)).finally(() => setLoading(false));
    api.getTags().then(setTags);
  }, []);

  const handleCategoryChange = (e) => {
    setCategory(e.target.value);
    setSelectedTag(null);
    setTagArticles([]);
  };

  const handleTagChange = async (e) => {
    const slug = e.target.value;
    const tag = tags.find((t) => t.slug === slug);
    setSelectedTag(tag || null);
    setTagArticles(tag ? await api.getTagArticles(tag.slug) : []);
  };

  const filteredTags = tags.filter((t) => t.category === category);

  return (
    <div>
      <div className="category-browser">
        <select value={category} onChange={handleCategoryChange}>
          <option value="">카테고리로 찾아보기</option>
          {Object.entries(CATEGORY_LABELS).map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>

        {category && (
          <select value={selectedTag?.slug || ""} onChange={handleTagChange}>
            <option value="">태그 선택</option>
            {filteredTags.map((t) => (
              <option key={t.slug} value={t.slug}>{t.name}</option>
            ))}
          </select>
        )}

        {selectedTag && (
          <div className="card">
            <p className="status-message">{selectedTag.description}</p>
            {tagArticles.map((a) => (
              <div key={a.id} className="card">
                <h3>{a.title}</h3>
                <p>{a.summary}</p>
                {a.links?.length > 0 && (
                  <ul>
                    {a.links.map((url) => (
                      <li key={url}><a href={url} target="_blank" rel="noreferrer">{url}</a></li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {loading && <p className="status-message">불러오는 중...</p>}
      {error && <p className="status-message error">{error}</p>}
      {!loading && !error && digest && <DigestView digest={digest} />}
      {!loading && !error && !digest && <p className="status-message">아직 저장된 다이제스트가 없어요.</p>}
    </div>
  );
}