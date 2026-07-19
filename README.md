# Thesis Breaker Japan

[Live demo](https://thesis-breaker-japan.fatshin.chatgpt.site) · [Public repository](https://github.com/fatshin/thesis-breaker-japan)

Thesis Breaker Japan searches normalized quarterly evidence for conditions
that disconfirm a Japanese-equity investment thesis. Broken theses appear
before intact ones regardless of input order. Every assessment retains a
validated local page reference and states both break and reversal conditions.

## Judge path

1. Run `./scripts/run.sh --port 8110`.
2. Open `http://127.0.0.1:8110`.
3. Select **Run analysis**.
4. Confirm one of three theses is broken.
5. Expand `T-1` and inspect the two consecutive declines, reversal condition,
   and all three source pages.

## What is implemented

- three explicit theses and falsification rules;
- normalized three-quarter evidence;
- strict `YYYY-Qn` validation, chronological sorting, and duplicate rejection;
- finite metric validation and an explicit supported-rule parser;
- minimum three-quarter history for two consecutive quarter-to-quarter declines;
- consecutive-decline and numeric-floor evaluators;
- stable disconfirming-evidence-first output;
- validated source-file/page anchors, reversal conditions, and a
  financial-advice disclaimer.

## Verification

```sh
./scripts/check.sh
```

## OpenAI and Codex

I used Codex with GPT-5.6 to implement the evaluator, multi-period source
citations, input-mutation tests, public interface, and review. A future live
path can use GPT-5.6 to extract candidate claims from normalized filings, but
deterministic rules decide whether a thesis is broken. The submitted path uses
synthetic filings and avoids live EDINET dependencies.

## Limits

This is not financial advice. The MVP accepts normalized JSON and does not
download filings, parse XBRL, place trades, or estimate expected return.

## License

This project and its synthetic filings are released under the MIT License.
