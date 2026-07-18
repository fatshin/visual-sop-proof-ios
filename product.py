from __future__ import annotations

import json
import re
from typing import Any

from runtime.contracts import Field, Product


SOURCE = json.dumps({"deadline": "2026-08-31", "amount_yen": 50000, "minimum_age": 18, "residency_date": "2026-04-01", "faq_contact": "benefits@example.go.jp"}, indent=2)
NOTICE = """Emergency Support Benefit
Apply by 2026-09-30 at 23:59.
Every resident aged 16 or older receives ¥70,000 automatically.
You must have lived in the city by 2026-05-01.
Questions: support@example.go.jp
Applications submitted after the deadline may still be accepted."""

PRODUCT = Product(
    3, "public-notice-stress-test", "Public Notice Stress Test",
    "Find factual conflicts and unsupported promises before a public notice ships.",
    "#0ea5e9",
    (Field("notice", "Draft public notice", NOTICE, 10), Field("source", "Authoritative facts (JSON)", SOURCE, 10)),
)


def inspect_notice(notice: str, source: dict[str, Any]) -> list[dict[str, str]]:
    checks = [
        ("DEADLINE", source["deadline"], r"20\d{2}-\d{2}-\d{2}", "deadline date"),
        ("AMOUNT", str(source["amount_yen"]), r"¥([\d,]+)", "benefit amount"),
        ("AGE", str(source["minimum_age"]), r"aged\s+(\d+)", "minimum age"),
        ("RESIDENCY", source["residency_date"], r"lived in the city by\s+(20\d{2}-\d{2}-\d{2})", "residency cutoff"),
        ("CONTACT", source["faq_contact"], r"[\w.+-]+@[\w.-]+", "contact address"),
    ]
    findings = []
    for code, expected, pattern, label in checks:
        match = re.search(pattern, notice, re.IGNORECASE)
        actual = match.group(1 if match and match.lastindex else 0).replace(",", "") if match else "MISSING"
        if actual != expected:
            findings.append({"id": code, "severity": "HIGH", "claim": label, "actual": actual, "expected": expected, "repair": f"Replace {label} with {expected}."})
    if "after the deadline may still be accepted" in notice.lower():
        findings.append({"id": "UNSUPPORTED_EXCEPTION", "severity": "MEDIUM", "claim": "late applications accepted", "actual": "present", "expected": "no supporting source", "repair": "Remove the unsupported exception."})
    return findings


def analyze(payload: dict[str, str]) -> dict[str, Any]:
    source = json.loads(payload["source"])
    findings = inspect_notice(payload["notice"], source)
    return {
        "status": "BLOCKED_FOR_RELEASE" if findings else "READY",
        "headline": f"{len(findings)} publication risks found before release",
        "metrics": {"risks": len(findings), "source_claims": len(source), "linked_repairs": len(findings)},
        "items": findings,
        "evidence": [{"label": key, "value": str(value)} for key, value in source.items()],
        "artifact": {"corrected_claims": [item["repair"] for item in findings]},
    }


def acceptance(result: dict[str, Any]) -> tuple[bool, dict[str, bool]]:
    checks = {"five_fixed_conflicts": sum(item["id"] != "UNSUPPORTED_EXCEPTION" for item in result["items"]) == 5, "unsupported_claim": any(item["id"] == "UNSUPPORTED_EXCEPTION" for item in result["items"]), "repairs_linked": all(item["repair"] for item in result["items"])}
    return all(checks.values()), checks

