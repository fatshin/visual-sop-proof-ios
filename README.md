# Misconception Replay

[Live demo](https://misconception-replay.fatshin.chatgpt.site) · [Public repository](https://github.com/fatshin/misconception-replay)

Misconception Replay checks the reasoning behind a correct fraction answer. It
detects a misconception, supplies a counterexample, and reports evaluation
precision, recall, and F1 over 20 labeled cases.

## Judge path

1. Run `./scripts/run.sh --port 8108`.
2. Open `http://127.0.0.1:8108`.
3. Select **Run analysis**.
4. Confirm 20 cases and F1 at or above 0.80.
5. Expand a flagged case whose final answer is still correct.
6. Read the counterexample that exposes the faulty rule.

## What is implemented

- fraction-reasoning taxonomy;
- correct-answer/wrong-reason separation;
- 20 labeled synthetic cases;
- counterexample generation;
- precision, recall, and F1 acceptance evidence.

## Verification

```sh
./scripts/check.sh
```

## OpenAI and Codex

Codex was used to implement and test the taxonomy. GPT-5.6 can provide richer
reasoning classification and varied counterexamples, while the fixed labeled
set remains the submitted quality gate.

## Limits

The MVP covers fraction addition and three reasoning states. It is not a
general student assessment or a substitute for a teacher.
