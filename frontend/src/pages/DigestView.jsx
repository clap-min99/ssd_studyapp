import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { CATEGORY_BADGE_CLASS, CATEGORY_LABEL } from "../api/client";
import TermDetail from "../components/TermDetail";
import DigestNotes from "../components/DigestNotes";
import ItemDetail from "../components/ItemDetail";
import DigestCalendar from "../components/DigestCalendar";
import { isSafeWebUrl } from "../components/safeUrl.js";

/** 다이제스트 상세 데이터를 받아서 렌더링하는 공용 컴포넌트.
 *  TodayFeed(최신 1건)와 DigestDetail(달력에서 고른 날짜)이 공유한다. */
export default function DigestView({ digest }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [calendarOpen, setCalendarOpen] = useState(false);
  const [selectedTermId, setSelectedTermId] = useState(null);
  const [selectedItem, setSelectedItem] = useState(null); // { kind, item }

  return (
    <div className="feed">
      <header className="feed-header">
        <div className="feed-date-row">
          <h1><button className="feed-date-button" onClick={() => setCalendarOpen(true)} aria-label={`${digest.date} 날짜 선택`} aria-haspopup="dialog" aria-expanded={calendarOpen}>
            <time dateTime={digest.date}>{digest.date}</time><span aria-hidden="true"> ▾</span>
          </button></h1>
          {location.pathname !== "/" && <Link className="pill pill-neutral" to="/">최신으로</Link>}
        </div>
        <p className="feed-subject">{digest.subject}</p>
      </header>

      {digest.articles.length > 0 && (
        <section>
          <h2>기사</h2>
          {digest.articles.map((a) => (
            <article
              key={a.id}
              className="card clickable"
              onClick={() => setSelectedItem({ kind: "article", item: a })}
            >
              <span className={`badge ${CATEGORY_BADGE_CLASS[a.category] ?? ""}`}>
                {CATEGORY_LABEL[a.category] ?? a.category}
              </span>
              <h3>{a.title}</h3>
              {a.summary && <p className="digest-summary">{a.summary}</p>}
              {a.insight && <p className="insight">💡 {a.insight}</p>}
              {a.links.length > 0 && (
                <div className="links">
                  {a.links.filter(isSafeWebUrl).map((link) => (
                    <a
                      key={link}
                      href={link}
                      target="_blank"
                      rel="noreferrer"
                      onClick={(e) => e.stopPropagation()}
                    >
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
          <h2>학습 콘텐츠</h2>
          {digest.learning_items.map((li) => (
            <article
              key={li.id}
              className="card clickable"
              onClick={() => setSelectedItem({ kind: "learning-item", item: li })}
            >
              <h3>{li.heading}</h3>
              <p className="digest-summary">{li.body}</p>
            </article>
          ))}
        </section>
      )}

      {digest.terms.length > 0 && (
        <section>
          <h2>이날의 용어</h2>
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

      {calendarOpen && <DigestCalendar selectedDate={digest.date} onClose={() => setCalendarOpen(false)} onSelect={(id) => {
        setCalendarOpen(false);
        navigate(`/digest/${id}`);
      }} />}

      {selectedTermId && (
        <TermDetail termId={selectedTermId} onClose={() => setSelectedTermId(null)} />
      )}

      {selectedItem && (
        <ItemDetail
          key={`${selectedItem.kind}-${selectedItem.item.id}`}
          {...selectedItem}
          rawText={digest.raw_text}
          onClose={() => setSelectedItem(null)}
        />
      )}

      <DigestNotes digestId={digest.id} />
    </div>
  );
}
