import test from "node:test";
import assert from "node:assert/strict";
import { isSafeWebUrl } from "./safeUrl.js";

test("accepts absolute HTTP and HTTPS article URLs", () => {
  for (const url of ["https://example.com/news?q=1#article", "http://example.com", "HTTPS://example.com"]) {
    assert.equal(isSafeWebUrl(url), true, url);
  }
});

test("rejects script URLs, other protocols, malformed URLs and non-string values", () => {
  for (const url of ["javascript:alert(1)", "JaVaScRiPt:alert(1)", "java\nscript:alert(1)", "data:text/html,<script>alert(1)</script>", "vbscript:msgbox(1)", "file:///etc/passwd", "//example.com", "/news", "https://", "", null, undefined, 42, {}]) {
    assert.equal(isSafeWebUrl(url), false, String(url));
  }
});
