from __future__ import annotations

import csv
import io
import itertools
from typing import Any

from runtime.contracts import Field, Product


MODEL_DATA = {
    "gpt-5.6": {"extract": (96, 2.1), "reason": (95, 3.2), "draft": (93, 2.4)},
    "terra": {"extract": (92, 1.0), "reason": (91, 1.5), "draft": (92, 1.1)},
    "luna": {"extract": (90, 0.4), "reason": (84, 0.7), "draft": (89, 0.5)},
}
ROWS = ["case_id,task,model,quality,cost"]
for index in range(20):
    task = ("extract", "reason", "draft")[index % 3]
    for model, values in MODEL_DATA.items():
        quality, cost = values[task]
        ROWS.append(f"C{index + 1:02},{task},{model},{quality + index % 2},{cost:.2f}")
CSV_DATA = "\n".join(ROWS)

PRODUCT = Product(
    6, "costroute-lab", "CostRoute Lab",
    "Find the lowest-cost model route that still clears a measured quality floor.",
    "#f59e0b",
    (Field("quality_floor", "Minimum average quality", "91", 2), Field("results", "Evaluation results (CSV)", CSV_DATA, 20)),
)


def parse_rows(raw: str) -> list[dict[str, Any]]:
    return [{**row, "quality": float(row["quality"]), "cost": float(row["cost"])} for row in csv.DictReader(io.StringIO(raw.strip()))]


def optimize(rows: list[dict[str, Any]], floor: float) -> dict[str, Any]:
    tasks, models = sorted({row["task"] for row in rows}), sorted({row["model"] for row in rows})
    totals: dict[tuple[str, str], list[float]] = {}
    counts: dict[tuple[str, str], int] = {}
    for row in rows:
        key = (row["task"], row["model"])
        totals.setdefault(key, [0.0, 0.0])
        counts[key] = counts.get(key, 0) + 1
        totals[key][0] += row["quality"]
        totals[key][1] += row["cost"]
    averages = {key: [value / counts[key] for value in values] for key, values in totals.items()}
    candidates = []
    for choice in itertools.product(models, repeat=len(tasks)):
        route = dict(zip(tasks, choice, strict=True))
        selected = [averages[(task, route[task])] for task in tasks]
        candidates.append({"route": route, "quality": round(sum(item[0] for item in selected) / len(tasks), 2), "cost": round(sum(item[1] for item in selected), 2)})
    feasible = [item for item in candidates if item["quality"] >= floor]
    if not feasible:
        raise ValueError("No route meets the quality floor")
    best = min(feasible, key=lambda item: (item["cost"], -item["quality"]))
    baseline_values = [averages[(task, "gpt-5.6")] for task in tasks]
    baseline = {"route": {task: "gpt-5.6" for task in tasks}, "quality": round(sum(item[0] for item in baseline_values) / len(tasks), 2), "cost": round(sum(item[1] for item in baseline_values), 2)}
    return {"best": best, "baseline": baseline, "frontier": sorted(feasible, key=lambda item: (item["cost"], -item["quality"]))[:5], "cases": len({row["case_id"] for row in rows})}


def analyze(payload: dict[str, str]) -> dict[str, Any]:
    result = optimize(parse_rows(payload["results"]), float(payload["quality_floor"]))
    saved = round(100 * (1 - result["best"]["cost"] / result["baseline"]["cost"]), 1)
    return {
        "status": "ROUTE_FOUND", "headline": f"{saved}% estimated cost reduction at the required quality floor",
        "metrics": {"quality": result["best"]["quality"], "cost": result["best"]["cost"], "cases": result["cases"]},
        "items": result["frontier"], "evidence": [{"label": task, "value": model} for task, model in result["best"]["route"].items()],
        "artifact": result,
    }


def acceptance(result: dict[str, Any]) -> tuple[bool, dict[str, bool]]:
    checks = {"twenty_cases": result["metrics"]["cases"] == 20, "quality_floor": result["metrics"]["quality"] >= 91, "cheaper_than_baseline": result["artifact"]["best"]["cost"] < result["artifact"]["baseline"]["cost"]}
    return all(checks.values()), checks

