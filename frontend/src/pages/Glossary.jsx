import { useEffect, useState } from "react";
import { api } from "../api/client";

const FAMILIARITY_LABEL = {
  new: "처음 봄",
  familiar: "익숙함",
  mastered: "설명 가능",
};

export default function Glossary() {
  const [terms, setTerms] = useState([]);
  const [query, setQuery] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getTerms()
      .then(setTerms)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const filtered = terms.filter(
    (t) =>
      t.term.toLowerCase().includes(query.toLowerCase()) ||
      t.meaning.toLowerCase().includes(query.toLowerCase())
  );

  if (loading) return <p className="status-message">불러오는 중...</p>;
  if (error) return <p className="status-message error">{error}</p>;

  return (
    <div className="glossary">
      <h1>용어 사전</h1>
      <input
        className="search-input"
        placeholder="용어 검색..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      {filtered.length === 0 ? (
        <p className="status-message">검색 결과가 없어요.</p>
      ) : (
        filtered.map((t) => (
          <article key={t.id} className="card term-card">
            <div className="term-card-header">
              <h3>{t.term}</h3>
              <span className="badge small">{FAMILIARITY_LABEL[t.familiarity]}</span>
            </div>
            <p>{t.meaning}</p>
            {t.relevance && <p className="insight">{t.relevance}</p>}
            {t.first_seen_date && (
              <p className="term-source">처음 나온 날: {t.first_seen_date}</p>
            )}
          </article>
        ))
      )}
    </div>
  );
}
