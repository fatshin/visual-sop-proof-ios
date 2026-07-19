from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from runtime.contracts import Field, Product


THESES = json.dumps([
    {"id": "T-1", "thesis": "Overseas revenue ratio keeps rising", "metric": "overseas_ratio", "rule": "two_consecutive_declines"},
    {"id": "T-2", "thesis": "Operating margin stays above 12%", "metric": "operating_margin", "rule": "below:12"},
    {"id": "T-3", "thesis": "Free cash flow remains positive", "metric": "free_cash_flow", "rule": "below:0"},
], indent=2)
QUARTERS = json.dumps([
    {"quarter": "2025-Q3", "overseas_ratio": 42, "operating_margin": 14.1, "free_cash_flow": 820, "source": "fixtures/FY2025-Q3-results.md#page-12"},
    {"quarter": "2025-Q4", "overseas_ratio": 40, "operating_margin": 13.8, "free_cash_flow": 610, "source": "fixtures/FY2025-Q4-results.md#page-9"},
    {"quarter": "2026-Q1", "overseas_ratio": 37, "operating_margin": 13.2, "free_cash_flow": 440, "source": "fixtures/FY2026-Q1-results.md#page-11"},
], indent=2)

PRODUCT = Product(
    10, "thesis-breaker-japan", "Thesis Breaker Japan",
    "Watch for the evidence that breaks an investment thesis—not the evidence that flatters it.",
    "#ef4444",
    (Field("theses", "Investment theses (JSON)", THESES, 13), Field("quarters", "Normalized quarterly evidence (JSON)", QUARTERS, 15)),
)


QUARTER_PATTERN = re.compile(r"^(\d{4})-Q([1-4])$")
SOURCE_PATTERN = re.compile(r"^([^#]+)#page-(\d+)$")


def normalize_quarters(quarters: list[dict[str, Any]], metrics: set[str]) -> list[dict[str, Any]]:
    normalized = []
    seen = set()
    for row in quarters:
        match = QUARTER_PATTERN.fullmatch(str(row.get("quarter", "")))
        if not match:
            raise ValueError(f"Invalid quarter {row.get('quarter')!r}; expected YYYY-Q1 through YYYY-Q4")
        key = (int(match.group(1)), int(match.group(2)))
        if key in seen:
            raise ValueError(f"Duplicate quarter: {row['quarter']}")
        seen.add(key)
        missing = metrics.difference(row)
        if missing:
            raise ValueError(f"{row['quarter']} is missing metrics: {', '.join(sorted(missing))}")
        if not source_reference_valid(str(row.get("source", ""))):
            raise ValueError(f"Invalid source reference for {row['quarter']}: {row.get('source')!r}")
        normalized.append((key, row))
    return [row for _, row in sorted(normalized, key=lambda item: item[0])]


def source_reference_valid(reference: str) -> bool:
    match = SOURCE_PATTERN.fullmatch(reference)
    if not match:
        return False
    root = Path(__file__).resolve().parent
    source = (root / match.group(1)).resolve()
    if not source.is_relative_to(root) or not source.is_file():
        return False
    return f"## Page {match.group(2)}" in source.read_text()


def assess(thesis: dict[str, str], quarters: list[dict[str, Any]]) -> dict[str, Any]:
    values = [float(row[thesis["metric"]]) for row in quarters]
    if thesis["rule"] == "two_consecutive_declines":
        broken, trace = len(values) >= 3 and values[-3] > values[-2] > values[-1], f"{values[-3]:g} → {values[-2]:g} → {values[-1]:g}"
        sources = [row["source"] for row in quarters[-3:]]
        break_condition = f"{thesis['metric']} declines in two consecutive quarter-to-quarter comparisons"
        reversal_condition = f"{thesis['metric']} must rise in two consecutive quarter-to-quarter comparisons; one rebound is insufficient"
    else:
        threshold = float(thesis["rule"].split(":", 1)[1])
        broken, trace = values[-1] < threshold, f"latest {values[-1]:g}; floor {threshold:g}"
        sources = [quarters[-1]["source"]]
        break_condition = f"latest {thesis['metric']} falls below {threshold:g}"
        reversal_condition = f"latest {thesis['metric']} returns to at least {threshold:g}"
    return {
        "id": thesis["id"],
        "thesis": thesis["thesis"],
        "status": "BROKEN" if broken else "INTACT",
        "trace": trace,
        "break_condition": break_condition,
        "reversal_condition": reversal_condition,
        "source": sources[-1],
        "sources": sources,
    }


def analyze(payload: dict[str, str]) -> dict[str, Any]:
    theses = json.loads(payload["theses"])
    quarters = normalize_quarters(json.loads(payload["quarters"]), {thesis["metric"] for thesis in theses})
    items = [assess(thesis, quarters) for thesis in theses]
    items = sorted(items, key=lambda item: item["status"] != "BROKEN")
    broken = sum(item["status"] == "BROKEN" for item in items)
    return {
        "status": "REVIEW_PORTFOLIO" if broken else "THESES_INTACT",
        "headline": f"{broken} investment thesis broken by disconfirming evidence",
        "metrics": {"theses": len(items), "broken": broken, "quarters": len(quarters)},
        "items": items,
        "evidence": [{"label": row["quarter"], "value": row["source"]} for row in quarters],
        "artifact": {"priority": "disconfirming evidence first", "assessments": items, "source_references_validated": True, "not_financial_advice": True},
    }


def acceptance(result: dict[str, Any]) -> tuple[bool, dict[str, bool]]:
    broken = [item for item in result["items"] if item["status"] == "BROKEN"]
    checks = {
        "three_theses": result["metrics"]["theses"] == 3,
        "one_broken": len(broken) == 1 and broken[0]["id"] == "T-1",
        "broken_first": result["items"][0]["status"] == "BROKEN",
        "source_links": all(item["sources"] for item in result["items"]) and result["artifact"]["source_references_validated"],
        "reversal_conditions": all(item["reversal_condition"] for item in result["items"]),
        "disclaimer": result["artifact"]["not_financial_advice"],
    }
    return all(checks.values()), checks
