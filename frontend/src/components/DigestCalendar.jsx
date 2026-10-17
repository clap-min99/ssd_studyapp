import { useEffect, useState } from "react";
import { api } from "../api/client";
import Modal from "./Modal";
import { monthDays } from "./calendar";

export default function DigestCalendar({ selectedDate, onSelect, onClose }) {
  const [digests, setDigests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retry, setRetry] = useState(0);
  const [month, setMonth] = useState(selectedDate.slice(0, 7));

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    api.getDigestDates().then((data) => active && setDigests(data))
      .catch((e) => active && setError(e.message))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [retry]);

  const months = [...new Set(digests.map((digest) => digest.date.slice(0, 7)))].sort();
  const displayedMonth = months.includes(month) ? month : months.at(-1);
  const index = months.indexOf(displayedMonth);
  const dates = new Map(digests.map((digest) => [digest.date, digest.id]));

  return (
    <Modal label="날짜별 콘텐츠 선택" onClose={onClose}>
      <h2 className="calendar-title">날짜별 콘텐츠</h2>
      <p className="calendar-hint">기사·학습 콘텐츠·용어가 있는 날짜만 선택할 수 있어요.</p>
      {loading && <p role="status">날짜를 불러오는 중...</p>}
      {error && <p role="alert">{error} <button className="pill pill-button" onClick={() => setRetry((value) => value + 1)}>다시 시도</button></p>}
      {!loading && !error && !months.length && <p role="status">아직 콘텐츠가 있는 날짜가 없어요.</p>}
      {!loading && !error && displayedMonth && <>
        <div className="calendar-month">
          <button className="pill pill-button" aria-label="이전 콘텐츠 월" disabled={index <= 0} onClick={() => setMonth(months[index - 1])}>‹</button>
          <h3 aria-live="polite">{displayedMonth.replace("-", "년 ")}월</h3>
          <button className="pill pill-button" aria-label="다음 콘텐츠 월" disabled={index >= months.length - 1} onClick={() => setMonth(months[index + 1])}>›</button>
        </div>
        <div className="calendar-grid">
          {["일", "월", "화", "수", "목", "금", "토"].map((day) => <span className="calendar-weekday" key={day} aria-hidden="true">{day}</span>)}
          {monthDays(displayedMonth).map((date, position) => date ? (
            <button key={date} className={`calendar-day${date === selectedDate ? " calendar-selected" : ""}`} disabled={!dates.has(date)} aria-label={`${date}${dates.has(date) ? " 콘텐츠 보기" : " 콘텐츠 없음"}`} aria-current={date === selectedDate ? "date" : undefined} onClick={() => onSelect(dates.get(date))}>
              {Number(date.slice(-2))}
            </button>
          ) : <span key={`blank-${position}`} />)}
        </div>
      </>}
    </Modal>
  );
}
