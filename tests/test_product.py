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
        for line in product.NOTICE.splitlines():
            self.assertIn(line, site)
        for key, value in json.loads(product.SOURCE).items():
            self.assertIn(f'"{key}"', site)
            self.assertIn(str(value).lower(), site.lower())
        self.assertIn(result["status"], site)
        self.assertIn('value: "5", label: "direct conflicts"', site)
        self.assertIn('value: "1", label: "unsupported claim"', site)
        self.assertIn("Six linked repairs prepared", site)

    def test_corrected_notice_clears_the_release_gate(self):
        source = json.loads(product.SOURCE)
        corrected = """Emergency Support Benefit
Apply by 2026-08-31 at 23:59.
Every resident aged 18 or older receives ¥50,000 automatically.
You must have lived in the city by 2026-04-01.
Questions: benefits@example.go.jp"""
        result = product.analyze({"notice": corrected, "source": json.dumps(source)})
        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["items"], [])


if __name__ == "__main__":
    unittest.main()
