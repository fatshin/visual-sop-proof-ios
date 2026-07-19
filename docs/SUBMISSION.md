# Misconception Replay — Submission

**Tagline:** Find the misconception hidden behind a correct answer.

**Category:** Education  
**Codex Session ID:** `019f7306-7262-7371-a03f-6b99df7129bf`

## What it does

The product scores a learner’s answer separately from the explanation, detects
correct answers supported by incorrect reasoning, and uses a mathematically
different contrastive replay to test the corrected mental model.

## How it was built

I used Codex with GPT-5.6 to implement answer/reason separation, misconception
labels, replay generation, a twenty-case evaluation, tests, and the public
interface. A future live path can use GPT-5.6 to classify open-ended
explanations and draft replays; the public demo uses a tested fixture.

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

The metric applies only to the included synthetic evaluation set.
