# Decision Invalidation Ledger

[Live demo](https://decision-invalidation-ledger.fatshin.chatgpt.site) · [Public repository](https://github.com/fatshin/decision-invalidation-ledger)

Decision Invalidation Ledger stores a decision beside the evidence conditions
that would reopen it. New evidence changes each item to `VALID`, `AT_RISK`,
`INVALIDATED`, or `NEEDS_EVIDENCE` without rewriting the original decision.
Missing facts or provenance never make a decision appear current.

## Judge path

1. Run `./scripts/run.sh --port 8105`.
2. Open `http://127.0.0.1:8105`.
3. Select **Run analysis**.
4. Confirm one decision in each state.
5. Expand the invalidated decision and follow its value, threshold, and source.

## What is implemented

- three-decision JSON ledger;
- small auditable condition DSL;
- invalidation-before-review precedence;
- fail-closed handling for missing values, sources, and decision metadata;
- source-linked status evidence;
- owner-linked machine-readable status-transition events.

## Verification

```sh
./scripts/check.sh
```

## OpenAI and Codex

I used Codex with GPT-5.6 to implement the ledger schema, trigger evaluator,
input-mutation tests, public interface, and validation. A future live path can
use GPT-5.6 to extract candidate assumptions and conditions from decision
documents, but humans approve the ledger and the deterministic evaluator owns
status changes.

## Limits

The DSL supports numeric comparisons only. The MVP emits assessment events but
does not fetch external evidence, send notifications, or change operational
systems when a decision becomes invalid.

## License

This project and its synthetic ledger are released under the MIT License.
