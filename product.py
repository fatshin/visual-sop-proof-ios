from __future__ import annotations

import json
import operator
import re
from typing import Any

from runtime.contracts import Field, Product


DECISIONS = json.dumps([
    {"id": "D-1", "decision": "Use Model A", "owner": "Maya", "reason": "Best measured quality-cost tradeoff", "decided_at": "2026-06-10", "invalidate_when": "quality < 80", "review_when": "cost > 200000"},
    {"id": "D-2", "decision": "Keep vendor B", "owner": "Ken", "reason": "Uptime remains above the service floor", "decided_at": "2026-05-22", "invalidate_when": "uptime < 99.5", "review_when": "incidents > 2"},
    {"id": "D-3", "decision": "Launch workflow C", "owner": "Ari", "reason": "Pilot completion cleared the launch floor", "decided_at": "2026-07-01", "invalidate_when": "completion < 90", "review_when": "complaints > 5"},
], indent=2)
EVIDENCE = json.dumps({
    "D-1": {"quality": 77, "cost": 180000, "source": "eval-2026-07-18.csv"},
    "D-2": {"uptime": 99.8, "incidents": 1, "source": "status-q2.json"},
    "D-3": {"completion": 93, "complaints": 7, "source": "launch-week.csv"},
}, indent=2)
OPS = {"<": operator.lt, ">": operator.gt, "<=": operator.le, ">=": operator.ge, "==": operator.eq}

PRODUCT = Product(
    5, "decision-invalidation-ledger", "Decision Invalidation Ledger",
    "Make assumptions executable so new evidence can reopen yesterday’s decisions.",
    "#14b8a6",
    (Field("decisions", "Decision ledger (JSON)", DECISIONS, 14), Field("evidence", "New evidence (JSON)", EVIDENCE, 14)),
)


def condition_result(condition: Any, values: dict[str, Any]) -> tuple[bool | None, str]:
    if not isinstance(condition, str) or not condition.strip():
        return None, "Missing or non-text condition"
    match = re.fullmatch(r"\s*([a-z_]+)\s*(<=|>=|==|<|>)\s*([\d.]+)\s*", condition)
    if not match:
        return None, f"Unsupported condition: {condition}"
    key, symbol, threshold = match.groups()
    if key not in values:
        return None, f"Missing evidence for {key}"
    try:
        actual, expected = float(values[key]), float(threshold)
    except (TypeError, ValueError):
        return None, f"Non-numeric evidence for {key}"
    return OPS[symbol](actual, expected), f"{key}={actual:g} {symbol} {expected:g}"


def assess(
    decision: dict[str, Any],
    evidence: dict[str, Any],
    *,
    input_errors: list[str] | None = None,
    fallback_id: str = "missing",
) -> dict[str, Any]:
    invalid, invalid_trace = condition_result(decision.get("invalidate_when"), evidence)
    review, review_trace = condition_result(decision.get("review_when"), evidence)
    missing_metadata = [
        key for key in ("decision", "owner", "reason", "decided_at")
        if not isinstance(decision.get(key), str) or not decision[key].strip()
    ]
    source = evidence.get("source")
    source_missing = not isinstance(source, str) or not source.strip()
    evidence_errors = [
        message
        for value, message in ((invalid, invalid_trace), (review, review_trace))
        if value is None
    ]
    reasons = list(input_errors or [])
    if source_missing:
        reasons.append("Missing evidence source")
    if missing_metadata:
        reasons.append(f"Missing decision metadata: {', '.join(missing_metadata)}")
    reasons.extend(evidence_errors)
    if reasons:
        status = "NEEDS_EVIDENCE"
        trace = "; ".join(dict.fromkeys(reasons))
    elif invalid is True:
        status, trace = "INVALIDATED", invalid_trace
    elif review is True:
        status, trace = "AT_RISK", review_trace
    else:
        status, trace = "VALID", f"{invalid_trace}; {review_trace}"
    return {
        "id": decision.get("id", fallback_id),
        "decision": decision.get("decision", ""),
        "owner": decision.get("owner", ""),
        "reason": decision.get("reason", ""),
        "decided_at": decision.get("decided_at", ""),
        "status": status,
        "evidence": trace,
        "source": source if not source_missing else "missing",
        "event": {
            "type": "STATUS_TRANSITION",
            "decision_id": decision.get("id", fallback_id),
            "from": "UNASSESSED",
            "to": status,
            "owner": decision.get("owner", ""),
            "decided_at": decision.get("decided_at", ""),
            "source": source if not source_missing else "missing",
        },
    }


def analyze(payload: dict[str, str]) -> dict[str, Any]:
    decisions, evidence = json.loads(payload["decisions"]), json.loads(payload["evidence"])
    decision_ids = [
        item.get("id")
        for item in decisions
        if isinstance(item.get("id"), str) and item["id"].strip()
    ]
    duplicate_ids = sorted({
        decision_id
        for decision_id in decision_ids
        if decision_ids.count(decision_id) > 1
    })
    input_errors = (
        [f"Duplicate decision ID: {decision_id}" for decision_id in duplicate_ids]
    )
    items = []
    for index, item in enumerate(decisions, start=1):
        decision_id = item.get("id")
        item_errors = []
        fallback_id = f"MISSING_ID_{index}"
        if not isinstance(decision_id, str) or not decision_id.strip():
            item_errors.append("Missing decision ID")
            input_errors.append(f"Decision {index} is missing an ID")
            decision_evidence = {}
        else:
            if decision_id in duplicate_ids:
                item_errors.append(f"Duplicate decision ID: {decision_id}")
            decision_evidence = evidence.get(decision_id, {})
        items.append(
            assess(
                item,
                decision_evidence,
                input_errors=item_errors,
                fallback_id=fallback_id,
            )
        )
    invalid = sum(item["status"] == "INVALIDATED" for item in items)
    at_risk = sum(item["status"] == "AT_RISK" for item in items)
    needs_evidence = sum(item["status"] == "NEEDS_EVIDENCE" for item in items)
    if input_errors:
        overall_status = "INVALID_INPUT"
    elif invalid:
        overall_status = "ACTION_REQUIRED"
    elif at_risk:
        overall_status = "REVIEW_REQUIRED"
    elif needs_evidence:
        overall_status = "EVIDENCE_REQUIRED"
    else:
        overall_status = "CURRENT"
    return {
        "status": overall_status,
        "headline": (
            f"{invalid} decision invalidated by new evidence"
            if invalid
            else f"{at_risk} decision requires review"
            if at_risk
            else f"{needs_evidence} decision needs evidence"
            if needs_evidence
            else "All decisions remain current"
        ),
        "metrics": {
            state.lower(): sum(item["status"] == state for item in items)
            for state in ("VALID", "AT_RISK", "INVALIDATED", "NEEDS_EVIDENCE")
        },
        "items": items,
        "evidence": [{"label": key, "value": value.get("source", "missing")} for key, value in evidence.items()],
        "artifact": {
            "ledger_version": "2",
            "assessments": items,
            "events": [item["event"] for item in items],
            "input_errors": input_errors,
        },
    }


def acceptance(result: dict[str, Any]) -> tuple[bool, dict[str, bool]]:
    checks = {
        "three_decisions": len(result["items"]) == 3,
        "state_distribution": result["metrics"] == {
            "valid": 1,
            "at_risk": 1,
            "invalidated": 1,
            "needs_evidence": 0,
        },
        "source_links": all(item["source"] != "missing" for item in result["items"]),
        "decision_metadata": all(
            item["owner"] and item["reason"] and item["decided_at"]
            for item in result["items"]
        ),
        "transition_events": len(result["artifact"]["events"]) == 3,
        "valid_input": not result["artifact"]["input_errors"],
    }
    return all(checks.values()), checks
