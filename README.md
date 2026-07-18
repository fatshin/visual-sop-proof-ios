# Public Notice Stress Test

Public Notice Stress Test checks a public notice against authoritative facts
before publication. It highlights conflicting dates, amounts, eligibility,
contact details, and unsupported promises, then emits source-linked repairs.

## Judge path

1. Run `./scripts/run.sh --port 8103`.
2. Open `http://127.0.0.1:8103`.
3. Select **Run analysis** with the supplied notice and source facts.
4. Confirm five direct conflicts and one unsupported exception.
5. Compare every repair with the Evidence column.

## What is implemented

- fixed claim extraction for dates, currency, age, residency, and email;
- exact comparison with a normalized source record;
- unsupported-exception detection;
- release-blocking status and six source-linked repairs;
- editable input for reviewer-created edge cases.

## Verification

```sh
./scripts/check.sh
```

## OpenAI and Codex

Codex was used to build and review the product. GPT-5.6 is reserved for
misreading simulation and rewrite suggestions; deterministic fact comparison
remains the release gate. The offline path is the primary submitted evidence.

## Limits

The MVP expects normalized authoritative facts. It does not scrape government
sites, establish legal validity, or publish a corrected notice automatically.

