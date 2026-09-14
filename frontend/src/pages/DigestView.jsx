import { useState } from "react";
import { CATEGORY_LABEL } from "../api/client";
import TermDetail from "../components/TermDetail";

/** 다이제스트 상세 데이터를 받아서 렌더링하는 공용 컴포넌트.
 *  TodayFeed(최신 1건)와 DigestDetail(타임라인에서 클릭한 특정 날짜)이 공유한다. */
export default function DigestView({ digest }) {
  const [selectedTermId, setSelectedTermId] = useState(null);

  return (
    <div className="feed">
      <header className="feed-header">
        <h1>{digest.date}</h1>
        <p className="feed-subject">{digest.subject}</p>
      </header>

      {digest.articles.length > 0 && (
        <section>
          <h2>기사</h2>
          {digest.articles.map((a) => (
            <article key={a.id} className="card">
              <span className="badge">{CATEGORY_LABEL[a.category] ?? a.category}</span>
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
        </section>
      )}

      {digest.learning_items.length > 0 && (
        <section>
          <h2>오늘의 학습 콘텐츠</h2>
          {digest.learning_items.map((li) => (
            <article key={li.id} className="card">
              <h3>{li.heading}</h3>
              <p>{li.body}</p>
            </article>
          ))}
        </section>
      )}

      {digest.terms.length > 0 && (
        <section>
          <h2>새로운 용어</h2>
          {digest.terms.map((t) => (
            <article
              key={t.id}
              className="card term-card clickable"
              onClick={() => setSelectedTermId(t.id)}
            >
              <h3>{t.term}</h3>
              <p>{t.meaning}</p>
            </article>
          ))}
        </section>
      )}

      {selectedTermId && (
        <TermDetail termId={selectedTermId} onClose={() => setSelectedTermId(null)} />
      )}
    </div>
  );
}
