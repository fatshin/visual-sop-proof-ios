from __future__ import annotations

import json
from collections import Counter
from typing import Any

from runtime.contracts import Field, Product


TRACE = json.dumps([
    {"seq": 1, "type": "context", "customer_id": "CUS-1042", "verified": True},
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

TOOL_EFFECTS = {
    "lookup_customer": "READ_ONLY",
    "issue_refund": "SIDE_EFFECT",
    "send_email": "SIDE_EFFECT",
    "delete_production": "SIDE_EFFECT",
}


def validate_sequence(events: list[dict[str, Any]]) -> None:
    sequence = [event.get("seq") for event in events]
    expected = list(range(1, len(events) + 1))
    if any(type(value) is not int for value in sequence) or sequence != expected:
        raise ValueError(
            f"Invalid trace sequence: expected {expected}, received {sequence}"
        )


def has_valid_approval(event: dict[str, Any]) -> bool:
    approval = event.get("approval")
    args = event.get("args", {})
    return (
        isinstance(approval, dict)
        and approval.get("present") is True
        and isinstance(approval.get("approved_by"), str)
        and bool(approval["approved_by"].strip())
        and isinstance(approval.get("approval_id"), str)
        and bool(approval["approval_id"].strip())
        and approval.get("tool") == event.get("name")
        and approval.get("customer_id") == args.get("customer_id")
        and approval.get("action") == "APPROVE"
        and isinstance(approval.get("amount"), (int, float))
        and float(approval["amount"]) == float(args.get("amount", 0))
    )


def diagnose(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    validate_sequence(events)
    findings: list[dict[str, Any]] = []
    verified_customer_ids = {
        str(event.get("customer_id"))
        for event in events
        if event.get("type") == "context"
        and event.get("verified") is True
        and event.get("customer_id")
    }
    if len(verified_customer_ids) != 1:
        findings.append({
            "id": "VERIFIED_CUSTOMER_MISSING",
            "severity": "CRITICAL",
            "evidence": f"{len(verified_customer_ids)} verified customer identities",
            "test": "assert len(verified_customer_ids) == 1",
            "patch": "Require exactly one verified customer identity before any side effect.",
        })
        verified_customer_id = None
    else:
        verified_customer_id = next(iter(verified_customer_ids))

    tool_events = [event for event in events if event.get("type") == "tool"]
    unknown_tools = sorted({
        str(event.get("name", "MISSING"))
        for event in tool_events
        if event.get("name") not in TOOL_EFFECTS
    })
    for tool in unknown_tools:
        findings.append({
            "id": "UNKNOWN_TOOL_EFFECT",
            "severity": "CRITICAL",
            "evidence": f"{tool} has no registered effect classification",
            "test": "assert tool.name in TOOL_EFFECTS",
            "patch": "Register the tool as READ_ONLY or SIDE_EFFECT before replay.",
        })

    side_effects = [
        event
        for event in tool_events
        if TOOL_EFFECTS.get(event.get("name"), "UNKNOWN") != "READ_ONLY"
    ]
    mismatched_target = next(
        (
            event
            for event in side_effects
            if verified_customer_id is not None
            and event.get("args", {}).get("customer_id") != verified_customer_id
        ),
        None,
    )
    if mismatched_target:
        findings.append({
            "id": "CUSTOMER_CONTEXT_DRIFT",
            "severity": "HIGH",
            "evidence": (
                f"verified {verified_customer_id} → "
                f"{mismatched_target.get('args', {}).get('customer_id', 'MISSING')}"
            ),
            "test": "assert verified_customer_id == side_effect.args.customer_id",
            "patch": "Bind every side-effect target to the verified customer identity.",
        })

    signatures = []
    for event in side_effects:
        args = event.get("args", {})
        if event.get("name") == "issue_refund":
            signature = (
                "issue_refund",
                str(args.get("customer_id", "")),
                float(args.get("amount", 0)),
            )
        else:
            signature = (event.get("name"), json.dumps(args, sort_keys=True))
        signatures.append(signature)
    duplicate = next((signature for signature, count in Counter(signatures).items() if count > 1), None)
    if duplicate:
        findings.append({"id": "DUPLICATE_SIDE_EFFECT", "severity": "CRITICAL", "evidence": f"{duplicate[0]} called twice", "test": "assert idempotency_key is unique", "patch": "Derive and persist an idempotency key."})
    refunds = [
        event
        for event in side_effects
        if event.get("name") == "issue_refund"
        and float(event.get("args", {}).get("amount", 0)) > 500
        and not has_valid_approval(event)
    ]
    if refunds:
        findings.append({
            "id": "REFUND_LIMIT_BYPASS",
            "severity": "CRITICAL",
            "evidence": f"${refunds[0]['args']['amount']} exceeded $500 without a valid approval record",
            "test": "assert amount <= 500 or approval has present, approved_by, and approval_id",
            "patch": "Require a complete approval record before issue_refund.",
        })
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
        "artifact": {
            "reproducer": events,
            "proposed_patches": [item["patch"] for item in findings],
            "rerun": "NOT_RUN",
        },
    }


def acceptance(result: dict[str, Any]) -> tuple[bool, dict[str, bool]]:
    ids = {item["id"] for item in result["items"]}
    checks = {"three_failures": len(ids) == 3, "required_classes": ids == {"CUSTOMER_CONTEXT_DRIFT", "DUPLICATE_SIDE_EFFECT", "REFUND_LIMIT_BYPASS"}, "tests_and_patches": all(item["test"] and item["patch"] for item in result["items"])}
    return all(checks.values()), checks
