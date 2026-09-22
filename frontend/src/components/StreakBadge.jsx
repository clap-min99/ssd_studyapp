import { useEffect, useState } from "react";
import { reviewApi } from "../api/client";

export default function StreakBadge({ refreshKey }) {
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
  }, [refreshKey]);

  if (!streak) return null;

  return <span className="streak-badge">🔥 {streak}일 연속</span>;
}