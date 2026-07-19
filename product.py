from __future__ import annotations

import csv
import io
import json
import math
import re
from datetime import date, timedelta
from statistics import mean
from typing import Any

from runtime.contracts import Field, Product


START = date(2026, 6, 19)
WEIGHTS = [
    82.0, 81.8, 82.1, 81.9, 81.7, 81.8, 81.6, 81.7, 81.5, 81.6,
    81.4, 81.5, 81.3, 81.4, 81.2, 81.3, 81.1, 81.2, 81.0, 81.1,
    80.9, 81.0, 80.9, 81.0, 80.8, 80.9, 80.8, 80.9, 80.8, 80.9,
]
WEIGHT_ROWS = ["date,weight_kg,calories,protein_g"]
for index, weight in enumerate(WEIGHTS):
    WEIGHT_ROWS.append(f"{START + timedelta(days=index)},{weight:.2f},{2200 - index % 3 * 50},{150 + index % 4 * 5}")
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


def by_date(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: date.fromisoformat(str(row["date"])))


REQUIRED_EXERCISES = ("Bench Press", "Deadlift", "Squat")


def validate_inputs(
    daily: list[dict[str, Any]],
    workouts: list[dict[str, Any]],
    body: Any,
) -> list[str]:
    errors = []
    if not isinstance(body, list):
        return ["Body scans must be a JSON array."]
    try:
        daily_dates = [date.fromisoformat(str(row["date"])) for row in daily]
        workout_dates = [date.fromisoformat(str(row["date"])) for row in workouts]
        body_dates = [date.fromisoformat(str(row["date"])) for row in body]
    except (KeyError, TypeError, ValueError) as error:
        return [f"Invalid or missing date: {error}"]
    if len(daily) != 30:
        errors.append(f"Exactly 30 daily observations are required; got {len(daily)}.")
    if len(set(daily_dates)) != len(daily_dates):
        errors.append("Daily observation dates must be distinct.")
    ordered_daily_dates = sorted(set(daily_dates))
    if len(ordered_daily_dates) >= 2 and any(
        later - earlier != timedelta(days=1)
        for earlier, later in zip(ordered_daily_dates, ordered_daily_dates[1:], strict=False)
    ):
        errors.append("Daily observations must cover consecutive calendar dates.")
    try:
        daily_values = [
            float(row[key])
            for row in daily
            for key in ("weight_kg", "calories", "protein_g")
        ]
        workout_values = [
            float(row[key])
            for row in workouts
            for key in ("weight_kg", "reps")
        ]
        body_values = [
            float(row[key])
            for row in body
            for key in ("body_fat_pct", "lean_mass_kg")
        ]
    except (KeyError, TypeError, ValueError) as error:
        errors.append(f"Missing or non-numeric measurement: {error}")
    else:
        if not all(math.isfinite(value) for value in daily_values + workout_values + body_values):
            errors.append("All measurements must be finite.")
        daily_weights = [float(row["weight_kg"]) for row in daily]
        workout_weights = [float(row["weight_kg"]) for row in workouts]
        if not all(weight > 0 for weight in daily_weights + workout_weights):
            errors.append("All weight measurements must be greater than zero.")
        invalid_reps = [
            row.get("reps")
            for row in workouts
            if (
                not isinstance(row.get("reps"), str)
                or re.fullmatch(r"\+?[0-9]+", row["reps"].strip()) is None
                or not row["reps"].strip().lstrip("+").strip("0")
            )
        ]
        if invalid_reps:
            errors.append("Workout reps must be positive integers.")
    workout_keys = [(row.get("date"), row.get("exercise")) for row in workouts]
    if len(set(workout_keys)) != len(workout_keys):
        errors.append("Workout date/exercise observations must be unique.")
    for exercise in REQUIRED_EXERCISES:
        rows = [row for row in workouts if row.get("exercise") == exercise]
        if len(rows) < 2 or len({row.get("date") for row in rows}) < 2:
            errors.append(f"{exercise}: at least two distinct dated observations are required.")
    if len(body) < 2:
        errors.append(f"At least two body scans are required; got {len(body)}.")
    if len(set(body_dates)) != len(body_dates):
        errors.append("Body scan dates must be distinct.")
    return list(dict.fromkeys(errors))


def invalid_evidence_result(
    errors: list[str],
    daily: list[dict[str, Any]],
    workouts: list[dict[str, Any]],
    body: list[dict[str, Any]],
) -> dict[str, Any]:
    lifts = []
    for exercise in REQUIRED_EXERCISES:
        rows = [row for row in workouts if row.get("exercise") == exercise]
        lifts.append({
            "exercise": exercise,
            "first_1rm": None,
            "latest_1rm": None,
            "change_pct": None,
            "state": "INSUFFICIENT" if len(rows) < 2 else "UNVERIFIED",
        })
    return {
        "status": "REVIEW_NEEDED",
        "headline": f"Review needed: {errors[0]}",
        "metrics": {
            "weight_change_kg": None,
            "body_fat_change_pp": None,
            "lean_mass_change_kg": None,
        },
        "items": lifts,
        "evidence": [
            {"label": "daily observations", "value": str(len(daily))},
            {"label": "body scans", "value": str(len(body))},
        ],
        "artifact": {
            "ewma": [],
            "strength_preserved": False,
            "warnings": errors,
            "input_valid": False,
            "raw_health_data_sent_to_openai": False,
        },
    }


def analyze(payload: dict[str, str]) -> dict[str, Any]:
    daily = csv_rows(payload["daily"])
    workouts = csv_rows(payload["workouts"])
    try:
        body = json.loads(payload["body"])
    except json.JSONDecodeError as error:
        return invalid_evidence_result([f"Invalid body scan JSON: {error.msg}"], daily, workouts, [])
    errors = validate_inputs(daily, workouts, body)
    if errors:
        return invalid_evidence_result(
            errors,
            daily,
            workouts,
            body if isinstance(body, list) else [],
        )
    daily = by_date(daily)
    workouts = by_date(workouts)
    body = by_date(body)
    trend = ewma([float(row["weight_kg"]) for row in daily])
    lifts = []
    warnings = []
    for exercise in REQUIRED_EXERCISES:
        rows = [row for row in workouts if row["exercise"] == exercise]
        if len(rows) < 2:
            lifts.append({"exercise": exercise, "first_1rm": None, "latest_1rm": None, "change_pct": None, "state": "INSUFFICIENT"})
            warnings.append(f"{exercise}: at least two dated observations are required")
            continue
        estimates = [float(row["weight_kg"]) * (1 + int(row["reps"]) / 30) for row in rows]
        change_pct = round(100 * (estimates[-1] / estimates[0] - 1), 1)
        state = "PRESERVED" if change_pct >= 0 else "DECLINING"
        lifts.append({"exercise": exercise, "first_1rm": round(estimates[0], 1), "latest_1rm": round(estimates[-1], 1), "change_pct": change_pct, "state": state})
        if state == "DECLINING":
            warnings.append(f"{exercise}: estimated 1RM declined {abs(change_pct):g}%")
    weight_change, fat_change = trend[-1] - trend[0], float(body[-1]["body_fat_pct"]) - float(body[0]["body_fat_pct"])
    lean_change = float(body[-1]["lean_mass_kg"]) - float(body[0]["lean_mass_kg"])
    strength_preserved = all(item["state"] == "PRESERVED" for item in lifts)
    status = "FAT_LOSS_WITH_STRENGTH_PRESERVED" if weight_change < 0 and fat_change < 0 and lean_change >= -0.3 and strength_preserved else "REVIEW_NEEDED"
    headline = (
        "Body fat trends down while all required strength markers are preserved"
        if status == "FAT_LOSS_WITH_STRENGTH_PRESERVED"
        else f"Review needed: {'; '.join(warnings) if warnings else 'body-composition evidence does not meet the preservation rule'}"
    )
    return {
        "status": status, "headline": headline,
        "metrics": {"weight_change_kg": round(weight_change, 1), "body_fat_change_pp": round(fat_change, 1), "lean_mass_change_kg": round(lean_change, 1)},
        "items": lifts,
        "evidence": [{"label": "daily observations", "value": str(len(daily))}, {"label": "body scans", "value": str(len(body))}, {"label": "average protein", "value": f"{mean(float(row['protein_g']) for row in daily):.0f} g/day"}],
        "artifact": {"ewma": [round(value, 2) for value in trend], "strength_preserved": strength_preserved, "warnings": warnings, "input_valid": True, "raw_health_data_sent_to_openai": False},
    }


def acceptance(result: dict[str, Any]) -> tuple[bool, dict[str, bool]]:
    checks = {
        "thirty_day_trend": len(result["artifact"]["ewma"]) == 30,
        "three_strength_markers": len(result["items"]) == 3 and all(item["state"] == "PRESERVED" for item in result["items"]),
        "classification": result["status"] == "FAT_LOSS_WITH_STRENGTH_PRESERVED",
        "input_valid": result["artifact"]["input_valid"],
        "privacy": result["artifact"]["raw_health_data_sent_to_openai"] is False,
    }
    return all(checks.values()), checks
