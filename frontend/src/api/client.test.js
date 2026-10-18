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

test("authentication uses session storage and clears it only when appropriate", async (t) => {
  const tokenKey = "ssd_digest_token";
  const usernameKey = `${tokenKey}_username`;
  t.mock.method(globalThis, "fetch");
  const originalLocal = Object.getOwnPropertyDescriptor(globalThis, "localStorage");
  const originalSession = Object.getOwnPropertyDescriptor(globalThis, "sessionStorage");
  Object.defineProperty(globalThis, "localStorage", { configurable: true, value: storage([
    [tokenKey, "legacy-token"], [usernameKey, "legacy-user"], ["unrelated", "keep"],
  ]) });
  Object.defineProperty(globalThis, "sessionStorage", { configurable: true, value: storage() });
  t.after(() => {
    for (const [name, descriptor] of [["localStorage", originalLocal], ["sessionStorage", originalSession]]) {
      if (descriptor) Object.defineProperty(globalThis, name, descriptor);
      else delete globalThis[name];
    }
  });
  const { auth, api } = await import("./client.js");
  const respond = (data, ok = true) => fetch.mock.mockImplementation(async () => ({ ok, json: async () => data }));

  await t.test("removes legacy credentials without migrating or clearing unrelated data", () => {
    assert.equal(localStorage.getItem(tokenKey), null);
    assert.equal(localStorage.getItem(usernameKey), null);
    assert.equal(localStorage.getItem("unrelated"), "keep");
    assert.equal(auth.isLoggedIn(), false);
  });

  await t.test("signup stores credentials in the current session only", async () => {
    respond({ token: "signup-token", username: "new-user" });
    await auth.signup("new-user", "password", "password");
    assert.equal(auth.getToken(), "signup-token");
    assert.equal(auth.getUsername(), "new-user");
    assert.equal(auth.isLoggedIn(), true);
    assert.equal(localStorage.getItem(tokenKey), null);
    assert.equal(localStorage.getItem(usernameKey), null);
  });

  await t.test("login and API calls use the session token; logout clears credentials and cache", async () => {
    respond({ token: "login-token", username: "user" });
    await auth.login("user", "password");
    assert.equal(auth.getToken(), "login-token");
    assert.equal(auth.getUsername(), "user");
    respond([]);
    await api.getTags();
    assert.equal(fetch.mock.calls.at(-1).arguments[1].headers.Authorization, "Token login-token");
    auth.logout();
    assert.equal(auth.getToken(), null);
    assert.equal(auth.getUsername(), null);
    assert.equal(auth.isLoggedIn(), false);
    respond({ token: "login-token", username: "user" });
    await auth.login("user", "password");
    respond(["fresh"]);
    assert.deepEqual(await api.getTags(), ["fresh"]);
  });

  await t.test("failed login does not replace the session", async () => {
    respond({ detail: "Invalid credentials" }, false);
    await assert.rejects(auth.login("other", "wrong"));
    assert.equal(auth.getToken(), "login-token");
  });

  await t.test("failed deletion keeps the session; successful deletion clears it", async () => {
    respond({ detail: "Wrong password" }, false);
    await assert.rejects(auth.deleteAccount("wrong"));
    assert.equal(auth.isLoggedIn(), true);
    respond(null);
    await auth.deleteAccount("correct");
    assert.equal(fetch.mock.calls.at(-1).arguments[1].headers.Authorization, "Token login-token");
    assert.equal(auth.getToken(), null);
    assert.equal(auth.getUsername(), null);
  });
});
