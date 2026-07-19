from __future__ import annotations

import csv
import io
import itertools
import math
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


class InvalidBenchmarkError(ValueError):
    pass


class NoFeasibleRouteError(ValueError):
    pass


def parse_rows(raw: str) -> list[dict[str, Any]]:
    reader = csv.DictReader(io.StringIO(raw.strip()))
    required_columns = {"case_id", "task", "model", "quality", "cost"}
    if reader.fieldnames is None or set(reader.fieldnames) != required_columns:
        raise InvalidBenchmarkError("CSV columns must be case_id, task, model, quality, cost")
    rows = []
    for line_number, row in enumerate(reader, start=2):
        if not all(row.get(column, "").strip() for column in required_columns):
            raise InvalidBenchmarkError(f"Missing value on CSV line {line_number}")
        try:
            quality, cost = float(row["quality"]), float(row["cost"])
        except ValueError as error:
            raise InvalidBenchmarkError(f"Non-numeric quality or cost on CSV line {line_number}") from error
        if (
            not math.isfinite(quality)
            or not 0 <= quality <= 100
            or not math.isfinite(cost)
            or cost < 0
        ):
            raise InvalidBenchmarkError(f"Invalid quality or cost on CSV line {line_number}")
        rows.append({**row, "quality": quality, "cost": cost})
    if not rows:
        raise InvalidBenchmarkError("Benchmark must contain at least one row")
    return rows


def validate_matrix(rows: list[dict[str, Any]]) -> None:
    expected_tasks = set(next(iter(MODEL_DATA.values())))
    expected_models = set(MODEL_DATA)
    observed_tasks = {row["task"] for row in rows}
    observed_models = {row["model"] for row in rows}
    if observed_tasks != expected_tasks:
        raise InvalidBenchmarkError(
            f"Task set must be {sorted(expected_tasks)}; got {sorted(observed_tasks)}"
        )
    if observed_models != expected_models:
        raise InvalidBenchmarkError(
            f"Model set must be {sorted(expected_models)}; got {sorted(observed_models)}"
        )
    case_ids = {row["case_id"] for row in rows}
    if len(case_ids) != 20:
        raise InvalidBenchmarkError(
            f"Benchmark must contain exactly 20 case IDs; got {len(case_ids)}"
        )
    tasks_by_case: dict[str, set[str]] = {}
    for row in rows:
        tasks_by_case.setdefault(row["case_id"], set()).add(row["task"])
    multi_task_cases = sorted(
        case_id for case_id, tasks in tasks_by_case.items() if len(tasks) != 1
    )
    if multi_task_cases:
        raise InvalidBenchmarkError(
            "Each case ID must map to exactly one task: "
            + ", ".join(multi_task_cases)
        )
    observed_cells = {(row["task"], row["model"]) for row in rows}
    missing_cells = sorted(
        (task, model)
        for task in expected_tasks
        for model in expected_models
        if (task, model) not in observed_cells
    )
    if missing_cells:
        formatted = ", ".join(f"{task}/{model}" for task, model in missing_cells)
        raise InvalidBenchmarkError(f"Incomplete task-model matrix: {formatted}")
    row_keys = [
        (row["case_id"], row["task"], row["model"])
        for row in rows
    ]
    duplicate_keys = sorted({
        key for key in row_keys if row_keys.count(key) > 1
    })
    if duplicate_keys:
        formatted = ", ".join("/".join(key) for key in duplicate_keys)
        raise InvalidBenchmarkError(f"Duplicate case-task-model rows: {formatted}")
    groups: dict[tuple[str, str], set[str]] = {}
    for row in rows:
        groups.setdefault((row["case_id"], row["task"]), set()).add(row["model"])
    incomplete_groups = sorted(
        (case_id, task, sorted(expected_models - models))
        for (case_id, task), models in groups.items()
        if models != expected_models
    )
    if incomplete_groups:
        formatted = ", ".join(
            f"{case_id}/{task} missing {','.join(models)}"
            for case_id, task, models in incomplete_groups
        )
        raise InvalidBenchmarkError(
            f"Incomplete model coverage per case/task: {formatted}"
        )


def optimize(rows: list[dict[str, Any]], floor: float) -> dict[str, Any]:
    validate_matrix(rows)
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
    baseline_values = [averages[(task, "gpt-5.6")] for task in tasks]
    baseline = {
        "route": {task: "gpt-5.6" for task in tasks},
        "quality": round(sum(item[0] for item in baseline_values) / len(tasks), 2),
        "cost": round(sum(item[1] for item in baseline_values), 2),
    }
    if baseline["cost"] <= 0:
        raise InvalidBenchmarkError("GPT-5.6 baseline bundle cost must be greater than zero")
    candidates = []
    for choice in itertools.product(models, repeat=len(tasks)):
        route = dict(zip(tasks, choice, strict=True))
        selected = [averages[(task, route[task])] for task in tasks]
        candidates.append({"route": route, "quality": round(sum(item[0] for item in selected) / len(tasks), 2), "cost": round(sum(item[1] for item in selected), 2)})
    feasible = [item for item in candidates if item["quality"] >= floor]
    if not feasible:
        raise NoFeasibleRouteError("No route meets the quality floor")
    best = min(feasible, key=lambda item: (item["cost"], -item["quality"]))
    return {"best": best, "baseline": baseline, "frontier": sorted(feasible, key=lambda item: (item["cost"], -item["quality"]))[:5], "cases": len({row["case_id"] for row in rows})}


def analyze(payload: dict[str, str]) -> dict[str, Any]:
    try:
        rows = parse_rows(payload["results"])
        floor = float(payload["quality_floor"])
        if not math.isfinite(floor) or not 0 <= floor <= 100:
            raise ValueError("Quality floor must be finite and between 0 and 100")
        result = optimize(rows, floor)
    except InvalidBenchmarkError as error:
        return {
            "status": "INVALID_BENCHMARK",
            "headline": str(error),
            "metrics": {
                "macro_average_quality": None,
                "normalized_three_task_bundle_cost": None,
                "fixture_cost_reduction": None,
                "cases": 0,
            },
            "items": [],
            "evidence": [],
            "artifact": {"error": str(error)},
        }
    except ValueError as error:
        if not isinstance(error, NoFeasibleRouteError):
            return {
                "status": "INVALID_BENCHMARK",
                "headline": f"Invalid quality floor: {payload['quality_floor']}",
                "metrics": {
                    "macro_average_quality": None,
                    "normalized_three_task_bundle_cost": None,
                    "fixture_cost_reduction": None,
                    "cases": 0,
                },
                "items": [],
                "evidence": [],
                "artifact": {"error": str(error)},
            }
        return {
            "status": "NO_FEASIBLE_ROUTE",
            "headline": str(error),
            "metrics": {
                "macro_average_quality": None,
                "normalized_three_task_bundle_cost": None,
                "fixture_cost_reduction": None,
                "cases": len({row["case_id"] for row in rows}),
            },
            "items": [],
            "evidence": [],
            "artifact": {"error": str(error), "quality_floor": payload["quality_floor"]},
        }
    saved = round(100 * (1 - result["best"]["cost"] / result["baseline"]["cost"]), 1)
    return {
        "status": "ROUTE_FOUND",
        "headline": f"{saved}% fixture cost reduction for a normalized three-task bundle",
        "metrics": {
            "macro_average_quality": result["best"]["quality"],
            "normalized_three_task_bundle_cost": result["best"]["cost"],
            "fixture_cost_reduction": saved,
            "cases": result["cases"],
        },
        "items": result["frontier"], "evidence": [{"label": task, "value": model} for task, model in result["best"]["route"].items()],
        "artifact": result,
    }


def acceptance(result: dict[str, Any]) -> tuple[bool, dict[str, bool]]:
    checks = {
        "route_found": result["status"] == "ROUTE_FOUND",
        "twenty_cases": result["metrics"]["cases"] == 20,
        "quality_floor": result["metrics"]["macro_average_quality"] >= 91,
        "cheaper_than_baseline": (
            result["metrics"]["normalized_three_task_bundle_cost"]
            < result["artifact"]["baseline"]["cost"]
        ),
        "fixture_reduction_reported": result["metrics"]["fixture_cost_reduction"] == 61.0,
    }
    return all(checks.values()), checks
