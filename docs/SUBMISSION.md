# Decision Invalidation Ledger — Submission

**Tagline:** Detect when new evidence invalidates an old decision.

**Category:** Work & Productivity  
**Codex Session ID:** `019f7306-7262-7371-a03f-6b99df7129bf`

## What it does

The ledger records a decision with its assumptions and review triggers. New
evidence is matched against those assumptions to classify the decision as
valid, at risk, invalidated, or needing evidence. Missing values, provenance,
or decision metadata never produce a valid result.

## How it was built

I used Codex with GPT-5.6 to implement the ledger schema, trigger comparison,
four-state fail-closed evaluation, owner-linked status-transition events,
tests, and browser interface. A future live path can use GPT-5.6 to extract
candidate assumptions; the public demo uses a tested fixture, and owners
approve the final assumptions and triggers.

## Proof

- one valid, one at-risk, and one invalidated decision
- every status links to an assumption and new evidence
- missing evidence, source, owner, reason, or decision date becomes NEEDS_EVIDENCE
- deterministic fixture and narrated demo

## Links

- Live product: https://decision-invalidation-ledger.fatshin.chatgpt.site
- Source: https://github.com/fatshin/decision-invalidation-ledger
- Devpost draft: https://devpost.com/software/decision-invalidation-ledger
- Video: `UPLOAD_TO_YOUTUBE_AND_REPLACE`

## Limits

The fixture includes named owners and durable-looking synthetic sources. The
MVP emits status events but does not notify people or change external systems.
