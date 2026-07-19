# CostRoute Lab — Submission

**Tagline:** Find the cheapest route that still clears the quality floor.

**Category:** Developer Tools  
**Codex Session ID:** `019f7306-7262-7371-a03f-6b99df7129bf`

## What it does

CostRoute Lab evaluates complete model-routing combinations over a fixed
twenty-case suite, rejects routes below a three-task macro-average quality
floor, and explains the lowest-cost passing route using normalized bundle units.

## How it was built

I used Codex with GPT-5.6 to implement exhaustive search, deterministic scoring,
coverage checks, tests, and the browser experience. GPT-5.6 is represented as
the high-capability baseline in the tested fixture. The public benchmark uses
fixed synthetic scores and does not make live model calls.

## Proof

- 20 cases with a 91-point three-task macro-average floor
- selected route has a 91.5 macro-average with complete task-model coverage
- selected route costs 3.0 normalized units per three-task bundle
- 61% fixture cost reduction versus the GPT-5.6-only fixture

## Links

- Live product: https://costroute-lab.fatshin.chatgpt.site
- Source: https://github.com/fatshin/costroute-lab
- Devpost draft: https://devpost.com/software/costroute-lab
- Video: `UPLOAD_TO_YOUTUBE_AND_REPLACE`

## Limits

The benchmark is a reproducible fixture, not a universal price claim. Cost is
not a total over all 20 cases; it is a normalized three-task bundle value.
