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

CLAIM_PATTERNS = {
    "deadline": r"(?im)^\s*(?:apply|application deadline)\s*(?:by|:)\s*(20\d{2}-\d{2}-\d{2})\b",
    "amount_yen": r"(?im)^\s*(?:benefit amount\s*:|every resident[^\n]*?\breceives?)\s*¥([\d,]+)",
    "minimum_age": r"(?im)^\s*every resident\s+aged\s+(\d+)\s+or older\b",
    "residency_date": r"(?im)^\s*you must have lived in the city by\s+(20\d{2}-\d{2}-\d{2})\b",
    "faq_contact": r"(?im)^\s*(?:questions?|faq contact)\s*:\s*([\w.+-]+@[\w.-]+)\s*$",
}
UNSUPPORTED_LATE_APPLICATION = re.compile(
    r"(?im)^\s*(?:(?:applications?\s+(?:submitted\s+)?)?after\s+the\s+deadline|late\s+applications?)\s+"
    r"(?:(?:may|will|can)\s+(?:still\s+)?be|are)\s+accepted[.!]?\s*$"
)


def extract_labeled_claim(notice: str, source_key: str) -> str:
    matches = {
        value.replace(",", "").strip()
        for value in re.findall(CLAIM_PATTERNS[source_key], notice)
    }
    if not matches:
        return "MISSING"
    if len(matches) > 1:
        return "AMBIGUOUS"
    return next(iter(matches))


def inspect_notice(notice: str, source: dict[str, Any]) -> list[dict[str, str]]:
    checks = [
        ("DEADLINE", "deadline", str(source["deadline"]), "deadline date"),
        ("AMOUNT", "amount_yen", str(source["amount_yen"]), "benefit amount"),
        ("AGE", "minimum_age", str(source["minimum_age"]), "minimum age"),
        ("RESIDENCY", "residency_date", str(source["residency_date"]), "residency cutoff"),
        ("CONTACT", "faq_contact", str(source["faq_contact"]), "contact address"),
    ]
    findings = []
    for code, source_key, expected, label in checks:
        actual = extract_labeled_claim(notice, source_key)
        if actual != expected:
            findings.append({
                "id": code,
                "severity": "HIGH",
                "claim": label,
                "actual": actual,
                "expected": expected,
                "source": source_key,
                "repair": (
                    f"Use source.{source_key} ({expected}) when the communications "
                    f"owner drafts and approves the {label} wording."
                ),
            })
    if UNSUPPORTED_LATE_APPLICATION.search(notice):
        findings.append({
            "id": "UNSUPPORTED_EXCEPTION",
            "severity": "MEDIUM",
            "claim": "late applications accepted",
            "actual": "present",
            "expected": "no supporting source",
            "source": "MISSING",
            "repair": (
                "Remove this claim, or add an authoritative late-application "
                "source field before the communications owner drafts wording."
            ),
        })
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
        "artifact": {"repair_instructions": [item["repair"] for item in findings]},
    }


def acceptance(result: dict[str, Any]) -> tuple[bool, dict[str, bool]]:
    checks = {"five_fixed_conflicts": sum(item["id"] != "UNSUPPORTED_EXCEPTION" for item in result["items"]) == 5, "unsupported_claim": any(item["id"] == "UNSUPPORTED_EXCEPTION" for item in result["items"]), "repairs_linked": all(item["repair"] for item in result["items"])}
    return all(checks.values()), checks
