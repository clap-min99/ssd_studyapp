// The session cookie is HttpOnly. Only the username and masked CSRF token
// live in memory; no bearer credentials are stored in browser storage.
const API_BASE = "/api";
let username = null;
let csrfToken = null;
let version = 0;
let restoring = null;
const listeners = new Set();

for (const name of ["localStorage", "sessionStorage"]) {
  try {
    globalThis[name]?.removeItem("ssd_digest_token");
    globalThis[name]?.removeItem("ssd_digest_token_username");
  } catch { /* Storage may be disabled; cookie authentication doesn't need it. */ }
}

function setSession(data, force = false) {
  const changed = username !== data.username || force;
  username = data.username;
  csrfToken = data.csrfToken || null;
  if (changed) {
    version += 1;
    for (const listener of listeners) listener();
  }
}

async function restoreSession() {
  if (!restoring) {
    const started = version;
    restoring = (async () => {
      const res = await fetch(`${API_BASE}/auth/session/`, {
        credentials: "same-origin", cache: "no-store",
      });
      if (!res.ok) throw new Error("로그인 상태를 확인하지 못했어요. 다시 시도해 주세요.");
      const data = await res.json();
      if (version === started) setSession(data);
      return data;
    })().finally(() => { restoring = null; });
  }
  return restoring;
}

export async function request(path, options = {}, { authAction = false, retryCsrf = true } = {}) {
  const method = options.method || "GET";
  const unsafe = !["GET", "HEAD", "OPTIONS"].includes(method);
  if (unsafe && !csrfToken) await restoreSession();
  const started = version;
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    credentials: "same-origin",
    cache: "no-store",
    headers: { ...options.headers, ...(unsafe ? { "X-CSRFToken": csrfToken } : {}) },
  });
  if (!authAction && started !== version) throw new Error("로그인 상태가 변경됐어요. 다시 시도해 주세요.");
  if (res.status === 403 && unsafe && retryCsrf) {
    const body = await res.clone().json().catch(() => ({}));
    if (body.code === "csrf_failed") {
      // Another tab may have rotated the CSRF secret. The rejected request
      // did not execute, so retry once after refreshing it. Never replay a
      // write under a different user's newly discovered session.
      await restoreSession();
      if (version !== started) throw new Error("로그인 상태가 변경됐어요. 다시 시도해 주세요.");
      return request(path, options, { authAction, retryCsrf: false });
    }
  }
  if (res.status === 401 && !authAction && started === version) {
    setSession({ username: null }, true);
  }
  return res;
}

async function authenticate(path, body) {
  const res = await request(path, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  }, { authAction: true });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(Object.values(data).flat().join(" ") || "로그인에 실패했어요.");
  setSession(data, true);
  return data;
}

export const auth = {
  getUsername: () => username,
  isLoggedIn: () => username !== null,
  getVersion: () => version,
  restoreSession,
  subscribe: (listener) => {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },
  signup: (name, password, passwordConfirm) => authenticate("/auth/session/signup/", {
    username: name, password, password_confirm: passwordConfirm,
  }),
  login: (name, password) => authenticate("/auth/session/login/", { username: name, password }),
  logout: async () => {
    const res = await request("/auth/session/logout/", { method: "POST" });
    if (!res.ok) throw new Error("로그아웃하지 못했어요. 다시 시도해 주세요.");
    setSession(await res.json(), true);
  },
  deleteAccount: async (password) => {
    const res = await request("/auth/account/", {
      method: "DELETE", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ password }),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(Object.values(data).flat().join(" ") || "계정 삭제에 실패했어요. 다시 시도해 주세요.");
    }
    setSession({ username: null }, true);
  },
};
