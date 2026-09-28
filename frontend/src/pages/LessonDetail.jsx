import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { marked } from "marked";
import { api } from "../api/client";

export default function LessonDetail() {
  const { slug, lessonId } = useParams();
  const navigate = useNavigate();

  const [lesson, setLesson] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;
    setLesson(null);
    setError(null);

    api
      .getLessonDetail(lessonId)
      .then((data) => active && setLesson(data))
      .catch((e) => active && setError(e.message));

    return () => {
      active = false;
    };
  }, [lessonId]);

  const bodyHtml = useMemo(() => {
    if (!lesson?.body) return "";
    return marked.parse(lesson.body);
  }, [lesson?.body]);

  if (error) return <p className="status-message error">{error}</p>;
  if (!lesson) return <p className="status-message">불러오는 중...</p>;

  return (
    <div>
      <button className="pill pill-button pill-neutral" onClick={() => navigate(`/chapters/${slug}`)}>
        ← {lesson.chapter_name}
      </button>

      <h1 style={{ marginTop: 12 }}>
        {lesson.order}. {lesson.title}
      </h1>

      <div className="lesson-content" dangerouslySetInnerHTML={{ __html: bodyHtml }} />

      <div className="lesson-nav">
        {lesson.prev_lesson_id && (
          <button
            className="pill pill-button pill-neutral"
            onClick={() => navigate(`/chapters/${slug}/lessons/${lesson.prev_lesson_id}`)}
          >
            ← 이전 레슨
          </button>
        )}
        {lesson.next_lesson_id && (
          <button
            className="pill pill-button pill-accent"
            onClick={() => navigate(`/chapters/${slug}/lessons/${lesson.next_lesson_id}`)}
          >
            다음 레슨: {lesson.next_lesson_title} →
          </button>
        )}
      </div>

      {!lesson.next_lesson_id &&
        (lesson.next_chapter_slug ? (
          <button
            className="btn-primary chapter-next-btn"
            onClick={() => navigate(`/chapters/${lesson.next_chapter_slug}`)}
          >
            다음 챕터: {lesson.next_chapter_name} →
          </button>
        ) : (
          <button className="btn-secondary chapter-next-btn" onClick={() => navigate("/chapters")}>
            마지막 챕터예요 — 목록으로
          </button>
        ))}
    </div>
  );
}
