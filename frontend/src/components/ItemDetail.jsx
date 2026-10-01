import { useState } from "react";
import { marked } from "marked";
import { auth, deepDiveApi } from "../api/client";
import Modal from "./Modal";

/** 기사/학습 카드를 눌렀을 때 뜨는 상세 팝업.
 *  카드 내용 + Gemini 심화 해설(한 번 만들면 서버에 저장됨) + 메일 원문 전체. */
export default function ItemDetail({ kind, item, rawText, onClose }) {
  const [deepDive, setDeepDive] = useState(item.deep_dive);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const generate = () => {
    setLoading(true);
    setError(null);
    deepDiveApi
      .generate(kind, item.id)
      .then((data) => {
        item.deep_dive = data.deep_dive; // 팝업을 다시 열 때 재요청하지 않도록 목록 데이터에도 반영
        setDeepDive(data.deep_dive);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  return (
    <Modal onClose={onClose}>
      <h3 style={{ fontSize: 20, marginTop: 0 }}>{item.title ?? item.heading}</h3>
      {item.summary && <p>{item.summary}</p>}
      {item.insight && <p className="insight">💡 {item.insight}</p>}
      {item.body && <p>{item.body}</p>}

      <div className="term-detail-block">
        <p className="term-detail-label">AI 심화 해설</p>
        {deepDive ? (
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

      {(item.source_text || rawText) && (
        <details className="term-detail-block">
          <summary className="term-detail-label">
            {/* source_text가 없는 예전 데이터는 메일 전체로 대체 */}
            {item.source_text ? "메일 원문 보기" : "메일 원문 전체 보기"}
          </summary>
          <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit" }}>
            {item.source_text || rawText}
          </pre>
        </details>
      )}
    </Modal>
  );
}
