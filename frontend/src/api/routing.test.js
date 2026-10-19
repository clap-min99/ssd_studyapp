import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { getTransformedRoutes } from "@vercel/routing-utils";

const config = JSON.parse(await readFile(new URL("../../vercel.json", import.meta.url), "utf8"));
const transformed = getTransformedRoutes(config);

test("Vercel proxies Django API paths including trailing slashes before SPA fallback", () => {
  assert.equal(transformed.error, null);
  const routes = transformed.routes.filter((route) => route.src && route.dest);
  for (const pathname of [
    "/api/", "/api/auth/session/", "/api/auth/session",
    "/api/auth/session/login/", "/api/auth/session/signup/", "/api/auth/session/logout/",
    "/api/auth/account/", "/api/review/session/", "/api/review/1/answer/",
    "/api/concept-bookmarks/1/", "/api/digests/latest/", "/api/lessons/12/",
    "/api/tags/", "/api/unknown-endpoint/",
  ]) {
    const route = routes.find((item) => new RegExp(item.src).test(pathname));
    assert.ok(route, pathname);
    const destination = pathname.replace(new RegExp(route.src), route.dest);
    assert.equal(destination, `https://ssd-studyapp-api-80165171345.asia-south1.run.app${pathname}`, pathname);
    assert.equal(route.methods, undefined, "Proxy must also accept POST/PUT/DELETE");
  }
});

test("SPA fallback cannot turn an API error into a successful HTML response", () => {
  const fallback = transformed.routes.find((route) => route.dest === "/index.html");
  assert.ok(fallback);
  const pattern = new RegExp(fallback.src);
  for (const pathname of ["/api", "/api/", "/api/auth/session/", "/api/missing/"]) {
    assert.equal(pattern.test(pathname), false, pathname);
  }
  for (const pathname of ["/", "/account", "/chapters/sequential-logic/lessons/12", "/privacy"]) {
    assert.equal(pattern.test(pathname), true, pathname);
  }
});
