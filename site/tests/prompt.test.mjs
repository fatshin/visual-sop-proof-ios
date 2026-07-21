import assert from "node:assert/strict";
import test from "node:test";

import { personalDataExportPrompt } from "../public/prompt.js";

for (const lang of ["en", "ja"]) {
  test(`${lang} personal-data prompt is grounded, paste-ready, and privacy bounded`, () => {
    const prompt = personalDataExportPrompt(lang);
    assert.ok(prompt.length > (lang === "ja" ? 650 : 1_200));
    assert.match(prompt, lang === "ja" ? /12〜20件/ : /12–20 Markdown bullet points/);
    assert.match(prompt, lang === "ja" ? /前置きと結論は不要/ : /Output only the bullets/);
    assert.match(prompt, lang === "ja" ? /価値観、繰り返す決断の型/ : /values, recurring decision pattern/);
    assert.match(prompt, lang === "ja" ? /確度: 高 \/ 中 \/ 低/ : /Confidence: high \/ medium \/ low/);
    assert.match(prompt, lang === "ja" ? /推測せず/ : /instead of guessing/);
    assert.match(prompt, lang === "ja" ? /出生時刻/ : /birth time/);
    assert.match(prompt, lang === "ja" ? /認証トークン/ : /authentication tokens/);
    assert.match(prompt, lang === "ja" ? /第三者の私的情報/ : /private information about other people/);
  });
}

test("unsupported language falls back to the English prompt", () => {
  assert.equal(personalDataExportPrompt("fr"), personalDataExportPrompt("en"));
});
