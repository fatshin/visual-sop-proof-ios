from __future__ import annotations

import ast
import difflib
import re
from typing import Any

from runtime.contracts import Field, Product


TRANSCRIPT = """[00:18] Maya: REQ-1 Checkout must reject a quantity below 1.
[00:44] Ken: REQ-2 Orders over $500 require manager approval.
[01:12] Maya: REQ-3 The receipt must show the order ID.
[01:48] Ken: REQ-4 Retry must not create a second charge.
[02:10] Maya: Approval means a non-empty manager token."""
SOURCE = """def checkout(quantity, total, manager_token="", order_id=""):
    approved = total >= 500
    charge()
    return {"ok": True, "order": ""}
"""

PRODUCT = Product(
    4, "meeting-to-merge", "Meeting to Merge",
    "Carry an approved requirement from spoken words to a test and minimal patch.",
    "#8b5cf6",
    (Field("transcript", "Meeting transcript", TRANSCRIPT, 10), Field("source", "Target source", SOURCE, 9)),
)

REQUIREMENT_TESTS = {
    "REQ-1": ("test_rejects_quantity_below_one", re.compile(r"\breject\b.+\bquantity\b.+\bbelow 1\b", re.I)),
    "REQ-2": ("test_large_order_requires_manager_token", re.compile(r"\bover \$?500\b.+\brequire\b.+\bmanager approval\b", re.I)),
    "REQ-3": ("test_receipt_includes_order_id", re.compile(r"\breceipt\b.+\bshow\b.+\border ID\b", re.I)),
    "REQ-4": ("test_retry_uses_idempotency_key", re.compile(r"\bretry\b.+\bnot create\b.+\bsecond charge\b", re.I)),
}
CONTRADICTION_PATTERNS = {
    "REQ-1": re.compile(
        r"\b(?:allow|accept)\b.+\bquantity\b.+\bbelow 1\b"
        r"|(?=.*\breject\b.+\bquantity\b.+\bbelow 1\b)"
        r"(?=.*(?:\b(?:allow|accept)\b.+\b(?:quantity\s+)?zero\b"
        r"|\b(?:quantity\s+)?zero\b.+\b(?:allow|accept|accepted)\b))",
        re.I,
    ),
    "REQ-2": re.compile(r"\b(?:no|not)\b.+\bmanager approval\b|\bdo(?:es)? not require\b.+\bapproval\b", re.I),
    "REQ-3": re.compile(r"\b(?:must not|should not|omit)\b.+\border ID\b", re.I),
    "REQ-4": re.compile(
        r"\bretry\b.+(?:\b(?:may|can)\b.+|\bmust create\b.+)"
        r"\b(?:second|duplicate)\s+charge\b",
        re.I,
    ),
}
EXPECTED_REQUIREMENT_IDS = set(REQUIREMENT_TESTS)
BROKEN_BLOCK = (
    '    approved = total >= 500\n'
    '    charge()\n'
    '    return {"ok": True, "order": ""}'
)
FIXED_BLOCK = (
    '    if quantity < 1:\n'
    '        return {"ok": False, "error": "invalid_quantity"}\n'
    '    if not order_id:\n'
    '        return {"ok": False, "error": "missing_order_id"}\n'
    '    if total > 500 and not manager_token:\n'
    '        return {"ok": False, "error": "approval_required"}\n'
    '    charge(idempotency_key=order_id)\n'
    '    return {"ok": True, "order": order_id}'
)


def requirements(transcript: str) -> list[dict[str, str]]:
    output = []
    for line in transcript.splitlines():
        match = re.search(r"\[(\d+:\d+)\]\s+([^:]+):\s+(REQ-\d+)\s+(.+)", line)
        if match:
            output.append({"timestamp": match.group(1), "speaker": match.group(2), "id": match.group(3), "text": match.group(4)})
    return output


def source_shape_errors(source: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ["Target source is not valid Python syntax."]
    checkouts = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "checkout"
    ]
    if len(checkouts) != 1:
        return ["Target source must define exactly one checkout function."]
    arguments = {argument.arg for argument in checkouts[0].args.args}
    expected_arguments = {"quantity", "total", "manager_token", "order_id"}
    if not expected_arguments.issubset(arguments):
        return ["Checkout is missing one or more required parameters."]
    checkout_source = ast.get_source_segment(source, checkouts[0]) or ""
    if BROKEN_BLOCK not in checkout_source or source.count(BROKEN_BLOCK) != 1:
        return ["Target source does not contain the supported broken checkout block."]
    return []


def generated_source_errors(source: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ["Generated source is not valid Python syntax."]
    checkouts = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "checkout"
    ]
    if len(checkouts) != 1:
        return ["Generated source must define exactly one checkout function."]
    checkout = checkouts[0]
    guard_indexes = [
        index
        for index, statement in enumerate(checkout.body)
        if (
            isinstance(statement, ast.If)
            and isinstance(statement.test, ast.UnaryOp)
            and isinstance(statement.test.op, ast.Not)
            and isinstance(statement.test.operand, ast.Name)
            and statement.test.operand.id == "order_id"
        )
    ]
    if len(guard_indexes) != 1:
        return ["Generated checkout must contain exactly one non-empty order-ID guard."]
    guard_index = guard_indexes[0]
    calls_before_guard = [
        node
        for statement in checkout.body[:guard_index]
        for node in ast.walk(statement)
        if isinstance(node, ast.Call)
    ]
    if calls_before_guard:
        return ["Generated checkout contains a call before the order-ID guard."]
    charge_calls = [
        node
        for statement in checkout.body[guard_index + 1:]
        for node in ast.walk(statement)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "charge"
    ]
    if len(charge_calls) != 1:
        return ["Generated checkout must contain exactly one charge call after the order-ID guard."]
    idempotency_keywords = [
        keyword
        for keyword in charge_calls[0].keywords
        if keyword.arg == "idempotency_key"
    ]
    if (
        len(idempotency_keywords) != 1
        or not isinstance(idempotency_keywords[0].value, ast.Name)
        or idempotency_keywords[0].value.id != "order_id"
    ):
        return ["Generated charge must use order_id as its idempotency key."]
    return []


def build_patch(source: str) -> tuple[str, dict[str, str], str, list[str]]:
    source = source.replace("\r\n", "\n").replace("\r", "\n")
    tests = {
        requirement_id: value[0]
        for requirement_id, value in REQUIREMENT_TESTS.items()
    }
    source_errors = source_shape_errors(source)
    if source_errors:
        return "", tests, "", source_errors
    fixed = source.replace(BROKEN_BLOCK, FIXED_BLOCK, 1)
    validation_errors = generated_source_errors(fixed)
    if validation_errors:
        return "", tests, fixed, validation_errors
    patch = "\n".join(difflib.unified_diff(source.splitlines(), fixed.splitlines(), "before.py", "after.py", lineterm=""))
    return patch, tests, fixed, []


def checkout_fixture(
    quantity: int,
    total: float,
    manager_token: str,
    order_id: str,
    *,
    patched: bool,
    retry: bool = False,
) -> dict[str, Any]:
    if patched and quantity < 1:
        return {"ok": False, "error": "invalid_quantity", "charges": 0}
    if patched and not order_id:
        return {"ok": False, "error": "missing_order_id", "charges": 0}
    if patched and total > 500 and not manager_token:
        return {"ok": False, "error": "approval_required", "charges": 0}
    return {
        "ok": True,
        "order": order_id if patched else "",
        "charges": 1 if patched or not retry else 2,
    }


def run_fixture_checks(*, patched: bool) -> list[bool]:
    invalid = checkout_fixture(0, 100, "", "O-1", patched=patched)
    approval = checkout_fixture(1, 501, "", "O-2", patched=patched)
    receipt = checkout_fixture(1, 100, "", "O-3", patched=patched)
    retry = checkout_fixture(1, 100, "", "O-4", patched=patched, retry=True)
    return [
        invalid.get("error") == "invalid_quantity",
        approval.get("error") == "approval_required",
        receipt.get("order") == "O-3",
        retry.get("charges") == 1,
    ]


def run_patch_safety_checks(*, patched: bool) -> list[bool]:
    missing_order_id = checkout_fixture(1, 100, "", "", patched=patched)
    return [
        missing_order_id.get("error") == "missing_order_id",
        missing_order_id.get("charges") == 0,
    ]


def analyze(payload: dict[str, str]) -> dict[str, Any]:
    reqs = requirements(payload["transcript"])
    patch, tests, generated_source, generated_validation_errors = build_patch(payload["source"])
    ids = [req["id"] for req in reqs]
    duplicate_ids = sorted({requirement_id for requirement_id in ids if ids.count(requirement_id) > 1})
    missing_ids = sorted(EXPECTED_REQUIREMENT_IDS - set(ids))
    unexpected_ids = sorted(set(ids) - EXPECTED_REQUIREMENT_IDS)
    invalid_text = sorted(
        req["id"] for req in reqs
        if req["id"] in REQUIREMENT_TESTS and not REQUIREMENT_TESTS[req["id"]][1].search(req["text"])
    )
    contradictory_text = sorted(
        req["id"] for req in reqs
        if (
            req["id"] in CONTRADICTION_PATTERNS
            and CONTRADICTION_PATTERNS[req["id"]].search(req["text"])
        )
    )
    ambiguities = []
    if "Approval means a non-empty manager token." not in payload["transcript"]:
        ambiguities.append("Approval token definition is missing or unsupported.")
    if duplicate_ids:
        ambiguities.append(f"Duplicate requirement IDs: {', '.join(duplicate_ids)}.")
    if missing_ids:
        ambiguities.append(f"Missing required requirement IDs: {', '.join(missing_ids)}.")
    if unexpected_ids:
        ambiguities.append(f"Unexpected requirement IDs: {', '.join(unexpected_ids)}.")
    if invalid_text:
        ambiguities.append(f"Unsupported requirement wording: {', '.join(invalid_text)}.")
    if contradictory_text:
        ambiguities.append(
            f"Contradictory requirement wording: {', '.join(contradictory_text)}."
        )
    ambiguities.extend(source_shape_errors(payload["source"].replace("\r\n", "\n").replace("\r", "\n")))
    ambiguities.extend(generated_validation_errors)
    if not patch:
        ambiguities.append("No source-changing patch could be produced.")
    baseline_checks = run_fixture_checks(patched=False)
    patched_checks = run_fixture_checks(patched=True)
    patch_safety_checks = run_patch_safety_checks(patched=True)
    if not all(patch_safety_checks):
        ambiguities.append("The proposed patch does not require a non-empty order ID.")
    items = [
        {
            **req,
            "test": tests[req["id"]],
            "baseline": "FAIL" if not baseline_checks[int(req["id"].split("-")[1]) - 1] else "PASS",
            "after_patch": "PASS" if patched_checks[int(req["id"].split("-")[1]) - 1] else "FAIL",
        }
        for req in reqs
        if req["id"] in tests
    ]
    complete_mapping = (
        len(items) == len(EXPECTED_REQUIREMENT_IDS)
        and len({item["id"] for item in items}) == len(EXPECTED_REQUIREMENT_IDS)
        and {item["id"] for item in items} == EXPECTED_REQUIREMENT_IDS
    )
    return {
        "status": "READY_FOR_HUMAN_APPLY" if not ambiguities and patch and complete_mapping else "NEEDS_CLARIFICATION",
        "headline": f"{len(items)} cited requirements mapped to deterministic scenario checks",
        "metrics": {
            "requirements": len(items),
            "baseline_failures": baseline_checks.count(False),
            "post_patch_passes": patched_checks.count(True),
        },
        "items": items,
        "evidence": [{"label": req["id"], "value": f"{req['timestamp']} · {req['speaker']}"} for req in reqs],
        "artifact": {
            "ambiguities": list(dict.fromkeys(ambiguities)),
            "patch": patch,
            "generated_source": generated_source,
            "generated_source_ast_validated": bool(generated_source) and not generated_validation_errors,
            "approval_required": True,
            "verification_kind": "deterministic scenario checks; patch not executed",
            "complete_mapping": complete_mapping,
            "patch_safety_checks": {
                "rejects_empty_order_id": patch_safety_checks[0],
                "empty_order_id_prevents_charge": patch_safety_checks[1],
            },
        },
    }


def acceptance(result: dict[str, Any]) -> tuple[bool, dict[str, bool]]:
    checks = {
        "four_requirements": result["metrics"]["requirements"] == 4,
        "baseline_reproduced": result["metrics"]["baseline_failures"] == 4,
        "four_tests_pass": result["metrics"]["post_patch_passes"] == 4,
        "idempotency_patch": "idempotency_key" in result["artifact"]["patch"],
        "non_empty_order_id_guard": all(result["artifact"]["patch_safety_checks"].values()),
        "generated_source_ast_validated": result["artifact"]["generated_source_ast_validated"],
        "complete_unique_mapping": result["artifact"]["complete_mapping"],
        "source_changed": bool(result["artifact"]["patch"]),
        "no_ambiguities": not result["artifact"]["ambiguities"],
        "human_apply": result["artifact"]["approval_required"],
    }
    return all(checks.values()), checks
