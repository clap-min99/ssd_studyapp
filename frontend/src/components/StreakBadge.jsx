import { useEffect, useState } from "react";
import { reviewApi } from "../api/client";

/** 상단바에 붙는 연속 복습일수 배지. 스트릭이 0이면 아무것도 안 보여준다
 *  (시작 전인데 "0일 연속"이라고 보여주는 건 오히려 김빠짐). */
export default function StreakBadge() {
  const [streak, setStreak] = useState(null);

  useEffect(() => {
    let active = true;
    reviewApi
      .getStreak()
      .then((data) => active && setStreak(data.current_streak))
      .catch(() => {});
    return () => {
      active = false;
    };
  }, []);

  if (!streak) return null;

  return <span className="streak-badge">🔥 {streak}일 연속</span>;
}
