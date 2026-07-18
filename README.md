# Agent Policy Compiler

[Live demo](https://agent-policy-compiler.fatshin.chatgpt.site) · [Public repository](https://github.com/fatshin/agent-policy-compiler)

Agent Policy Compiler turns a short operating policy into an inspectable policy
IR, then evaluates runtime tool calls as `ALLOW`, `BLOCK`, or
`APPROVAL_REQUIRED`. Every non-allow decision carries the policy sentence that
caused it.

## Judge path

1. Run `./scripts/run.sh --port 8101`.
2. Open `http://127.0.0.1:8101`.
3. Keep the supplied policy and seven scenarios.
4. Select **Run analysis**.
5. Confirm 3 ALLOW, 2 BLOCK, and 2 APPROVAL_REQUIRED decisions.
6. Expand a decision and compare its rule ID with the Evidence column.

The demo is deterministic and requires no API key. It does not represent the
fixture as a live model response.

## What is implemented

- policy completeness gate that stops compilation on missing policy domains;
- a versioned Policy IR with source citations;
- role-based tool access, PII egress blocking, and high-risk approval;
- seven acceptance scenarios and a machine-readable artifact;
- loopback-only product UI with no third-party runtime dependency.

## Verification

```sh
./scripts/check.sh
```

## OpenAI and Codex

I used Codex with GPT-5.6 to turn the policy idea into the intermediate
representation, input-driven evaluator, regression cases, public interface, and
review evidence. A future live extension can use GPT-5.6 Structured Outputs to
draft the Policy IR; the local validator remains authoritative and rejects
incomplete or unsupported rules. The submitted judge path uses the tested
fixture so it remains reviewable without credentials.

## Limits

This MVP deliberately supports three rule families. It is a policy compiler
proof, not a general authorization system or a production policy engine.

## License

This project and its synthetic fixture are released under the MIT License.
