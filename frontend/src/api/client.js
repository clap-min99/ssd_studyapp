const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api";

async function get(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    throw new Error(`API 요청 실패: ${path} (${res.status})`);
  }
  return res.json();
}

export const api = {
  getLatestDigest: () => get("/digests/latest/"),
  getDigestList: () => get("/digests/"),
  getDigestDetail: (id) => get(`/digests/${id}/`),
  getTerms: (familiarity) =>
    get(`/terms/${familiarity ? `?familiarity=${familiarity}` : ""}`),
};

export const CATEGORY_LABEL = {
  ssd: "SSD/NAND",
  automotive: "자동차 SW",
};

// 복습 화면용 추가 API
export const reviewApi = {
  updateFamiliarity: async (termId, familiarity) => {
    const res = await fetch(`${API_BASE}/terms/${termId}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ familiarity }),
    });
    if (!res.ok) throw new Error("채점 결과 저장에 실패했어요.");
    return res.json();
  },
  checkAnswer: async (termId, answer) => {
    const res = await fetch(`${API_BASE}/terms/${termId}/check_answer/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answer }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || "AI 첨삭 요청에 실패했어요.");
    }
    return res.json();
  },
};
