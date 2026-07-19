# Public Notice Stress Test

[Live demo](https://public-notice-stress-test.fatshin.chatgpt.site) · [Public repository](https://github.com/fatshin/public-notice-stress-test)

Public Notice Stress Test checks a public notice against authoritative facts
before publication. It highlights conflicting dates, amounts, eligibility,
contact details, and unsupported promises, then emits source-linked repair
instructions for a communications owner.

## Judge path

1. Run `./scripts/run.sh --port 8103`.
2. Open `http://127.0.0.1:8103`.
3. Select **Run analysis** with the supplied notice and source facts.
4. Confirm five direct conflicts and one unsupported exception.
5. Compare every repair with the Evidence column.

## What is implemented

- label-bound claim extraction that ignores unrelated issue dates and press emails;
- fail-closed `MISSING` and `AMBIGUOUS` results for absent or conflicting labels;
- exact comparison with a normalized source record;
- unsupported-exception detection;
- release-blocking status and six source-linked repair instructions;
- editable input for reviewer-created edge cases.

## Verification

```sh
./scripts/check.sh
```

## OpenAI and Codex

I used Codex with GPT-5.6 to implement claim extraction, evidence comparison,
release gating, regression tests, the public interface, and review. A future
live path can use GPT-5.6 for misreading simulation and rewrite suggestions;
deterministic fact comparison remains the release gate. The tested offline
fixture is the primary submitted evidence.

## Limits

The MVP expects normalized authoritative facts. It does not scrape government
sites, establish legal validity, draft approved public wording, or publish a
corrected notice automatically.

## License

This project and its synthetic notice are released under the MIT License.
