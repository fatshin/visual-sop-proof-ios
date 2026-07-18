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
        self.assertIn("index < 30", site)
        self.assertIn("82 - index * 0.08", site)
        for line in product.WORKOUTS.splitlines():
            self.assertIn(line, site)
        for scan in json.loads(product.BODY):
            self.assertIn(f'"date":"{scan["date"]}"', site)
        self.assertIn(result["status"], site)
        self.assertIn("Bench Press +3.3%", site)
        self.assertIn("Deadlift +5.8%", site)
        self.assertIn("Squat +5.0%", site)

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


if __name__ == "__main__":
    unittest.main()
