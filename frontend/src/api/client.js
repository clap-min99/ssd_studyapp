import { createReadCache } from "./readCache";

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api";
const TOKEN_STORAGE_KEY = "ssd_digest_token";
const readCache = createReadCache();
const CONTENT_TTL = 60_000;

export const auth = {
  getToken: () => localStorage.getItem(TOKEN_STORAGE_KEY),
  getUsername: () => localStorage.getItem(`${TOKEN_STORAGE_KEY}_username`),
  isLoggedIn: () => !!localStorage.getItem(TOKEN_STORAGE_KEY),

  signup: async (username, password, passwordConfirm) => {
    const res = await fetch(`${API_BASE}/auth/signup/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password, password_confirm: passwordConfirm }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const messages = Object.values(data).flat().join(" ");
      throw new Error(messages || "회원가입에 실패했어요. 잠시 후 다시 시도해 주세요.");
    }
    localStorage.setItem(TOKEN_STORAGE_KEY, data.token);
    localStorage.setItem(`${TOKEN_STORAGE_KEY}_username`, data.username);
    return data;
  },

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
    readCache.clear();
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    localStorage.removeItem(`${TOKEN_STORAGE_KEY}_username`);
  },

  deleteAccount: async (password) => {
    const res = await fetch(`${API_BASE}/auth/account/`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ password }),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(Object.values(data).flat().join(" ") || "계정 삭제에 실패했어요. 다시 시도해 주세요.");
    }
    auth.logout();
  },
};

function authHeaders() {
  const token = auth.getToken();
  return token ? { Authorization: `Token ${token}` } : {};
}

function get(path, ttl = 0) {
  const headers = authHeaders();
  const key = JSON.stringify([headers.Authorization || "", path]);
  return readCache.read(key, () => fetchJson(path, headers), ttl);
}

async function fetchJson(path, headers) {
  const res = await fetch(`${API_BASE}${path}`, { headers });
  if (res.status === 401 && auth.isLoggedIn()) {
    // 저장된 토큰이 서버에 없음(DB 변경·토큰 삭제 등) -> 로그아웃 후 로그인 화면으로
    auth.logout();
    window.location.reload();
  }
  if (!res.ok) {
    throw new Error(`API 요청 실패: ${path} (${res.status})`);
  }
  return res.json();
}

export const api = {
  getLatestDigest: () => get("/digests/latest/?compact=1"),
  getDigestList: () => get("/digests/", CONTENT_TTL),
  getDigestDates: () => get("/digests/dates/", CONTENT_TTL),
  getDigestDetail: (id) => get(`/digests/${id}/?compact=1`),
  getTerms: () => get("/terms/"),
  getTags: () => get("/tags/", CONTENT_TTL),
  getTagDetail: (slug) => get(`/tags/${slug}/`, CONTENT_TTL),
  getTagTerms: (slug) => get(`/tags/${slug}/terms/`),
  getChapterLessons: (slug) => get(`/tags/${slug}/lessons/`, CONTENT_TTL),
  getLessonDetail: (id) => get(`/lessons/${id}/`, CONTENT_TTL),
  getTagArticles: (slug) => get(`/tags/${slug}/articles/?compact=1`, CONTENT_TTL),
  getLearningItems: () => get("/learning-items/?compact=1", CONTENT_TTL),
  getTagLearningItems: (slug) => get(`/tags/${slug}/learning-items/?compact=1`, CONTENT_TTL),
  getContentDetail: (kind, id) => get(`/content/${kind}/${id}/`, CONTENT_TTL),
};

export const CATEGORY_LABEL = {
  foundations: "컴퓨터 구조 기초",
  ssd: "SSD/NAND",
  automotive: "자동차 SW",
};

export const CATEGORY_BADGE_CLASS = {
  foundations: "badge-ssd",
  ssd: "badge-ssd",
  automotive: "badge-automotive",
};

// 복습 화면용 API — 간격 반복(spaced repetition)
export const reviewApi = {
  getSession: () => get("/review/session/"),
  startSession: async (options) => {
    const res = await fetch(`${API_BASE}/review/session/`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(options),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(Object.values(data).flat().join(" ") || "복습을 시작하지 못했어요.");
    return data;
  },
  getDue: () => get("/review/due/"),
  getStreak: () => get("/review/streak/"),
  submitAnswer: async (termId, familiarity, sessionId) => {
    const res = await fetch(`${API_BASE}/review/${termId}/answer/`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ familiarity, session_id: sessionId }),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || "채점 결과 저장에 실패했어요.");
    }
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
export const bookmarkApi = {
  getIds: () => get("/concept-bookmarks/"),
  set: async (id, saved) => {
    const res = await fetch(`${API_BASE}/concept-bookmarks/${id}/`, {
      method: saved ? "PUT" : "DELETE",
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error("북마크 변경에 실패했어요. 다시 시도해 주세요.");
  },
};

export const termApi = {
  getDetail: (id) => get(`/terms/${id}/`),
};

// 기사/학습 카드 심화 해설 — kind: "article" | "learning-item"
export const deepDiveApi = {
  generate: async (kind, id) => {
    const res = await fetch(`${API_BASE}/deep-dive/${kind}/${id}/`, {
      method: "POST",
      headers: authHeaders(),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || "AI 해설 요청에 실패했어요.");
    }
    readCache.clear();
    return res.json();
  },
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
