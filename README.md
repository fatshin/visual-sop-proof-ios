# Agent Autopsy

[Live demo](https://agent-autopsy.fatshin.chatgpt.site) · [Public repository](https://github.com/fatshin/agent-autopsy)

Agent Autopsy converts a failed support-agent trace into reproducible failure
modes, regression-test assertions, and scoped patch suggestions. It never
applies a patch automatically.

## Judge path

1. Run `./scripts/run.sh --port 8102`.
2. Open `http://127.0.0.1:8102`.
3. Select **Run analysis** with the supplied five-event trace.
4. Confirm three findings: customer drift, duplicate refund, and approval-limit bypass.
5. Expand each finding to inspect its evidence, regression assertion, and bounded patch.

## What is implemented

- contiguous trace-sequence validation;
- verified-customer to side-effect target matching;
- duplicate side-effect detection that excludes registered read-only tools;
- fail-closed handling for tools without an effect classification;
- refund-limit validation against a complete approval record;
- one regression assertion and one limited patch per failure;
- an explicit `NOT_RUN` replay state until a patch is actually executed.

## Verification

```sh
./scripts/check.sh
```

## OpenAI and Codex

I used Codex with GPT-5.6 to implement trace normalization, deterministic
failure-mode detectors, regression tests, the public interface, and adversarial review. A future live
path can use GPT-5.6 as a hypothesis generator over an unstructured trace, but
deterministic detectors decide whether the three acceptance failures are
present. The submitted judge path is intentionally credential-free.

## Limits

The MVP accepts normalized JSON traces and proposes patches. It does not execute
untrusted code, replay production transactions, or mutate a repository.

## License

This project and its synthetic trace are released under the MIT License.
