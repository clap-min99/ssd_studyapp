import { useEffect, useState } from "react";
import { api, reviewApi } from "../api/client";

const VERDICT_LABEL = {
  correct: { text: "정확해요", className: "verdict-correct" },
  partial: { text: "방향은 맞아요", className: "verdict-partial" },
  wrong: { text: "다시 봐야 해요", className: "verdict-wrong" },
};

export default function Review() {
  const [terms, setTerms] = useState([]);
  const [index, setIndex] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [answer, setAnswer] = useState("");
  const [aiResult, setAiResult] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // StrictMode(개발모드)에서 effect가 두 번 실행되면서 첫 번째 shuffle 결과가
    // 잠깐 보였다가 두 번째로 바뀌는 현상을 막기 위한 가드
    let active = true;

    api
      .getTerms()
      .then((data) => {
        if (active) setTerms(shuffle(data));
      })
      .catch((e) => {
        if (active) setError(e.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  const current = terms[index];

  function shuffle(arr) {
    const copy = [...arr];
    for (let i = copy.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    return copy;
  }

  function goNext() {
    setRevealed(false);
    setAnswer("");
    setAiResult(null);
    setAiError(null);
    setIndex((i) => i + 1);
  }

  async function handleSelfGrade(familiarity) {
    try {
      await reviewApi.updateFamiliarity(current.id, familiarity);
    } catch (e) {
      // 저장 실패해도 복습 흐름은 막지 않는다 — 다음 카드로 진행 가능하게
      console.error(e);
    }
    goNext();
  }

  async function handleAiCheck() {
    if (!answer.trim()) return;
    setAiLoading(true);
    setAiError(null);
    try {
      const result = await reviewApi.checkAnswer(current.id, answer);
      setAiResult(result);
    } catch (e) {
      setAiError(e.message);
    } finally {
      setAiLoading(false);
    }
  }

  if (loading) return <p className="status-message">불러오는 중...</p>;
  if (error) return <p className="status-message error">{error}</p>;
  if (terms.length === 0) return <p className="status-message">아직 복습할 용어가 없어요.</p>;

  if (index >= terms.length) {
    return (
      <div className="review">
        <h1>복습 끝!</h1>
        <p className="status-message">오늘 준비된 {terms.length}개 카드를 다 봤어요.</p>
        <button className="btn-primary" onClick={() => { setIndex(0); setTerms(shuffle(terms)); }}>
          다시 처음부터
        </button>
      </div>
    );
  }

  return (
    <div className="review">
      <div className="review-topbar">
        <span className="pill pill-neutral">전체 {terms.length}개</span>
        <span className="pill pill-accent">{index + 1} / {terms.length}</span>
      </div>

      <div className="flashcard">
        <h2>{current.term}</h2>

        {!revealed ? (
          <>
            <textarea
              className="answer-input"
              placeholder="이 용어, 내 언어로 설명해보기..."
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              rows={3}
            />
            <button className="btn-primary" onClick={() => setRevealed(true)}>
              정답 확인
            </button>
          </>
        ) : (
          <>
            <p className="answer-preview">{answer || "(답을 안 쓰고 정답부터 봤어요)"}</p>

            <div className="card meaning-card">
              <p>{current.meaning}</p>
              {current.relevance && <p className="insight">{current.relevance}</p>}
            </div>

            {answer.trim() && !aiResult && (
              <button className="btn-secondary" onClick={handleAiCheck} disabled={aiLoading}>
                {aiLoading ? "첨삭 중..." : "AI 첨삭 받기"}
              </button>
            )}

            {aiError && <p className="status-message error">{aiError}</p>}

            {aiResult && (
              <div className={`ai-feedback ${VERDICT_LABEL[aiResult.verdict]?.className ?? ""}`}>
                <strong>{VERDICT_LABEL[aiResult.verdict]?.text ?? aiResult.verdict}</strong>
                <p>{aiResult.feedback}</p>
              </div>
            )}

            <div className="self-grade">
              <p className="self-grade-label">스스로 채점하기</p>
              <div className="self-grade-buttons">
                <button className="grade-btn grade-wrong" onClick={() => handleSelfGrade("new")}>
                  몰랐음
                </button>
                <button className="grade-btn grade-partial" onClick={() => handleSelfGrade("familiar")}>
                  애매함
                </button>
                <button className="grade-btn grade-correct" onClick={() => handleSelfGrade("mastered")}>
                  알았음
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
