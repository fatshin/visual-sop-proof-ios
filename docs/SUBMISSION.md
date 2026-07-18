# Misconception Replay — Submission

**Tagline:** Find the misconception hidden behind a correct answer.

## What it does

The product scores a learner’s answer separately from the explanation, detects
correct answers supported by incorrect reasoning, and generates a contrastive
replay that tests the corrected mental model.

## How it was built

Codex implemented answer/reason separation, misconception labels, replay
generation, a twenty-case evaluation, tests, and the public interface. GPT-5.6
is intended to classify open-ended explanations and draft replays.

## Proof

- 20 labeled cases
- all 5 correct-answer/wrong-reason cases flagged in the fixture
- fixture F1 of 1.00

## Links

- Live product: https://misconception-replay.fatshin.chatgpt.site
- Source: https://github.com/fatshin/misconception-replay
- Video: `UPLOAD_TO_YOUTUBE_AND_REPLACE`

## Limits

The metric applies only to the included synthetic evaluation set.
