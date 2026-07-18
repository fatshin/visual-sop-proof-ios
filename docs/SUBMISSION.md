# Agent Autopsy — Submission

**Tagline:** Make every agent failure leave behind a test.

## What it does

Agent Autopsy reconstructs a failed trace, separates the first causal mistake
from downstream symptoms, proposes the smallest patch, and emits one regression
assertion per failure.

## How it was built

Codex implemented trace normalization, causal classification, patch generation,
fixture evaluation, and the browser experience. GPT-5.6 is intended to explain
unstructured traces; deterministic checks decide whether regressions cover the
original failure.

## Proof

- detects context drift, duplicate side effects, and a limit bypass
- produces 3 regression tests and one minimal patch set
- performs no external customer or refund action

## Links

- Live product: https://agent-autopsy.fatshin.chatgpt.site
- Source: https://github.com/fatshin/agent-autopsy
- Video: `UPLOAD_TO_YOUTUBE_AND_REPLACE`

## Limits

The public trace is synthetic. Proposed patches require owner review.
