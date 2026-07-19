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
    pii_match = re.search(
        r"(?im)^POL-01:\s*External transmissions containing PII must be blocked\.$",
        policy,
    )
    if not pii_match:
        raise ValueError("Ambiguous policy: POL-01 must use the supported PII-block grammar.")
    threshold_match = re.search(
        r"(?im)^POL-02:\s*Refunds above \$([0-9]+(?:\.[0-9]+)?) and production deletion require human approval\.$",
        policy,
    )
    if not threshold_match:
        raise ValueError("Ambiguous policy: POL-02 must use the supported approval grammar.")
    allowlists: dict[str, list[str]] = {}
    role_rule_ids: dict[str, str] = {}
    for rule_id, role, tools in re.findall(
        r"(?im)^(POL-\d+):\s*(Support|Finance)\s+may use\s+(.+?)\.$",
        policy,
    ):
        normalized_role = role.lower()
        allowlists[normalized_role] = [
            tool.strip() for tool in re.split(r"\s+and\s+|,\s*", tools)
        ]
        role_rule_ids[normalized_role] = rule_id
    admin_match = re.search(
        r"(?im)^(POL-\d+):\s*Admin may use every registered tool\.$",
        policy,
    )
    if admin_match:
        allowlists["admin"] = ["*"]
        role_rule_ids["admin"] = admin_match.group(1)
    if set(allowlists) != {"support", "finance", "admin"}:
        raise ValueError("Ambiguous policy: one or more role tool lists could not be compiled.")
    approval_tools = ["delete_production"]
    return {
        "version": "policy-ir/v1",
        "refund_approval_above": float(threshold_match.group(1)),
        "role_allowlists": allowlists,
        "role_rule_ids": role_rule_ids,
        "approval_tools": approval_tools,
        "rules": [
            {"id": "POL-01", "predicate": "external && pii", "effect": "BLOCK"},
            {
                "id": "POL-02",
                "predicate": f"amount > {threshold_match.group(1)} || tool in approval_tools",
                "effect": "APPROVAL_REQUIRED",
            },
            *[
                {
                    "id": role_rule_ids[role],
                    "predicate": f"role == {role} && tool not in role_allowlist",
                    "effect": "BLOCK",
                }
                for role in ("support", "finance", "admin")
            ],
        ],
        "citations": citations,
    }


def evaluate(ir: dict[str, Any], scenario: dict[str, Any]) -> dict[str, str]:
    if scenario.get("external") and scenario.get("pii"):
        return {"decision": "BLOCK", "rule": "POL-01", "reason": ir["citations"]["POL-01"]}
    role, tool = str(scenario.get("role", "")), str(scenario.get("tool", ""))
    allowed = set(ir["role_allowlists"].get(role, []))
    if "*" not in allowed and tool not in allowed:
        rule_id = ir["role_rule_ids"].get(role)
        if not rule_id:
            raise ValueError(f"Unknown role: {role or 'MISSING'}")
        return {
            "decision": "BLOCK",
            "rule": rule_id,
            "reason": ir["citations"][rule_id],
        }
    if (
        float(scenario.get("amount", 0)) > ir["refund_approval_above"]
        or tool in ir["approval_tools"]
    ):
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
    citations = result["artifact"]["citations"]
    non_allow = [item for item in result["items"] if item["decision"] != "ALLOW"]
    checks = {
        "seven_scenarios": len(result["items"]) == 7,
        "expected_decisions": result["metrics"] == {"ALLOW": 3, "BLOCK": 2, "APPROVAL_REQUIRED": 2},
        "source_citations": all(
            item["rule"] in citations and item["reason"] == citations[item["rule"]]
            for item in non_allow
        ),
        "compiled_threshold": result["artifact"]["refund_approval_above"] == 500,
        "compiled_allowlists": result["artifact"]["role_allowlists"]["support"] == ["lookup_customer", "draft_reply"],
    }
    return all(checks.values()), checks
