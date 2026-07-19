# Misconception Replay — Submission

**Tagline:** Find the misconception hidden behind a correct answer.

**Category:** Education  
**Codex Session ID:** `019f7306-7262-7371-a03f-6b99df7129bf`

## What it does

The product scores a learner’s answer separately from the explanation, detects
correct answers supported by incorrect reasoning, and verifies a pre-authored
synthetic response to a mathematically different contrastive replay.

## How it was built

I used Codex with GPT-5.6 to implement answer/reason separation, misconception
labels, replay-fixture validation, a twenty-case evaluation, tests, and the
public interface. A future live path can use GPT-5.6 to classify open-ended
explanations and draft replays; the public demo neither generates a replay nor
records a live learner attempt.

## Proof

- 20 labeled cases
- all 5 correct-answer/wrong-reason cases flagged in the fixture
- exact fixture classification with precision, recall, and F1 of 1.00
- all five replay explanations match their actual fraction transformations

## Links

- Live product: https://misconception-replay.fatshin.chatgpt.site
- Source: https://github.com/fatshin/misconception-replay
- Devpost draft: https://devpost.com/software/misconception-replay
- Video: `UPLOAD_TO_YOUTUBE_AND_REPLACE`

## Limits

The metrics and resolved outcomes apply only to the included pre-authored
synthetic evaluation set.
