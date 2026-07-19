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


if __name__ == "__main__":
    unittest.main()
