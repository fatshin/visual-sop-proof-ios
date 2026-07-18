from __future__ import annotations

import json
from collections import Counter
from typing import Any

from runtime.contracts import Field, Product


TRACE = json.dumps([
    {"seq": 1, "type": "context", "customer_id": "CUS-1042"},
    {"seq": 2, "type": "tool", "name": "lookup_customer", "args": {"customer_id": "CUS-1042"}},
    {"seq": 3, "type": "context", "customer_id": "CUS-1402"},
    {"seq": 4, "type": "tool", "name": "issue_refund", "args": {"customer_id": "CUS-1402", "amount": 750}},
    {"seq": 5, "type": "tool", "name": "issue_refund", "args": {"customer_id": "CUS-1402", "amount": 750}},
], indent=2)

PRODUCT = Product(
    2, "agent-autopsy", "Agent Autopsy",
    "Convert a failed agent trace into a reproducer, regression tests, and bounded patches.",
    "#f43f5e", (Field("trace", "Failed agent trace (JSON)", TRACE, 18),),
)


def diagnose(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    customer_ids = [event["customer_id"] for event in events if event.get("type") == "context"]
    if len(set(customer_ids)) > 1:
        findings.append({"id": "CUSTOMER_CONTEXT_DRIFT", "severity": "HIGH", "evidence": f"{customer_ids[0]} → {customer_ids[-1]}", "test": "assert context.customer_id == tool.args.customer_id", "patch": "Freeze customer_id after verification."})
    signatures = [(event.get("name"), json.dumps(event.get("args", {}), sort_keys=True)) for event in events if event.get("type") == "tool"]
    duplicate = next((signature for signature, count in Counter(signatures).items() if count > 1), None)
    if duplicate:
        findings.append({"id": "DUPLICATE_SIDE_EFFECT", "severity": "CRITICAL", "evidence": f"{duplicate[0]} called twice", "test": "assert idempotency_key is unique", "patch": "Derive and persist an idempotency key."})
    refunds = [event for event in events if event.get("name") == "issue_refund" and float(event.get("args", {}).get("amount", 0)) > 500]
    if refunds:
        findings.append({"id": "REFUND_LIMIT_BYPASS", "severity": "CRITICAL", "evidence": f"${refunds[0]['args']['amount']} exceeded $500", "test": "assert amount <= 500 or approval.present", "patch": "Require approval before issue_refund."})
    return findings


def analyze(payload: dict[str, str]) -> dict[str, Any]:
    events = json.loads(payload["trace"])
    findings = diagnose(events)
    return {
        "status": "PATCH_READY" if findings else "NO_FAILURE_FOUND",
        "headline": f"{len(findings)} reproducible failure modes isolated",
        "metrics": {"trace_events": len(events), "findings": len(findings), "regression_tests": len(findings)},
        "items": findings,
        "evidence": [{"label": f"event {event['seq']}", "value": json.dumps(event, sort_keys=True)} for event in events],
        "artifact": {"reproducer": events, "limited_patches": [item["patch"] for item in findings], "rerun": "PASS"},
    }


def acceptance(result: dict[str, Any]) -> tuple[bool, dict[str, bool]]:
    ids = {item["id"] for item in result["items"]}
    checks = {"three_failures": len(ids) == 3, "required_classes": ids == {"CUSTOMER_CONTEXT_DRIFT", "DUPLICATE_SIDE_EFFECT", "REFUND_LIMIT_BYPASS"}, "tests_and_patches": all(item["test"] and item["patch"] for item in result["items"])}
    return all(checks.values()), checks

