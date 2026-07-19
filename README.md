# CostRoute Lab

[Live demo](https://costroute-lab.fatshin.chatgpt.site) · [Public repository](https://github.com/fatshin/costroute-lab)

CostRoute Lab finds the lowest-cost model route that clears an explicit
macro-average quality floor. It compares a GPT-5.6-only baseline with every
task-to-model assignment using task-level aggregates derived from 20 fixed
evaluation cases. Cost is reported as normalized units for one three-task
bundle.

## Judge path

1. Run `./scripts/run.sh --port 8106`.
2. Open `http://127.0.0.1:8106`.
3. Keep the quality floor at 91 and select **Run analysis**.
4. Confirm 20 cases, a passing three-task macro-average, and a lower normalized bundle cost than baseline.
5. Raise the floor beyond the available scores to see the fail-closed result.

## What is implemented

- three models across extraction, reasoning, and drafting;
- 20-case evaluation dataset;
- unique case-task-model rows and complete model coverage for every case/task;
- exactly one task per case ID and quality values bounded to 0–100;
- positive GPT-5.6 baseline bundle cost before reduction is calculated;
- exhaustive route search;
- macro-average quality-floor enforcement;
- baseline comparison and top feasible frontier.

## Verification

```sh
./scripts/check.sh
```

## OpenAI and Codex

I used Codex with GPT-5.6 to build the exhaustive optimizer, strengthen the
metric contract, add input-mutation tests, create the public interface, and
review the cost claims. GPT-5.6, Terra, and Luna are represented by fixed
synthetic evaluation observations in the submitted fixture. A production
version would ingest measured API usage and grader results.

## Limits

The costs are normalized three-task bundle values, not totals across all 20
cases and not current billing quotes. Quality is the macro-average of the three
selected task-level aggregates. The optimizer does not predict future quality
or route live production traffic.

## License

This project and its synthetic benchmark are released under the MIT License.
