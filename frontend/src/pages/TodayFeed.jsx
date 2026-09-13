import { useEffect, useState } from "react";
import { api } from "../api/client";
import DigestView from "./DigestView";

export default function TodayFeed() {
  const [digest, setDigest] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getLatestDigest()
      .then(setDigest)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="status-message">불러오는 중...</p>;
  if (error) return <p className="status-message error">{error}</p>;
  if (!digest) return <p className="status-message">아직 저장된 다이제스트가 없어요.</p>;

  return <DigestView digest={digest} />;
}
