import test from "node:test";
import assert from "node:assert/strict";
import { monthDays } from "./calendar.js";

test("places a leap February on the correct weekdays", () => {
  const days = monthDays("2024-02");
  assert.equal(days.indexOf("2024-02-01"), 4);
  assert.equal(days.filter(Boolean).length, 29);
  assert.equal(days.at(32), "2024-02-29");
  assert.equal(days.length % 7, 0);
});

test("handles Sunday starts, six-week months and year boundaries without adjacent dates", () => {
  assert.equal(monthDays("2026-02")[0], "2026-02-01");
  assert.equal(monthDays("2026-02").length, 28);
  const days = monthDays("2026-08");
  assert.equal(days.length, 42);
  assert.equal(days.indexOf("2026-08-01"), 6);
  assert.equal(days.filter(Boolean).length, 31);
  assert.ok(monthDays("2027-01").filter(Boolean).every((date) => date.startsWith("2027-01-")));
});
