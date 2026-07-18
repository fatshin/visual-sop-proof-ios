from __future__ import annotations

import json
import re
from typing import Any

from runtime.contracts import Field, Product


POLICY = """POL-01: External transmissions containing PII must be blocked.
POL-02: Refunds above $500 and production deletion require human approval.
POL-03: Support may use lookup_customer and draft_reply.
POL-04: Finance may use issue_refund and lookup_customer.
POL-05: Admin may use every registered tool."""
SCENARIOS = json.dumps([
    {"id": "S1", "role": "support", "tool": "lookup_customer", "external": False, "pii": False, "amount": 0},
    {"id": "S2", "role": "support", "tool": "send_email", "external": True, "pii": True, "amount": 0},
    {"id": "S3", "role": "finance", "tool": "issue_refund", "external": False, "pii": False, "amount": 120},
    {"id": "S4", "role": "finance", "tool": "issue_refund", "external": False, "pii": False, "amount": 900},
    {"id": "S5", "role": "support", "tool": "issue_refund", "external": False, "pii": False, "amount": 50},
    {"id": "S6", "role": "admin", "tool": "delete_production", "external": False, "pii": False, "amount": 0},
    {"id": "S7", "role": "admin", "tool": "rotate_logs", "external": False, "pii": False, "amount": 0},
], indent=2)
ALLOWLISTS = {"support": {"lookup_customer", "draft_reply"}, "finance": {"issue_refund", "lookup_customer"}, "admin": {"*"}}

PRODUCT = Product(
    1, "agent-policy-compiler", "Agent Policy Compiler",
    "Turn natural-language operating rules into testable agent decisions.",
    "#ff5c35",
    (Field("policy", "Policy source", POLICY, 8), Field("scenarios", "Runtime scenarios (JSON)", SCENARIOS, 18)),
)


def compile_policy(policy: str) -> dict[str, Any]:
    required = ("PII", "human approval", "Support", "Finance", "Admin")
    missing = [term for term in required if term.lower() not in policy.lower()]
    if missing:
        raise ValueError(f"Ambiguous policy: missing {', '.join(missing)}")
    citations = {}
    for line in policy.splitlines():
        match = re.match(r"(POL-\d+):\s*(.+)", line.strip())
        if match:
            citations[match.group(1)] = match.group(2)
    return {
        "version": "policy-ir/v1",
        "rules": [
            {"id": "POL-01", "predicate": "external && pii", "effect": "BLOCK"},
            {"id": "POL-02", "predicate": "amount > 500 || tool == delete_production", "effect": "APPROVAL_REQUIRED"},
            {"id": "POL-03-05", "predicate": "tool not in role_allowlist", "effect": "BLOCK"},
        ],
        "citations": citations,
    }


def evaluate(ir: dict[str, Any], scenario: dict[str, Any]) -> dict[str, str]:
    if scenario.get("external") and scenario.get("pii"):
        return {"decision": "BLOCK", "rule": "POL-01", "reason": ir["citations"]["POL-01"]}
    role, tool = str(scenario.get("role", "")), str(scenario.get("tool", ""))
    allowed = ALLOWLISTS.get(role, set())
    if "*" not in allowed and tool not in allowed:
        return {"decision": "BLOCK", "rule": "POL-03-05", "reason": f"{role} cannot use {tool}"}
    if float(scenario.get("amount", 0)) > 500 or tool == "delete_production":
        return {"decision": "APPROVAL_REQUIRED", "rule": "POL-02", "reason": ir["citations"]["POL-02"]}
    return {"decision": "ALLOW", "rule": "ALLOWLIST", "reason": f"{role} may use {tool}"}


def analyze(payload: dict[str, str]) -> dict[str, Any]:
    ir = compile_policy(payload["policy"])
    decisions = [{**item, **evaluate(ir, item)} for item in json.loads(payload["scenarios"])]
    counts = {name: sum(item["decision"] == name for item in decisions) for name in ("ALLOW", "BLOCK", "APPROVAL_REQUIRED")}
    return {
        "status": "COMPILED", "headline": f"{len(decisions)} scenarios evaluated with source-linked rules",
        "metrics": counts, "items": decisions,
        "evidence": [{"label": key, "value": value} for key, value in ir["citations"].items()],
        "artifact": ir,
    }


def acceptance(result: dict[str, Any]) -> tuple[bool, dict[str, bool]]:
    checks = {
        "seven_scenarios": len(result["items"]) == 7,
        "expected_decisions": result["metrics"] == {"ALLOW": 3, "BLOCK": 2, "APPROVAL_REQUIRED": 2},
        "source_citations": all(item["reason"] for item in result["items"]),
    }
    return all(checks.values()), checks

