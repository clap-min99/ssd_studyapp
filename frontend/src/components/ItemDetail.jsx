import { useEffect, useState } from "react";
import { marked } from "marked";
import { api, auth, deepDiveApi } from "../api/client";
import Modal from "./Modal";

/** 기사/학습 카드를 눌렀을 때 뜨는 상세 팝업.
 *  카드 내용 + OpenAI 심화 해설(한 번 만들면 서버에 저장됨) + 메일 원문 전체. */
export default function ItemDetail({ kind, item, rawText, onClose }) {
  const [deepDive, setDeepDive] = useState(item.deep_dive);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [detail, setDetail] = useState(item);
  const [detailLoaded, setDetailLoaded] = useState(item.deep_dive !== undefined);
  const [detailError, setDetailError] = useState(null);
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    if (item.deep_dive !== undefined) return;
    let active = true;
    setDetailError(null);
    api.getContentDetail(kind, item.id)
      .then((data) => {
        if (!active) return;
        setDetail(data);
        setDeepDive(data.deep_dive);
        setDetailLoaded(true);
      })
      .catch((e) => active && setDetailError(e.message));
    return () => { active = false; };
  }, [kind, item.id, item.deep_dive, retry]);

  const generate = () => {
    setLoading(true);
    setError(null);
    deepDiveApi
      .generate(kind, item.id)
      .then((data) => {
        setDeepDive(data.deep_dive);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  return (
    <Modal onClose={onClose}>
      <h3 style={{ fontSize: 20, marginTop: 0 }}>{item.title ?? item.heading}</h3>
      {item.summary && <p className="digest-summary">{item.summary}</p>}
      {item.insight && <p className="insight">💡 {item.insight}</p>}
      {item.body && <p className="digest-summary">{item.body}</p>}

      <div className="term-detail-block">
        <p className="term-detail-label">AI 심화 해설</p>
        {!detailLoaded ? (
          detailError ? <p role="alert">{detailError} <button className="pill pill-button" onClick={() => setRetry((value) => value + 1)}>다시 시도</button></p>
            : <p role="status">해설을 불러오는 중...</p>
        ) : deepDive ? (
          <div className="lesson-content" dangerouslySetInnerHTML={{ __html: marked.parse(deepDive) }} />
        ) : auth.isLoggedIn() ? (
          <button className="pill pill-button pill-accent" onClick={generate} disabled={loading}>
            {loading ? "해설 만드는 중... (최대 1분)" : "AI로 자세히 풀어보기"}
          </button>
        ) : (
          <p className="status-message">로그인하면 AI 해설을 볼 수 있어요.</p>
        )}
        {error && <p className="status-message error">{error}</p>}
      </div>

      {(detail.source_text || detail.raw_text || rawText) && (
        <details className="term-detail-block">
          <summary className="term-detail-label">
            {/* source_text가 없는 예전 데이터는 메일 전체로 대체 */}
            {detail.source_text ? "메일 원문 보기" : "메일 원문 전체 보기"}
          </summary>
          <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit" }}>
            {detail.source_text || detail.raw_text || rawText}
          </pre>
        </details>
      )}
    </Modal>
  );
}
