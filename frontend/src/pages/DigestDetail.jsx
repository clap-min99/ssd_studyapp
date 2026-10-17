import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client";
import DigestView from "./DigestView";

export default function DigestDetail() {
  const { id } = useParams();
  const [digest, setDigest] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    setDigest(null);
    api
      .getDigestDetail(id)
      .then((data) => active && setDigest(data))
      .catch((e) => active && setError(e.message))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [id]);

  if (loading) return <p className="status-message">불러오는 중...</p>;
  if (error) return <p className="status-message error">{error}</p>;
  if (!digest) return null;

  return <DigestView key={digest.id} digest={digest} />;
}
