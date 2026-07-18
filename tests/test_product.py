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
        for event in json.loads(product.TRACE):
            self.assertIn(f'"seq":{event["seq"]}', site)
        self.assertIn(result["status"], site)
        self.assertIn('value: "5", label: "trace events"', site)
        self.assertIn('value: "3", label: "root causes"', site)
        for title in ("Customer context drift", "Duplicate refund side effect", "$750 limit bypass"):
            self.assertIn(title, site)

    def test_diagnosis_changes_when_duplicate_is_removed(self):
        events = json.loads(product.TRACE)[:-1]
        result = product.analyze({"trace": json.dumps(events)})
        ids = {item["id"] for item in result["items"]}
        self.assertNotIn("DUPLICATE_SIDE_EFFECT", ids)
        self.assertEqual(result["metrics"]["findings"], 2)


if __name__ == "__main__":
    unittest.main()
