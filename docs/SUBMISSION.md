# Public Notice Stress Test — Submission

**Tagline:** Catch the sentence that should stop a public release.

**Category:** Work & Productivity  
**Codex Session ID:** `019f7306-7262-7371-a03f-6b99df7129bf`

## What it does

The product breaks a public notice into factual claims, compares each claim with
its evidence, blocks contradictory or unsupported wording, and proposes a
repair that preserves uncertainty.

## How it was built

I used Codex with GPT-5.6 to implement claim extraction, evidence matching,
release gating, deterministic evaluation, and the public interface. A future
live path can use GPT-5.6 to propose claim boundaries and repair wording; the
public demo uses a tested fixture, and cited evidence remains the gate.

## Proof

- 5 direct conflicts and 1 unsupported claim detected
- release blocked until all six findings are repaired
- synthetic fixture, automated tests, and narrated demo

## Links

- Live product: https://public-notice-stress-test.fatshin.chatgpt.site
- Source: https://github.com/fatshin/public-notice-stress-test
- Devpost draft: https://devpost.com/software/public-notice-stress-test
- Video: `UPLOAD_TO_YOUTUBE_AND_REPLACE`

## Limits

A communications owner must approve a real notice. The demo does not publish.
