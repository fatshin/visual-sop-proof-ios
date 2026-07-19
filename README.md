# Misconception Replay

[Live demo](https://misconception-replay.fatshin.chatgpt.site) · [Public repository](https://github.com/fatshin/misconception-replay)

Misconception Replay checks the reasoning behind a correct fraction answer. It
detects a misconception, supplies a targeted counterexample, and checks a
different replay problem before reporting the misconception as resolved.

## Judge path

1. Run `./scripts/run.sh --port 8108`.
2. Open `http://127.0.0.1:8108`.
3. Select **Run analysis**.
4. Confirm 20 cases and F1 at or above 0.80.
5. Expand a flagged case whose final answer is still correct.
6. Read the different replay problem and confirm its answer, reasoning, and
   `RESOLVED` outcome.

## What is implemented

- fraction-reasoning taxonomy;
- correct-answer/wrong-reason separation;
- 20 labeled synthetic cases spanning five distinct fraction problems;
- misconception-specific counterexamples;
- deterministic replay answers and reasoning with `RESOLVED`/`UNRESOLVED`;
- precision, recall, and F1 acceptance evidence.

## Verification

```sh
./scripts/check.sh
```

## OpenAI and Codex

I used Codex with GPT-5.6 to implement the reasoning taxonomy, labeled
evaluation, input-mutation tests, public interface, and review. A future live
path can use GPT-5.6 for richer reasoning classification and varied
counterexamples, while the fixed labeled set remains the submitted quality
gate.

## Limits

The MVP covers deterministic fraction addition and three reasoning states.
Replay success is evidence for this fixed fixture, not proof of durable learning
or a substitute for a teacher.

## License

This project and its synthetic learner responses are released under the MIT License.
