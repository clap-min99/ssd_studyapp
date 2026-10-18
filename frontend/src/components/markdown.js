import { marked } from "marked";
import DOMPurify from "dompurify";

export function renderMarkdown(source) {
  return DOMPurify.sanitize(marked.parse(source), {
    FORBID_TAGS: ["style", "form", "input", "button", "textarea", "select"],
    FORBID_ATTR: ["style"],
  });
}
