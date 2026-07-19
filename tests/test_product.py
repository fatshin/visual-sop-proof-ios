import unittest
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

    def test_public_fixture_matches_engine_fixture_without_escalation_claim(self):
        site = Path("site/app/product-data.ts").read_text()
        result = product.analyze({field.name: field.value for field in product.PRODUCT.fields})
        self.assertIn('const csvRows = ["case_id,task,model,quality,cost"]', site)
        self.assertIn("index < 20", site)
        for model in product.MODEL_DATA:
            self.assertIn(model, site)
        self.assertIn(result["status"], site)
        self.assertIn("91.5", site)
        self.assertIn("draft→terra, extract→luna, reason→terra", site)
        self.assertIn("95.17", site)
        self.assertIn("7.7", site)
        self.assertNotIn("escalation", site.lower())

    def test_higher_quality_floor_changes_selected_route(self):
        result = product.analyze({"quality_floor": "93", "results": product.CSV_DATA})
        self.assertEqual(
            result["artifact"]["best"]["route"],
            {"draft": "terra", "extract": "gpt-5.6", "reason": "terra"},
        )
        self.assertEqual(result["metrics"]["macro_average_quality"], 93.5)
        self.assertEqual(result["metrics"]["normalized_three_task_bundle_cost"], 4.7)

    def test_incomplete_matrix_returns_invalid_benchmark(self):
        rows = [
            line for line in product.CSV_DATA.splitlines()
            if ",reason,terra," not in line
        ]
        result = product.analyze({"quality_floor": "91", "results": "\n".join(rows)})
        self.assertEqual(result["status"], "INVALID_BENCHMARK")
        self.assertIn("Incomplete task-model matrix", result["headline"])

    def test_unreachable_floor_returns_no_feasible_route(self):
        result = product.analyze({"quality_floor": "101", "results": product.CSV_DATA})
        self.assertEqual(result["status"], "NO_FEASIBLE_ROUTE")
        self.assertEqual(result["items"], [])

    def test_invalid_floor_returns_invalid_benchmark(self):
        result = product.analyze({"quality_floor": "not-a-number", "results": product.CSV_DATA})
        self.assertEqual(result["status"], "INVALID_BENCHMARK")
        result = product.analyze({"quality_floor": "nan", "results": product.CSV_DATA})
        self.assertEqual(result["status"], "INVALID_BENCHMARK")

    def test_non_finite_or_negative_measurements_are_invalid(self):
        non_finite = product.CSV_DATA.replace(",96,2.10", ",nan,2.10", 1)
        self.assertEqual(
            product.analyze({"quality_floor": "91", "results": non_finite})["status"],
            "INVALID_BENCHMARK",
        )
        negative = product.CSV_DATA.replace(",96,2.10", ",96,-2.10", 1)
        self.assertEqual(
            product.analyze({"quality_floor": "91", "results": negative})["status"],
            "INVALID_BENCHMARK",
        )

    def test_metric_names_state_their_actual_grain(self):
        result = product.analyze({field.name: field.value for field in product.PRODUCT.fields})
        self.assertEqual(
            set(result["metrics"]),
            {
                "macro_average_quality",
                "normalized_three_task_bundle_cost",
                "fixture_cost_reduction",
                "cases",
            },
        )


if __name__ == "__main__":
    unittest.main()
