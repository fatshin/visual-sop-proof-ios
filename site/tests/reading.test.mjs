import assert from "node:assert/strict";
import test from "node:test";

import {
  buildBirthProfile,
  buildReadingMarkdown,
  createDeepReading,
  validateBirthInput,
} from "../public/reading.js";

const today = new Date("2026-07-21T00:00:00Z");
const birth = {
  date: "1990-04-18",
  time: "around 08:00",
  place: "Tokyo, Japan",
  timePrecision: "approximate",
  placePrecision: "exact",
};
const memories = [
  {
    id: "m1",
    source: "Obsidian",
    title: "A role I want to test",
    text: "I want ownership, but I need a small reversible experiment before changing roles.",
    path: "Career/test.md",
  },
  {
    id: "m2",
    source: "ChatGPT Memory",
    title: "How I make decisions",
    text: "I move more confidently when I have comparison criteria and an exit condition.",
    path: "",
  },
];
const themes = [{ theme: "仕事", mentions: 4 }];

test("birth date, time, and place are all required", () => {
  for (const missing of ["date", "time", "place"]) {
    assert.throws(
      () => validateBirthInput({ ...birth, [missing]: "" }, today),
      new RegExp(`birth-${missing}`),
    );
  }
});

test("approximate and unknown birth details are accepted when explicitly labelled", () => {
  assert.doesNotThrow(() =>
    validateBirthInput(
      {
        ...birth,
        time: "unknown",
        place: "Kanto area",
        timePrecision: "unknown",
        placePrecision: "approximate",
      },
      today,
    ),
  );
});

test("invalid and future birth dates fail closed", () => {
  assert.throws(() => validateBirthInput({ ...birth, date: "1990-02-30" }, today), /birth-date/);
  assert.throws(() => validateBirthInput({ ...birth, date: "2026-07-22" }, today), /birth-date-future/);
});

test("birth profile produces reproducible date-based signals", () => {
  const profile = buildBirthProfile(birth, "en", today);
  assert.equal(profile.sunSign, "Aries");
  assert.equal(profile.lifePath, 5);
  assert.equal(profile.timeBand, "morning");
  assert.match(profile.display, /approximate/);
});

for (const lang of ["en", "ja"]) {
  test(`${lang} reading has ten deep lenses and three actions per lens`, () => {
    const reading = createDeepReading({
      question: lang === "ja" ? "次の仕事へ進む前に何を試すべきですか。" : "What should I test before changing roles?",
      memories,
      themes,
      birth,
      lang,
    });

    assert.equal(reading.lang, lang);
    assert.equal(reading.readings.length, 10);
    assert.ok(reading.synthesis.length > 180);
    for (const item of reading.readings) {
      assert.ok(item.context.length > (lang === "ja" ? 40 : 80));
      assert.ok(item.interpretation.length > (lang === "ja" ? 38 : 70));
      assert.match(item.resonance, /A role I want to test|How I make decisions/);
      assert.equal(item.actions.length, 3);
      assert.ok(item.actions.every((action) => action.length > (lang === "ja" ? 14 : 25)));
      assert.match(item.caveat, lang === "ja" ? /象徴的な内省/ : /symbolic reflection/);
    }

    const markdown = buildReadingMarkdown(reading);
    assert.match(markdown, lang === "ja" ? /## 出生情報/ : /## Birth context/);
    assert.equal((markdown.match(/^### /gmu) || []).length, 10);
    assert.equal((markdown.match(/^1\. /gmu) || []).length, 10);
    assert.match(markdown, /birth_time_precision: approximate/);
    assert.match(markdown, /status: REFLECTION_READY/);
    assert.match(markdown, /memory_count: 2/);
    assert.match(markdown, /themes:\n  - 仕事/);
    assert.match(markdown, lang === "ja" ? /共有前に内容を確認/ : /Review it before sharing/);
    assert.match(markdown, lang === "ja" ? /## 使用した記憶/ : /## Memories used/);
    assert.match(markdown, lang === "ja" ? /医療・法律・投資・安全/ : /medical, legal, financial, or safety/);
    assert.match(markdown, /Career\/test\.md/);
  });
}
