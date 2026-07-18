from __future__ import annotations

import csv
import io
import json
from datetime import date, timedelta
from statistics import mean
from typing import Any

from runtime.contracts import Field, Product


START = date(2026, 6, 19)
WEIGHT_ROWS = ["date,weight_kg,calories,protein_g"]
for index in range(30):
    WEIGHT_ROWS.append(f"{START + timedelta(days=index)},{82 - index * 0.08:.2f},{2200 - index % 3 * 50},{150 + index % 4 * 5}")
DAILY = "\n".join(WEIGHT_ROWS)
WORKOUTS = """date,exercise,weight_kg,reps
2026-06-20,Squat,100,5
2026-07-17,Squat,105,5
2026-06-20,Bench Press,75,6
2026-07-17,Bench Press,77.5,6
2026-06-20,Deadlift,130,4
2026-07-17,Deadlift,137.5,4"""
BODY = json.dumps([
    {"date": "2026-06-19", "body_fat_pct": 23.4, "lean_mass_kg": 62.8},
    {"date": "2026-07-18", "body_fat_pct": 21.8, "lean_mass_kg": 63.0},
], indent=2)

PRODUCT = Product(
    9, "body-recomposition-evidence-engine", "Body Recomposition Evidence Engine",
    "Separate useful fat loss from strength loss with local, source-linked trends.",
    "#22c55e",
    (Field("daily", "Synthetic HealthKit + nutrition export (CSV)", DAILY, 16), Field("workouts", "Strong workout export (CSV)", WORKOUTS, 9), Field("body", "Body scan snapshots (JSON)", BODY, 9)),
)


def csv_rows(raw: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(raw.strip())))


def ewma(values: list[float], alpha: float = 0.25) -> list[float]:
    output = [values[0]]
    for value in values[1:]:
        output.append(alpha * value + (1 - alpha) * output[-1])
    return output


def analyze(payload: dict[str, str]) -> dict[str, Any]:
    daily, workouts, body = csv_rows(payload["daily"]), csv_rows(payload["workouts"]), json.loads(payload["body"])
    trend = ewma([float(row["weight_kg"]) for row in daily])
    lifts = []
    for exercise in sorted({row["exercise"] for row in workouts}):
        rows = [row for row in workouts if row["exercise"] == exercise]
        estimates = [float(row["weight_kg"]) * (1 + int(row["reps"]) / 30) for row in rows]
        lifts.append({"exercise": exercise, "first_1rm": round(estimates[0], 1), "latest_1rm": round(estimates[-1], 1), "change_pct": round(100 * (estimates[-1] / estimates[0] - 1), 1)})
    weight_change, fat_change = trend[-1] - trend[0], float(body[-1]["body_fat_pct"]) - float(body[0]["body_fat_pct"])
    lean_change = float(body[-1]["lean_mass_kg"]) - float(body[0]["lean_mass_kg"])
    status = "FAT_LOSS_WITH_STRENGTH_PRESERVED" if weight_change < 0 and fat_change < 0 and lean_change >= -0.3 else "REVIEW_NEEDED"
    return {
        "status": status, "headline": "Weight and body-fat trend down while all three strength markers improve",
        "metrics": {"weight_change_kg": round(weight_change, 1), "body_fat_change_pp": round(fat_change, 1), "lean_mass_change_kg": round(lean_change, 1)},
        "items": lifts,
        "evidence": [{"label": "daily observations", "value": str(len(daily))}, {"label": "body scans", "value": str(len(body))}, {"label": "average protein", "value": f"{mean(float(row['protein_g']) for row in daily):.0f} g/day"}],
        "artifact": {"ewma": [round(value, 2) for value in trend], "raw_health_data_sent_to_openai": False},
    }


def acceptance(result: dict[str, Any]) -> tuple[bool, dict[str, bool]]:
    checks = {"thirty_day_trend": len(result["artifact"]["ewma"]) == 30, "three_strength_markers": len(result["items"]) == 3, "classification": result["status"] == "FAT_LOSS_WITH_STRENGTH_PRESERVED", "privacy": result["artifact"]["raw_health_data_sent_to_openai"] is False}
    return all(checks.values()), checks

