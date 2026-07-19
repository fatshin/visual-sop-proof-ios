# Meeting to Merge

[Live demo](https://meeting-to-merge.fatshin.chatgpt.site) · [Public repository](https://github.com/fatshin/meeting-to-merge)

Meeting to Merge carries a complete, uniquely identified set of four cited
meeting requirements into deterministic scenario checks and a minimal proposed
diff. A human approval boundary remains between the proposal and repository
mutation.

## Judge path

1. Run `./scripts/run.sh --port 8104`.
2. Open `http://127.0.0.1:8104`.
3. Select **Run analysis**.
4. Confirm four speaker-and-timestamp citations and four baseline failures.
5. Expand the machine-readable artifact and inspect the unified diff.
6. Remove the approval definition and rerun to see the fail-closed ambiguity gate.

## What is implemented

- timestamped `REQ-*` extraction;
- explicit ambiguity gate;
- completeness, unique-ID, supported-wording, and requirement-to-check gates;
- one deterministic scenario-check name per requirement;
- a bounded diff for validation, approval, receipt, and idempotency;
- baseline FAIL and deterministic post-patch expectation PASS evidence;
- human apply requirement.

## Verification

```sh
./scripts/check.sh
```

## OpenAI and Codex

I used Codex with GPT-5.6 to implement transcript normalization, requirement
extraction, baseline-failure reproduction, patch generation, regression tests,
and the public interface. A future live path can use GPT-5.6 to draft
requirements and patch candidates, while deterministic validation enforces
citations, ambiguity handling, and the human-apply boundary.

## Limits

The MVP operates on a bounded source snippet. It structurally parses the source
without executing it, and it does not apply or execute the proposed patch. Its
scenario checks are deterministic fixture evidence, not a CI rerun.

## License

This project and its synthetic transcript are released under the MIT License.
