import assert from "node:assert/strict";
import test from "node:test";

import { looksSensitive } from "../public/privacy.js";

test("rejects secret-like memory text from every browser import path", () => {
  for (const text of [
    "password: value",
    "passwd value",
    "api_key: value",
    "Authorization: Bearer value",
    "token=value",
    "パスワードは value",
    "sk-1234567890abcdefghijkl",
    "ghp_1234567890abcdefghijkl",
  ]) {
    assert.equal(looksSensitive(text), true, text);
  }
});

test("keeps ordinary reflection text", () => {
  assert.equal(looksSensitive("次の仕事について考えた記録です。"), false);
  assert.equal(looksSensitive("I evaluated passwordless login and tokenization."), false);
  assert.equal(looksSensitive("A trade secret and a token of appreciation."), false);
});
