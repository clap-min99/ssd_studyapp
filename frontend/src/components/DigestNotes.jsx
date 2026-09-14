import { useEffect, useState } from "react";
import { noteApi } from "../api/client";

/** 다이제스트 하나에 딸린 "내 생각"과 "추가로 공부할 질문" 섹션.
 *  DigestView(오늘 피드 / 타임라인 상세) 안에 붙는다. */
export default function DigestNotes({ digestId }) {
  const [insight, setInsight] = useState("");
  const [savedInsight, setSavedInsight] = useState("");
  const [saving, setSaving] = useState(false);

  const [questions, setQuestions] = useState([]);
  const [newQuestion, setNewQuestion] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    Promise.all([noteApi.getInsight(digestId), noteApi.getQuestions(digestId)])
      .then(([insightData, questionData]) => {
        if (!active) return;
        setInsight(insightData.text);
        setSavedInsight(insightData.text);
        setQuestions(questionData);
      })
      .catch((e) => console.error(e))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [digestId]);

  async function handleSaveInsight() {
    setSaving(true);
    try {
      await noteApi.saveInsight(digestId, insight);
      setSavedInsight(insight);
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  }

  async function handleAddQuestion(e) {
    e.preventDefault();
    if (!newQuestion.trim()) return;
    try {
      const q = await noteApi.addQuestion(digestId, newQuestion.trim());
      setQuestions((prev) => [q, ...prev]);
      setNewQuestion("");
    } catch (e) {
      console.error(e);
    }
  }

  async function handleToggleQuestion(q) {
    const nextResolved = !q.resolved;
    setQuestions((prev) =>
      prev.map((item) => (item.id === q.id ? { ...item, resolved: nextResolved } : item))
    );
    try {
      await noteApi.toggleQuestion(q.id, nextResolved);
    } catch (e) {
      console.error(e);
    }
  }

  async function handleDeleteQuestion(q) {
    setQuestions((prev) => prev.filter((item) => item.id !== q.id));
    try {
      await noteApi.deleteQuestion(q.id);
    } catch (e) {
      console.error(e);
    }
  }

  if (loading) return null;

  const isDirty = insight !== savedInsight;

  return (
    <>
      <section>
        <h2>오늘의 인사이트</h2>
        <textarea
          className="answer-input"
          placeholder="읽고 나서 든 내 생각을 자유롭게..."
          value={insight}
          onChange={(e) => setInsight(e.target.value)}
          rows={4}
        />
        {isDirty && (
          <button className="btn-secondary" onClick={handleSaveInsight} disabled={saving}>
            {saving ? "저장 중..." : "저장"}
          </button>
        )}
      </section>

      <section>
        <h2>추가로 공부할 질문</h2>

        {questions.map((q) => (
          <label key={q.id} className="question-item">
            <input
              type="checkbox"
              checked={q.resolved}
              onChange={() => handleToggleQuestion(q)}
            />
            <span className={q.resolved ? "question-text resolved" : "question-text"}>
              {q.text}
            </span>
            <button
              type="button"
              className="question-delete"
              onClick={() => handleDeleteQuestion(q)}
              aria-label="삭제"
            >
              ×
            </button>
          </label>
        ))}

        <form className="question-add-form" onSubmit={handleAddQuestion}>
          <input
            className="search-input"
            placeholder="궁금한 것 추가하기..."
            value={newQuestion}
            onChange={(e) => setNewQuestion(e.target.value)}
          />
        </form>
      </section>
    </>
  );
}
