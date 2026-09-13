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
