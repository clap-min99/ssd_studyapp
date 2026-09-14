const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api";
const TOKEN_STORAGE_KEY = "ssd_digest_token";

export const auth = {
  getToken: () => localStorage.getItem(TOKEN_STORAGE_KEY),
  getUsername: () => localStorage.getItem(`${TOKEN_STORAGE_KEY}_username`),
  isLoggedIn: () => !!localStorage.getItem(TOKEN_STORAGE_KEY),

  login: async (username, password) => {
    const res = await fetch(`${API_BASE}/auth/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || "로그인에 실패했어요.");
    }
    const data = await res.json();
    localStorage.setItem(TOKEN_STORAGE_KEY, data.token);
    localStorage.setItem(`${TOKEN_STORAGE_KEY}_username`, data.username);
    return data;
  },

  logout: () => {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    localStorage.removeItem(`${TOKEN_STORAGE_KEY}_username`);
  },
};

function authHeaders() {
  const token = auth.getToken();
  return token ? { Authorization: `Token ${token}` } : {};
}

async function get(path) {
  const res = await fetch(`${API_BASE}${path}`, { headers: authHeaders() });
  if (!res.ok) {
    throw new Error(`API 요청 실패: ${path} (${res.status})`);
  }
  return res.json();
}

export const api = {
  getLatestDigest: () => get("/digests/latest/"),
  getDigestList: () => get("/digests/"),
  getDigestDetail: (id) => get(`/digests/${id}/`),
  getTerms: () => get("/terms/"),
};

export const CATEGORY_LABEL = {
  ssd: "SSD/NAND",
  automotive: "자동차 SW",
};

export const CATEGORY_BADGE_CLASS = {
  ssd: "badge-ssd",
  automotive: "badge-automotive",
};

// 복습 화면용 API — 간격 반복(spaced repetition)
export const reviewApi = {
  getDue: () => get("/review/due/"),
  getStreak: () => get("/review/streak/"),
  submitAnswer: async (termId, familiarity) => {
    const res = await fetch(`${API_BASE}/review/${termId}/answer/`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ familiarity }),
    });
    if (!res.ok) throw new Error("채점 결과 저장에 실패했어요.");
    return res.json();
  },
  checkAnswer: async (termId, answer) => {
    const res = await fetch(`${API_BASE}/terms/${termId}/check_answer/`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ answer }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || "AI 첨삭 요청에 실패했어요.");
    }
    return res.json();
  },
};

// 용어 상세 팝업용
export const termApi = {
  getDetail: (id) => get(`/terms/${id}/`),
};

// 다이제스트별 내 생각 / 추가 질문
export const noteApi = {
  getInsight: (digestId) => get(`/digests/${digestId}/insight/`),
  saveInsight: async (digestId, text) => {
    const res = await fetch(`${API_BASE}/digests/${digestId}/insight/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) throw new Error("인사이트 저장에 실패했어요.");
    return res.json();
  },
  getQuestions: (digestId) => get(`/digests/${digestId}/questions/`),
  addQuestion: async (digestId, text) => {
    const res = await fetch(`${API_BASE}/digests/${digestId}/questions/`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) throw new Error("질문 추가에 실패했어요.");
    return res.json();
  },
  toggleQuestion: async (questionId, resolved) => {
    const res = await fetch(`${API_BASE}/questions/${questionId}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ resolved }),
    });
    if (!res.ok) throw new Error("질문 상태 변경에 실패했어요.");
    return res.json();
  },
  deleteQuestion: async (questionId) => {
    const res = await fetch(`${API_BASE}/questions/${questionId}/`, {
      method: "DELETE",
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error("질문 삭제에 실패했어요.");
  },
};