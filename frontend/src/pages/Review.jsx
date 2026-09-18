import { useEffect, useState } from "react";
import { api, reviewApi } from "../api/client";

const VERDICT_LABEL = {
  correct: { text: "정확해요", className: "verdict-correct" },
  partial: { text: "방향은 맞아요", className: "verdict-partial" },
  wrong: { text: "다시 봐야 해요", className: "verdict-wrong" },
};

function shuffle(arr) {
  const copy = [...arr];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

export default function Review() {
  const [mode, setMode] = useState("written"); // "written" | "choice"

  const [terms, setTerms] = useState([]);
  const [totalDueAtStart, setTotalDueAtStart] = useState(null);
  const [index, setIndex] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [answer, setAnswer] = useState("");
  const [aiResult, setAiResult] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // --- 객관식 모드 ---
  const [termPool, setTermPool] = useState([]);
  const [options, setOptions] = useState([]);
  const [picked, setPicked] = useState(null);

  function loadDueTerms() {
    setLoading(true);
    setError(null);
    let active = true;

    reviewApi
      .getDue()
      .then((data) => {
        if (!active) return;
        const shuffled = shuffle(data);
        setTerms(shuffled);
        setTotalDueAtStart(shuffled.length);
        setIndex(0);
      })
      .catch((e) => active && setError(e.message))
      .finally(() => active && setLoading(false));

    return () => {
      active = false;
    };
  }

  useEffect(() => loadDueTerms(), []);

  useEffect(() => {
    if (mode === "choice" && termPool.length === 0) {
      api.getTerms().then(setTermPool);
    }
  }, [mode, termPool.length]);

  const current = terms[index];

  useEffect(() => {
    if (mode !== "choice" || !current || termPool.length === 0) return;
    const decoys = shuffle(termPool.filter((t) => t.id !== current.id))
      .slice(0, 3)
      .map((t) => t.meaning);
    setOptions(shuffle([current.meaning, ...decoys]));
    setPicked(null);
  }, [mode, current, termPool]);

  function goNext() {
    setRevealed(false);
    setAnswer("");
    setAiResult(null);
    setAiError(null);
    setPicked(null);
    setIndex((i) => i + 1);
  }

  async function handleSelfGrade(familiarity) {
    try {
      await reviewApi.submitAnswer(current.id, familiarity);
    } catch (e) {
      console.error(e);
    }
    goNext();
  }

  async function handlePick(choice) {
    if (picked !== null) return; // 이미 선택했으면 무시
    setPicked(choice);
    const familiarity = choice === current.meaning ? "familiar" : "new";
    try {
      await reviewApi.submitAnswer(current.id, familiarity);
    } catch (e) {
      console.error(e);
    }
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

  if (terms.length === 0) {
    return (
      <div className="review">
        <h1>오늘 복습 끝!</h1>
        <p className="status-message">지금 당장 복습할 용어가 없어요. 내일 다시 와보세요.</p>
      </div>
    );
  }

  if (index >= terms.length) {
    return (
      <div className="review">
        <h1>복습 끝!</h1>
        <p className="status-message">오늘 준비된 {totalDueAtStart}개 카드를 다 봤어요.</p>
        <button className="btn-primary" onClick={loadDueTerms}>
          다시 확인하기
        </button>
      </div>
    );
  }

  return (
    <div className="review">
      <div className="review-topbar">
        <span className="pill pill-neutral">오늘 {totalDueAtStart}개</span>
        <span className="pill pill-accent">{index + 1} / {terms.length}</span>
      </div>

      <div className="view-switcher">
        <button
          className={`pill pill-button ${mode === "written" ? "pill-accent" : "pill-neutral"}`}
          onClick={() => setMode("written")}
        >
          서술형
        </button>
        <button
          className={`pill pill-button ${mode === "choice" ? "pill-accent" : "pill-neutral"}`}
          onClick={() => setMode("choice")}
        >
          객관식
        </button>
      </div>

      <div className="flashcard">
        <h2>{current.term}</h2>

        {mode === "written" ? (
          !revealed ? (
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
                  <button className="grade-btn grade-wrong" onClick={() => handleSelfGrade("new")}>몰랐음</button>
                  <button className="grade-btn grade-partial" onClick={() => handleSelfGrade("familiar")}>애매함</button>
                  <button className="grade-btn grade-correct" onClick={() => handleSelfGrade("mastered")}>알았음</button>
                </div>
              </div>
            </>
          )
        ) : (
          <>
            {options.length === 0 ? (
              <p className="status-message">보기 만드는 중...</p>
            ) : (
              <div className="quiz-options">
                {options.map((opt) => {
                  const isCorrect = opt === current.meaning;
                  const isPicked = picked === opt;
                  const showState = picked !== null;
                  const cls = !showState
                    ? "quiz-option"
                    : isCorrect
                    ? "quiz-option quiz-correct"
                    : isPicked
                    ? "quiz-option quiz-wrong"
                    : "quiz-option";
                  return (
                    <button key={opt} className={cls} onClick={() => handlePick(opt)} disabled={showState}>
                      {opt}
                    </button>
                  );
                })}
              </div>
            )}

            {picked !== null && (
              <>
                {current.relevance && <p className="insight">{current.relevance}</p>}
                <button className="btn-primary" onClick={goNext}>다음</button>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}