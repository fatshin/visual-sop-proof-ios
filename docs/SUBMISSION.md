# Agent Autopsy — Submission

**Tagline:** Make every agent failure leave behind a test.

**Category:** Developer Tools  
**Codex Session ID:** `019f7306-7262-7371-a03f-6b99df7129bf`

## What it does

Agent Autopsy reconstructs a failed trace, separates the first causal mistake
from downstream symptoms, proposes the smallest patch, and emits one regression
assertion per failure.

## How it was built

I used Codex with GPT-5.6 to implement trace normalization, causal
classification, patch generation, fixture evaluation, and the browser
experience. A future live path can use GPT-5.6 to explain unstructured traces;
the public demo uses a tested fixture, and deterministic checks decide whether
regressions cover the original failure.

## Proof

- detects context drift, duplicate side effects, and a limit bypass
- produces 3 regression tests and one minimal patch set
- performs no external customer or refund action

## Links

- Live product: https://agent-autopsy.fatshin.chatgpt.site
- Source: https://github.com/fatshin/agent-autopsy
- Devpost draft: https://devpost.com/software/agent-autopsy
- Video: `UPLOAD_TO_YOUTUBE_AND_REPLACE`

## Limits

The public trace is synthetic. Proposed patches require owner review.
