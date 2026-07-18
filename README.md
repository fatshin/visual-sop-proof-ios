# Thesis Breaker Japan

Thesis Breaker Japan searches normalized quarterly evidence for conditions
that disconfirm a Japanese-equity investment thesis. Broken theses appear
before intact ones and retain a page-level source reference.

## Judge path

1. Run `./scripts/run.sh --port 8110`.
2. Open `http://127.0.0.1:8110`.
3. Select **Run analysis**.
4. Confirm one of three theses is broken.
5. Expand `T-1` and inspect the two consecutive declines and its source page.

## What is implemented

- three explicit theses and falsification rules;
- normalized three-quarter evidence;
- consecutive-decline and numeric-floor evaluators;
- disconfirming-evidence-first output;
- source references and a financial-advice disclaimer.

## Verification

```sh
./scripts/check.sh
```

## OpenAI and Codex

Codex was used to implement and review the evaluator. GPT-5.6 can extract
candidate claims from normalized filings, but deterministic rules decide
whether a thesis is broken. The offline path avoids live EDINET dependencies.

## Limits

This is not financial advice. The MVP accepts normalized JSON and does not
download filings, parse XBRL, place trades, or estimate expected return.

