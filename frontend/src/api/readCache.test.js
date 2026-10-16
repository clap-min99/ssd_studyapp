import test from "node:test";
import assert from "node:assert/strict";
import { createReadCache } from "./readCache.js";

test("shares in-flight reads and returns independent objects", async () => {
  const cache = createReadCache();
  let calls = 0;
  const load = async () => { calls++; return { values: [1] }; };
  const [a, b] = await Promise.all([cache.read("user-a", load, 60), cache.read("user-a", load, 60)]);
  a.values.push(2);
  assert.deepEqual(b.values, [1]);
  assert.deepEqual(await cache.read("user-a", load, 60), b);
  assert.equal(calls, 1);
});

test("expires and separates accounts; uncached reads always refresh", async () => {
  let time = 0, calls = 0;
  const cache = createReadCache({ now: () => time });
  const load = async () => ++calls;
  assert.equal(await cache.read("user-a", load, 60), 1);
  assert.equal(await cache.read("user-b", load, 60), 2);
  time = 61;
  assert.equal(await cache.read("user-a", load, 60), 3);
  assert.equal(await cache.read("personal", load), 4);
  assert.equal(await cache.read("personal", load), 5);
});

test("failed requests can be retried", async () => {
  const cache = createReadCache();
  await assert.rejects(cache.read("key", () => Promise.reject(new Error("offline")), 60));
  assert.equal(await cache.read("key", () => 42, 60), 42);
});

test("logout or invalidation prevents old pending data from repopulating cache", async () => {
  const cache = createReadCache();
  let finish;
  const old = cache.read("key", () => new Promise((resolve) => { finish = resolve; }), 60);
  await Promise.resolve();
  cache.clear();
  assert.equal(await cache.read("key", () => "fresh", 60), "fresh");
  finish("old");
  await old;
  assert.equal(await cache.read("key", () => "unexpected", 60), "fresh");
});

test("bounds cached entries", async () => {
  const cache = createReadCache({ limit: 2 });
  for (const key of ["a", "b", "c"]) await cache.read(key, () => key, 60);
  assert.equal(await cache.read("a", () => "reloaded", 60), "reloaded");
});
