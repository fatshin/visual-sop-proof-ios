import unittest
import json
from pathlib import Path

import product
from runtime.server import page, result_markup


class ProductTests(unittest.TestCase):
    def test_fixed_acceptance(self):
        result = product.analyze({field.name: field.value for field in product.PRODUCT.fields})
        passed, checks = product.acceptance(result)
        self.assertTrue(passed, checks)

    def test_page_is_product_specific_and_escapes_output(self):
        self.assertIn(product.PRODUCT.name, page())
        self.assertNotIn("<script>", result_markup({"status": "<script>", "headline": "safe", "metrics": {}, "items": [], "evidence": [], "artifact": {}}))

    def test_public_fixture_matches_engine_fixture(self):
        site = Path("site/app/product-data.ts").read_text()
        result = product.analyze({field.name: field.value for field in product.PRODUCT.fields})
        self.assertIn("weightFixture.map", site)
        self.assertIn("82, 81.8, 82.1", site)
        for line in product.WORKOUTS.splitlines():
            self.assertIn(line, site)
        for scan in json.loads(product.BODY):
            self.assertIn(f'"date":"{scan["date"]}"', site)
        self.assertIn(result["status"], site)
        self.assertIn("Bench Press +3.3%", site)
        self.assertIn("Deadlift +5.8%", site)
        self.assertIn("Squat +5.0%", site)
        self.assertIn(f'{result["metrics"]["weight_change_kg"]:+.1f}kg', site)

    def test_lean_mass_loss_changes_classification(self):
        body = json.loads(product.BODY)
        body[-1]["lean_mass_kg"] = 61.0
        result = product.analyze({"daily": product.DAILY, "workouts": product.WORKOUTS, "body": json.dumps(body)})
        self.assertEqual(result["status"], "REVIEW_NEEDED")
        passed, checks = product.acceptance(result)
        self.assertFalse(passed)
        self.assertFalse(checks["classification"])

    def test_analysis_path_has_no_outbound_openai_client(self):
        source = Path("product.py").read_text().lower()
        for token in ("import openai", "from openai", "import requests", "import urllib", "import socket"):
            self.assertNotIn(token, source)
        result = product.analyze({field.name: field.value for field in product.PRODUCT.fields})
        self.assertFalse(result["artifact"]["raw_health_data_sent_to_openai"])

    def test_declining_lift_requires_review(self):
        workouts = product.WORKOUTS.replace("2026-07-17,Squat,105,5", "2026-07-17,Squat,90,5")
        result = product.analyze({"daily": product.DAILY, "workouts": workouts, "body": product.BODY})
        squat = next(item for item in result["items"] if item["exercise"] == "Squat")
        self.assertEqual(result["status"], "REVIEW_NEEDED")
        self.assertEqual(squat["state"], "DECLINING")
        self.assertIn("Squat", result["headline"])

    def test_missing_lift_requires_review(self):
        workouts = "\n".join(line for line in product.WORKOUTS.splitlines() if ",Deadlift," not in line)
        result = product.analyze({"daily": product.DAILY, "workouts": workouts, "body": product.BODY})
        deadlift = next(item for item in result["items"] if item["exercise"] == "Deadlift")
        self.assertEqual(result["status"], "REVIEW_NEEDED")
        self.assertEqual(deadlift["state"], "INSUFFICIENT")
        self.assertIsNone(deadlift["change_pct"])
        self.assertFalse(result["artifact"]["input_valid"])

    def test_input_order_does_not_change_result(self):
        daily_lines = product.DAILY.splitlines()
        workout_lines = product.WORKOUTS.splitlines()
        shuffled_daily = "\n".join([daily_lines[0], *reversed(daily_lines[1:])])
        shuffled_workouts = "\n".join([workout_lines[0], *reversed(workout_lines[1:])])
        body = list(reversed(json.loads(product.BODY)))
        result = product.analyze({"daily": shuffled_daily, "workouts": shuffled_workouts, "body": json.dumps(body)})
        baseline = product.analyze({"daily": product.DAILY, "workouts": product.WORKOUTS, "body": product.BODY})
        self.assertEqual(result["status"], baseline["status"])
        self.assertEqual(result["items"], baseline["items"])
        self.assertEqual(result["metrics"], baseline["metrics"])

    def test_daily_dates_must_be_thirty_distinct_and_consecutive(self):
        lines = product.DAILY.splitlines()
        too_short = product.analyze({
            "daily": "\n".join(lines[:-1]),
            "workouts": product.WORKOUTS,
            "body": product.BODY,
        })
        self.assertEqual(too_short["status"], "REVIEW_NEEDED")
        self.assertIn("Exactly 30", too_short["headline"])

        duplicate = lines.copy()
        duplicate[-1] = duplicate[-2]
        result = product.analyze({
            "daily": "\n".join(duplicate),
            "workouts": product.WORKOUTS,
            "body": product.BODY,
        })
        self.assertEqual(result["status"], "REVIEW_NEEDED")
        self.assertIn("Daily observation dates must be distinct.", result["artifact"]["warnings"])

        gap = lines.copy()
        fields = gap[-1].split(",")
        fields[0] = "2026-07-20"
        gap[-1] = ",".join(fields)
        result = product.analyze({
            "daily": "\n".join(gap),
            "workouts": product.WORKOUTS,
            "body": product.BODY,
        })
        self.assertIn("Daily observations must cover consecutive calendar dates.", result["artifact"]["warnings"])

    def test_empty_or_duplicate_body_scans_require_review(self):
        empty = product.analyze({
            "daily": product.DAILY,
            "workouts": product.WORKOUTS,
            "body": "[]",
        })
        self.assertEqual(empty["status"], "REVIEW_NEEDED")
        self.assertIn("At least two body scans", empty["headline"])

        scans = json.loads(product.BODY)
        scans[1]["date"] = scans[0]["date"]
        duplicate = product.analyze({
            "daily": product.DAILY,
            "workouts": product.WORKOUTS,
            "body": json.dumps(scans),
        })
        self.assertEqual(duplicate["status"], "REVIEW_NEEDED")
        self.assertIn("Body scan dates must be distinct.", duplicate["artifact"]["warnings"])

    def test_duplicate_workout_observation_requires_review(self):
        lines = product.WORKOUTS.splitlines()
        duplicated = "\n".join([*lines, lines[1]])
        result = product.analyze({
            "daily": product.DAILY,
            "workouts": duplicated,
            "body": product.BODY,
        })
        self.assertEqual(result["status"], "REVIEW_NEEDED")
        self.assertIn("Workout date/exercise observations must be unique.", result["artifact"]["warnings"])

    def test_invalid_reps_and_weights_fail_closed_before_strength_math(self):
        cases = {
            "fractional reps": product.WORKOUTS.replace(
                "2026-06-20,Squat,100,5",
                "2026-06-20,Squat,100,5.5",
            ),
            "zero reps": product.WORKOUTS.replace(
                "2026-06-20,Squat,100,5",
                "2026-06-20,Squat,100,0",
            ),
            "zero baseline weight": product.WORKOUTS.replace(
                "2026-06-20,Squat,100,5",
                "2026-06-20,Squat,0,5",
            ),
            "non-finite weight": product.WORKOUTS.replace(
                "2026-06-20,Squat,100,5",
                "2026-06-20,Squat,nan,5",
            ),
            "overlong reps": product.WORKOUTS.replace(
                "2026-06-20,Squat,100,5",
                f"2026-06-20,Squat,100,{'9' * 5000}",
            ),
        }
        for label, workouts in cases.items():
            with self.subTest(label=label):
                result = product.analyze({
                    "daily": product.DAILY,
                    "workouts": workouts,
                    "body": product.BODY,
                })
                self.assertEqual(result["status"], "REVIEW_NEEDED")
                self.assertFalse(result["artifact"]["input_valid"])
                self.assertFalse(product.acceptance(result)[0])

        daily = product.DAILY.replace(
            "2026-06-19,82.00",
            "2026-06-19,0.00",
        )
        result = product.analyze({
            "daily": daily,
            "workouts": product.WORKOUTS,
            "body": product.BODY,
        })
        self.assertEqual(result["status"], "REVIEW_NEEDED")
        self.assertIn(
            "All weight measurements must be greater than zero.",
            result["artifact"]["warnings"],
        )


if __name__ == "__main__":
    unittest.main()
