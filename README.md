# Agent Autopsy

[Live demo](https://agent-autopsy.fatshin.chatgpt.site) · [Public repository](https://github.com/fatshin/agent-autopsy)

Agent Autopsy converts a failed support-agent trace into a reproducible failure
report, regression-test assertions, and a narrow patch plan. It never applies a
patch automatically.

## Judge path

1. Run `./scripts/run.sh --port 8102`.
2. Open `http://127.0.0.1:8102`.
3. Select **Run analysis** with the supplied five-event trace.
4. Confirm three findings: customer drift, duplicate refund, and approval-limit bypass.
5. Expand each finding to inspect its evidence, regression assertion, and bounded patch.

## What is implemented

- trace normalization and event-order evidence;
- customer-context drift detection;
- duplicate side-effect detection using canonical tool signatures;
- refund-limit violation detection;
- one regression assertion and one limited patch per failure;
- deterministic rerun artifact.

## Verification

```sh
./scripts/check.sh
```

## OpenAI and Codex

Codex was used for implementation and adversarial review. GPT-5.6 can be added
as a hypothesis generator over the normalized trace, but deterministic
detectors decide whether the three acceptance failures are present. The offline
judge path is intentionally credential-free.

## Limits

The MVP accepts normalized JSON traces and proposes patches. It does not execute
untrusted code, replay production transactions, or mutate a repository.
