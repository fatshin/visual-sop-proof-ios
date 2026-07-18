from __future__ import annotations

import json
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


def assess(thesis: dict[str, str], quarters: list[dict[str, Any]]) -> dict[str, Any]:
    values = [float(row[thesis["metric"]]) for row in quarters]
    if thesis["rule"] == "two_consecutive_declines":
        broken, trace = len(values) >= 3 and values[-3] > values[-2] > values[-1], f"{values[-3]:g} → {values[-2]:g} → {values[-1]:g}"
    else:
        threshold = float(thesis["rule"].split(":", 1)[1])
        broken, trace = values[-1] < threshold, f"latest {values[-1]:g}; floor {threshold:g}"
    return {"id": thesis["id"], "thesis": thesis["thesis"], "status": "BROKEN" if broken else "INTACT", "trace": trace, "source": quarters[-1]["source"]}


def analyze(payload: dict[str, str]) -> dict[str, Any]:
    theses, quarters = json.loads(payload["theses"]), json.loads(payload["quarters"])
    items = [assess(thesis, quarters) for thesis in theses]
    broken = sum(item["status"] == "BROKEN" for item in items)
    return {
        "status": "REVIEW_PORTFOLIO" if broken else "THESES_INTACT",
        "headline": f"{broken} investment thesis broken by disconfirming evidence",
        "metrics": {"theses": len(items), "broken": broken, "quarters": len(quarters)},
        "items": items,
        "evidence": [{"label": row["quarter"], "value": row["source"]} for row in quarters],
        "artifact": {"priority": "disconfirming evidence first", "assessments": items, "not_financial_advice": True},
    }


def acceptance(result: dict[str, Any]) -> tuple[bool, dict[str, bool]]:
    broken = [item for item in result["items"] if item["status"] == "BROKEN"]
    checks = {"three_theses": result["metrics"]["theses"] == 3, "one_broken": len(broken) == 1 and broken[0]["id"] == "T-1", "source_links": all(item["source"] for item in result["items"]), "disclaimer": result["artifact"]["not_financial_advice"]}
    return all(checks.values()), checks
