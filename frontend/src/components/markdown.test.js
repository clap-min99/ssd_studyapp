import test from "node:test";
import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import { JSDOM } from "jsdom";

test("Markdown sanitization removes executable HTML and preserves lesson content", async (t) => {
  const dom = new JSDOM("");
  globalThis.window = dom.window;
  t.after(() => { delete globalThis.window; dom.window.close(); });
  const { renderMarkdown } = await import("./markdown.js");
  const parse = (source) => JSDOM.fragment(renderMarkdown(source));

  await t.test("removes scripts, event handlers, frames, forms, CSS and dangerous URLs", () => {
    const result = parse(`
<script>alert(1)</script><img src=x onerror="alert(1)">
<iframe srcdoc="<script>alert(1)</script>"></iframe>
<object data="data:text/html,evil"></object>
<style>body{display:none}</style><p style="position:fixed">text</p>
<form action="https://evil.example"><input name="password"><button>Submit</button></form>
<a href="java&#x73;cript:alert(1)">bad</a>
[bad](javascript:alert%281%29)
<svg onload="alert(1)"><script>alert(1)</script><a xlink:href="javascript:alert(1)"><text>bad</text></a><foreignObject><iframe src="https://evil.example"></iframe></foreignObject></svg>
`);
    assert.equal(result.querySelector("script,iframe,object,style,form,input,button,foreignObject"), null);
    for (const element of result.querySelectorAll("*")) {
      for (const attr of element.attributes) {
        assert.equal(/^on/i.test(attr.name), false, attr.name);
        assert.notEqual(attr.name, "style");
        if (["href", "xlink:href", "src"].includes(attr.name)) {
          assert.doesNotMatch(attr.value, /javascript:|data:text\/html/i);
        }
      }
    }
    assert.match(result.textContent, /text/);
  });

  await t.test("preserves Markdown formatting, tables, code and safe links", () => {
    const result = parse("# Heading\n\n**bold** and `code`\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n[article](https://example.com/news)");
    for (const selector of ["h1", "strong", "code", "table"]) assert.ok(result.querySelector(selector), selector);
    assert.equal(result.querySelector("a").href, "https://example.com/news");
  });

  await t.test("preserves the arithmetic shift operator in chapter 5 lesson 9 prose", async () => {
    const source = await readFile(new URL("../../../digest/content/foundations/chapter05/09-shifters.md", import.meta.url), "utf8");
    const result = parse(source);
    assert.equal(result.querySelector("blockquote"), null);
    const operator = [...result.querySelectorAll("p > code")].find((code) => code.textContent === ">>>");
    assert.ok(operator, "arithmetic shift operator must remain visible as inline code");
    assert.match(operator.parentElement.textContent, /^>>>의 왼쪽 피연산자가 unsigned/);
  });

  await t.test("preserves existing foundation SVG diagrams and accessible labels", async () => {
    const folder = new URL("../../../digest/content/foundations/", import.meta.url);
    const files = (await readdir(folder, { recursive: true })).filter((name) => name.endsWith(".md"));
    let diagrams = 0;
    for (const name of files) {
      const source = await readFile(new URL(name, folder), "utf8");
      const expected = (source.match(/<svg\b/g) || []).length;
      const result = parse(source);
      assert.equal(result.querySelectorAll("svg").length, expected, name);
      assert.equal(result.querySelectorAll("details").length, (source.match(/<details>/g) || []).length, name);
      if (/chapter0[45][\\/]/.test(name)) {
        assert.equal(result.querySelectorAll("pre code.language-systemverilog").length,
          (source.match(/```systemverilog/g) || []).length, name);
        assert.equal(result.querySelectorAll("table").length,
          (source.match(/^\| ---/gm) || []).length, name);
      }
      assert.equal(result.querySelector("del"), null, name);
      // SystemVerilog exponentiation (2**N) is valid code, not broken emphasis.
      const prose = result.cloneNode(true);
      for (const code of prose.querySelectorAll("pre,code")) code.remove();
      assert.doesNotMatch(prose.textContent, /\*\*/, name);
      if (expected) {
        diagrams += expected;
        const svg = result.querySelector("svg");
        assert.ok(svg.getAttribute("viewBox"), name);
        assert.ok(svg.querySelector("text"), name);
        assert.ok(svg.querySelector("title"), name);
        assert.ok(svg.getAttribute("aria-labelledby"), name);
      }
    }
    assert.ok(diagrams > 0);
  });
});
