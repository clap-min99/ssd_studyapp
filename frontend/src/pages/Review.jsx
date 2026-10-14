import { useEffect, useRef, useState } from "react";
import { api, reviewApi } from "../api/client";

const VERDICT_LABEL = {
  correct: { text: "정확해요", className: "verdict-correct" },
  partial: { text: "방향은 맞아요", className: "verdict-partial" },
  wrong: { text: "다시 봐야 해요", className: "verdict-wrong" },
};

export default function Review({ onAnswered }) {
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
  const [picked, setPicked] = useState(null);

  const [summary, setSummary] = useState(null);
  const [tags, setTags] = useState([]);
  const [setup, setSetup] = useState(true);
  const [settings, setSettings] = useState({ daily_goal: 10, category: "", tag: "", date: "", weak_only: false });
  const [saving, setSaving] = useState(false);
  const saveLock = useRef(false);

  function applySession(data) {
    setSummary(data);
    const session = data.session;
    setTerms(session ? session.terms.filter((term) => !session.completed_ids.includes(term.id)) : []);
    setTotalDueAtStart(session?.terms.length || 0);
    setIndex(0);
    setMode(session?.mode || "written");
    setRevealed(false); setAnswer(""); setPicked(null); setAiResult(null); setAiError(null);
  }

  useEffect(() => {
    let active = true;
    Promise.all([reviewApi.getSession(), api.getTags()]).then(([data, tagList]) => {
      if (!active) return;
      applySession(data);
      setTags(tagList);
      setSettings({ daily_goal: data.daily_goal, category: "", tag: "", weak_only: false,
        ...data.session?.scope, date: data.session?.scope.date || "" });
    }).catch((err) => active && setError(err.message)).finally(() => active && setLoading(false));
    return () => { active = false; };
  }, []);

  async function loadDueTerms(extra = false) {
    if (saveLock.current) return;
    saveLock.current = true;
    setSaving(true); setError(null);
    try {
      const data = await reviewApi.startSession({ ...settings, mode, date: settings.date || null, extra });
      applySession(data); setSetup(false);
    } catch (err) { setError(err.message); }
    finally { saveLock.current = false; setSaving(false); }
  }

  const current = terms[index];
  const options = current?.options || [];

  function markSaved() {
    setSummary((previous) => ({ ...previous,
      completed_today: previous.completed_today + 1,
      new_today: previous.new_today + (current.is_new ? 1 : 0),
      session: { ...previous.session, completed_ids: [...previous.session.completed_ids, current.id] },
    }));
    onAnswered?.();
  }

  function goNext() {
    setRevealed(false);
    setAnswer("");
    setAiResult(null);
    setAiError(null);
    setPicked(null);
    setIndex((i) => i + 1);
  }

  async function handleSelfGrade(familiarity) {
    if (saveLock.current) return;
    saveLock.current = true; setSaving(true); setError(null);
    try {
      await reviewApi.submitAnswer(current.id, familiarity, summary.session.id);
      markSaved(); goNext();
    } catch (err) { setError(err.message); }
    finally { saveLock.current = false; setSaving(false); }
  }

  async function handlePick(choice) {
    if (picked !== null || saveLock.current) return;
    saveLock.current = true; setSaving(true); setError(null);
    try {
      await reviewApi.submitAnswer(current.id, choice === current.meaning ? "familiar" : "new", summary.session.id);
      markSaved(); setPicked(choice);
    } catch (err) { setError(err.message); }
    finally { saveLock.current = false; setSaving(false); }
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
  if (!summary) return <p role="alert">{error || "복습 정보를 불러오지 못했어요."}</p>;

  const displayedGoal = setup ? settings.daily_goal : summary.daily_goal;
  const goalMet = summary.completed_today >= displayedGoal;
  const progress = <div className="card review-progress">
    <strong>오늘 목표 {summary.completed_today} / {displayedGoal}개 {goalMet && "달성!"}</strong>
    <progress aria-label="오늘의 복습 진행률" max={displayedGoal} value={Math.min(summary.completed_today, displayedGoal)} />
    <small>새 용어 {summary.new_today} / 3개 · 복습일이 지난 용어부터 학습</small>
  </div>;

  if (setup) return <div className="review">
    <h1>오늘의 복습</h1>
    {progress}
    {current && <button className="btn-primary" disabled={saving} onClick={() => {
      setSettings({ daily_goal: summary.daily_goal, ...summary.session.scope, date: summary.session.scope.date || "" });
      setMode(summary.session.mode);
      setSetup(false);
    }}>이전 복습 이어하기 · {terms.length - index}개 남음</button>}
    <form className="card review-settings" onSubmit={(event) => { event.preventDefault(); loadDueTerms(goalMet); }}>
      <h2>학습 설정</h2>
      <label>하루 목표<select value={settings.daily_goal} onChange={(event) => setSettings({ ...settings, daily_goal: Number(event.target.value) })}>
        {[5, 10, 20].map((count) => <option key={count} value={count}>{count}개</option>)}
      </select></label>
      <label>분야<select value={settings.category} onChange={(event) => setSettings({ ...settings, category: event.target.value, tag: "" })}>
        <option value="">전체</option><option value="ssd">SSD/NAND</option><option value="automotive">자동차 SW</option>
      </select></label>
      <label>주제<select value={settings.tag} onChange={(event) => setSettings({ ...settings, tag: event.target.value })}>
        <option value="">전체 주제</option>{tags.filter((tag) => !settings.category || tag.category === settings.category).map((tag) => <option key={tag.slug} value={tag.slug}>{tag.name}</option>)}
      </select></label>
      <label>다이제스트 날짜 (선택)<input type="date" value={settings.date} onChange={(event) => setSettings({ ...settings, date: event.target.value })} /></label>
      <label>문제 방식<select value={mode} onChange={(event) => setMode(event.target.value)}><option value="written">서술형</option><option value="choice">객관식</option></select></label>
      <label className="review-check"><input type="checkbox" checked={settings.weak_only} onChange={(event) => setSettings({ ...settings, weak_only: event.target.checked })} /> 틀리거나 헷갈린 용어만</label>
      <p className="feed-subject">새 용어는 하루 최대 3개. 완료한 용어는 오늘 다시 출제하지 않아요. 주제·날짜를 선택하면 해당 범위에서 출제해요.</p>
      {current && <small>새로 시작하면 진행 중인 문제 목록이 바뀌어요. 저장된 답변은 유지돼요.</small>}
      <button className="btn-primary" disabled={saving}>{saving ? "준비 중..." : goalMet ? "추가 5개 학습" : "선택한 설정으로 시작"}</button>
    </form>
    {error && <p role="alert" className="status-message error">{error}</p>}
  </div>;

  if (!current) return <div className="review">
    <h1>{goalMet ? "오늘 목표 완료!" : totalDueAtStart ? "이번 복습 완료!" : "학습할 용어가 없어요"}</h1>
    {progress}
    <p className="status-message">{goalMet ? "오늘 정한 분량을 마쳤어요. 원하면 조금 더 학습할 수 있어요." : "선택한 범위의 복습을 마쳤거나, 새 용어의 하루 한도에 도달했어요. 다른 주제를 선택하거나 내일 이어가세요."}</p>
    <button className="btn-primary" onClick={() => { setError(null); setSetup(true); }}>학습 설정으로</button>
    {goalMet && <button className="btn-secondary" disabled={saving} onClick={() => loadDueTerms(true)}>추가 5개 학습</button>}
    {error && <p role="alert">{error}</p>}
  </div>;

  return (
    <div className="review">
      {progress}
      <div className="review-topbar">
        <button className="logout-link" disabled={saving || aiLoading} onClick={() => { if (picked !== null) goNext(); setSetup(true); }}>저장하고 나가기</button>
        <span className="pill pill-accent">{totalDueAtStart - terms.length + index + 1} / {totalDueAtStart}</span>
      </div>

      {saving && <p role="status">답변 저장 중...</p>}
      {error && <p role="alert" className="status-message error">{error} 다시 시도해 주세요.</p>}
      <div className="flashcard">
        <span className="pill pill-neutral">{current.is_new ? "새 용어" : "복습"}</span>
        <h2>{current.term}</h2>
        {mode === "choice" && options.length < 2 && <p className="status-message">객관식 보기가 부족해 서술형으로 진행해요.</p>}

        {mode === "written" || options.length < 2 ? (
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
                <button className="btn-secondary" onClick={handleAiCheck} disabled={aiLoading || saving}>
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
                  <button className="grade-btn grade-wrong" disabled={saving || aiLoading} onClick={() => handleSelfGrade("new")}>몰랐음</button>
                  <button className="grade-btn grade-partial" disabled={saving || aiLoading} onClick={() => handleSelfGrade("familiar")}>애매함</button>
                  <button className="grade-btn grade-correct" disabled={saving || aiLoading} onClick={() => handleSelfGrade("mastered")}>알았음</button>
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
                    <button key={opt} className={cls} onClick={() => handlePick(opt)} disabled={showState || saving}>
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
