import test from "node:test";
import assert from "node:assert/strict";

function storage(entries = []) {
  const values = new Map(entries);
  return {
    getItem: (key) => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, String(value)),
    removeItem: (key) => values.delete(key),
  };
}

test("cookie authentication restores safely without browser-stored credentials", async (t) => {
  t.mock.method(globalThis, "fetch");
  const keys = ["ssd_digest_token", "ssd_digest_token_username"];
  const originals = ["localStorage", "sessionStorage"].map((name) => [name, Object.getOwnPropertyDescriptor(globalThis, name)]);
  for (const [name] of originals) Object.defineProperty(globalThis, name, {
    configurable: true, value: storage([[keys[0], "old-token"], [keys[1], "old-user"], ["unrelated", "keep"]]),
  });
  t.after(() => {
    for (const [name, descriptor] of originals) {
      if (descriptor) Object.defineProperty(globalThis, name, descriptor);
      else delete globalThis[name];
    }
  });
  const { auth, api, bookmarkApi, deepDiveApi, noteApi, reviewApi } = await import("./client.js");
  const session = (name = "reader", csrfToken = "masked-csrf") => ({ username: name, csrfToken });
  const json = (data, status = 200) => new Response(data === null ? null : JSON.stringify(data), {
    status, headers: { "Content-Type": "application/json" },
  });
  const respond = (data, status = 200) => fetch.mock.mockImplementation(async () => json(data, status));

  await t.test("removes old tokens from both storage types and keeps unrelated data", () => {
    for (const name of ["localStorage", "sessionStorage"]) {
      for (const key of keys) assert.equal(globalThis[name].getItem(key), null);
      assert.equal(globalThis[name].getItem("unrelated"), "keep");
    }
    assert.equal(auth.isLoggedIn(), false);
  });

  await t.test("restores an existing server session on a new page with no token in storage", async () => {
    respond(session());
    await auth.restoreSession();
    assert.equal(auth.isLoggedIn(), true);
    assert.equal(auth.getUsername(), "reader");
    const reopened = await import("./sessionAuth.js?reopened");
    assert.equal(reopened.auth.isLoggedIn(), false);
    await reopened.auth.restoreSession();
    assert.equal(reopened.auth.getUsername(), "reader");
    assert.equal(fetch.mock.calls.at(-1).arguments[0], "/api/auth/session/");
    assert.equal(fetch.mock.calls.at(-1).arguments[1].credentials, "same-origin");
  });

  await t.test("login and signup keep only metadata in memory and send CSRF", async () => {
    respond(session("new-user", "rotated-csrf"));
    await auth.signup("new-user", "password", "password");
    assert.equal(auth.getUsername(), "new-user");
    const options = fetch.mock.calls.at(-1).arguments[1];
    assert.equal(options.headers["X-CSRFToken"], "masked-csrf");
    assert.equal(options.headers.Authorization, undefined);
    respond(session("reader"));
    await auth.login("reader", "password");
    assert.equal(auth.getUsername(), "reader");
    for (const name of ["localStorage", "sessionStorage"]) {
      for (const key of keys) assert.equal(globalThis[name].getItem(key), null);
    }
  });

  await t.test("HTML returned by the SPA fallback cannot be mistaken for a session", async () => {
    const before = auth.getUsername();
    fetch.mock.mockImplementation(async () => new Response("<!doctype html><html></html>", {
      status: 200, headers: { "Content-Type": "text/html; charset=utf-8" },
    }));
    await assert.rejects(auth.restoreSession(), /로그인 서비스를 불러오지 못했어요/);
    await assert.rejects(auth.login("reader", "password"), /로그인 서비스를 불러오지 못했어요/);
    assert.equal(auth.getUsername(), before);
  });

  await t.test("malformed JSON and missing session fields preserve the current identity", async () => {
    const before = auth.getUsername();
    fetch.mock.mockImplementation(async () => new Response("not json", {
      status: 200, headers: { "Content-Type": "application/json" },
    }));
    await assert.rejects(auth.restoreSession(), /로그인 서비스를 불러오지 못했어요/);
    for (const invalid of [{}, { username: "reader" }, { csrfToken: "csrf" }, { username: null, csrfToken: "csrf" }]) {
      respond(invalid);
      await assert.rejects(auth.login("reader", "password"), /로그인 서비스를 불러오지 못했어요/);
      assert.equal(auth.getUsername(), before);
    }
  });

  await t.test("every write API uses the common cookie and CSRF request path", async () => {
    respond({});
    const writes = [
      () => reviewApi.startSession({}),
      () => reviewApi.submitAnswer(1, 2, 3),
      () => reviewApi.checkAnswer(1, "answer"),
      () => bookmarkApi.set(1, true),
      () => bookmarkApi.set(1, false),
      () => deepDiveApi.generate("article", 1),
      () => noteApi.saveInsight(1, "text"),
      () => noteApi.addQuestion(1, "text"),
      () => noteApi.toggleQuestion(1, true),
      () => noteApi.deleteQuestion(1),
    ];
    for (const write of writes) {
      await write();
      const [url, options] = fetch.mock.calls.at(-1).arguments;
      assert.ok(url.startsWith("/api/"));
      assert.equal(options.credentials, "same-origin");
      assert.equal(options.headers["X-CSRFToken"], "masked-csrf");
      assert.equal(options.headers.Authorization, undefined);
    }
  });

  await t.test("network errors, 5xx and ordinary 403 never clear a working session", async () => {
    fetch.mock.mockImplementation(async () => { throw new Error("offline"); });
    await assert.rejects(api.getTerms());
    await assert.rejects(auth.restoreSession());
    assert.equal(auth.getUsername(), "reader");
    for (const status of [503, 403]) {
      respond({ detail: "unavailable" }, status);
      await assert.rejects(api.getTerms());
      assert.equal(auth.getUsername(), "reader");
    }
    respond({ detail: "wrong password" }, 401);
    await assert.rejects(auth.login("other", "wrong"));
    assert.equal(auth.getUsername(), "reader");
  });

  await t.test("refreshes rotated CSRF once and retries only the rejected write", async () => {
    const calls = [];
    fetch.mock.mockImplementation(async (url, options) => {
      calls.push([url, options]);
      if (url.endsWith("/auth/session/")) return json(session("reader", "new-csrf"));
      if (options.headers["X-CSRFToken"] !== "new-csrf") return json({ code: "csrf_failed" }, 403);
      return json({});
    });
    await bookmarkApi.set(1, true);
    assert.equal(calls.length, 3);
    assert.equal(calls[2][1].headers["X-CSRFToken"], "new-csrf");
  });

  await t.test("never retries a write after discovering a different account", async () => {
    let writes = 0;
    fetch.mock.mockImplementation(async (url) => {
      if (url.endsWith("/auth/session/")) return json(session("other"));
      writes += 1;
      return json({ code: "csrf_failed" }, 403);
    });
    await assert.rejects(bookmarkApi.set(1, true), /로그인 상태가 변경/);
    assert.equal(writes, 1);
    assert.equal(auth.getUsername(), "other");
  });

  await t.test("failed server logout preserves state; success clears state and cached reads", async () => {
    respond(["old"]);
    assert.deepEqual(await api.getTags(), ["old"]);
    respond({ detail: "offline" }, 503);
    await assert.rejects(auth.logout());
    assert.equal(auth.getUsername(), "other");
    respond(session(null));
    await auth.logout();
    assert.equal(auth.isLoggedIn(), false);
    respond(session("other"));
    await auth.login("other", "password");
    respond(["fresh"]);
    assert.deepEqual(await api.getTags(), ["fresh"]);
  });

  await t.test("late unauthorized responses cannot sign out a newer login", async () => {
    let finish;
    fetch.mock.mockImplementation(() => new Promise((resolve) => { finish = resolve; }));
    const old = api.getTerms();
    await new Promise((resolve) => setTimeout(resolve, 0));
    respond(session("reader"));
    await auth.login("reader", "password");
    finish(json({ detail: "old session expired" }, 401));
    await assert.rejects(old);
    assert.equal(auth.getUsername(), "reader");
  });

  await t.test("a current session's 401 clears authentication without reloading the page", async () => {
    respond({ detail: "expired" }, 401);
    await assert.rejects(api.getTerms());
    assert.equal(auth.isLoggedIn(), false);
    respond(session("reader"));
    await auth.restoreSession();
  });

  await t.test("failed deletion preserves session; success clears it without an extra logout", async () => {
    respond({ detail: "wrong password" }, 400);
    await assert.rejects(auth.deleteAccount("wrong"));
    assert.equal(auth.isLoggedIn(), true);
    respond(null, 204);
    const before = fetch.mock.calls.length;
    await auth.deleteAccount("correct");
    assert.equal(fetch.mock.calls.length, before + 1);
    assert.equal(auth.isLoggedIn(), false);
    assert.equal(auth.getUsername(), null);
  });
});
