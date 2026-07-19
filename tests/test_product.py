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
        for thesis in json.loads(product.THESES):
            self.assertIn(f'"id":"{thesis["id"]}"', site)
            self.assertIn(f'"rule":"{thesis["rule"]}"', site)
        for quarter in json.loads(product.QUARTERS):
            self.assertIn(f'"quarter":"{quarter["quarter"]}"', site)
            self.assertIn(quarter["source"], site)
        self.assertIn(result["status"], site)
        self.assertIn("42→40→37", site)
        self.assertIn("T-1 is broken", site)

    def test_rising_overseas_ratio_keeps_all_theses_intact(self):
        quarters = json.loads(product.QUARTERS)[1:]
        quarters.append({
            "quarter": "2026-Q2",
            "overseas_ratio": 38,
            "operating_margin": 13.0,
            "free_cash_flow": 450,
            "source": "fixtures/FY2026-Q2-results.md#page-10",
        })
        result = product.analyze({"theses": product.THESES, "quarters": json.dumps(quarters)})
        self.assertEqual(result["status"], "THESES_INTACT")
        self.assertEqual(result["metrics"]["broken"], 0)

    def test_multi_period_trigger_cites_all_three_source_pages(self):
        result = product.analyze({"theses": product.THESES, "quarters": product.QUARTERS})
        t1 = next(item for item in result["items"] if item["id"] == "T-1")
        self.assertEqual(
            t1["sources"],
            [
                "fixtures/FY2025-Q3-results.md#page-12",
                "fixtures/FY2025-Q4-results.md#page-9",
                "fixtures/FY2026-Q1-results.md#page-11",
            ],
        )

    def test_broken_theses_sort_first_stably(self):
        theses = json.loads(product.THESES)
        result = product.analyze({"theses": json.dumps(list(reversed(theses))), "quarters": product.QUARTERS})
        self.assertEqual(result["items"][0]["id"], "T-1")
        self.assertEqual([item["id"] for item in result["items"][1:]], ["T-3", "T-2"])

    def test_quarter_input_order_does_not_change_assessment(self):
        quarters = list(reversed(json.loads(product.QUARTERS)))
        result = product.analyze({"theses": product.THESES, "quarters": json.dumps(quarters)})
        baseline = product.analyze({"theses": product.THESES, "quarters": product.QUARTERS})
        self.assertEqual(result["items"], baseline["items"])
        self.assertEqual(result["evidence"], baseline["evidence"])

    def test_malformed_or_duplicate_quarter_is_rejected(self):
        malformed = json.loads(product.QUARTERS)
        malformed[0]["quarter"] = "Q3-2025"
        with self.assertRaisesRegex(ValueError, "Invalid quarter"):
            product.analyze({"theses": product.THESES, "quarters": json.dumps(malformed)})
        duplicate = json.loads(product.QUARTERS)
        duplicate[1]["quarter"] = duplicate[0]["quarter"]
        with self.assertRaisesRegex(ValueError, "Duplicate quarter"):
            product.analyze({"theses": product.THESES, "quarters": json.dumps(duplicate)})

    def test_quarter_history_must_be_adjacent(self):
        quarters = json.loads(product.QUARTERS)
        quarters[1]["quarter"] = "2026-Q2"
        with self.assertRaisesRegex(ValueError, "chronologically adjacent"):
            product.analyze({"theses": product.THESES, "quarters": json.dumps(quarters)})

    def test_non_finite_metric_is_rejected(self):
        quarters = json.loads(product.QUARTERS)
        quarters[-1]["operating_margin"] = float("nan")
        with self.assertRaisesRegex(ValueError, "non-finite operating_margin"):
            product.analyze({"theses": product.THESES, "quarters": json.dumps(quarters)})

    def test_unknown_rule_is_rejected(self):
        theses = json.loads(product.THESES)
        theses[1]["rule"] = "above:12"
        with self.assertRaisesRegex(ValueError, "Unsupported rule"):
            product.analyze({"theses": json.dumps(theses), "quarters": product.QUARTERS})

    def test_insufficient_history_is_rejected_deliberately(self):
        quarters = json.loads(product.QUARTERS)[:2]
        with self.assertRaisesRegex(ValueError, "requires at least 3 quarters"):
            product.analyze({"theses": product.THESES, "quarters": json.dumps(quarters)})

    def test_source_file_and_anchor_are_validated(self):
        for quarter in json.loads(product.QUARTERS):
            self.assertTrue(product.source_reference_valid(quarter["source"]))
        quarters = json.loads(product.QUARTERS)
        quarters[0]["source"] = "fixtures/FY2025-Q3-results.md#page-99"
        with self.assertRaisesRegex(ValueError, "Invalid source reference"):
            product.analyze({"theses": product.THESES, "quarters": json.dumps(quarters)})
        mismatch = json.loads(product.QUARTERS)
        mismatch[0]["overseas_ratio"] = 99
        with self.assertRaisesRegex(ValueError, "Source metric/value mismatch"):
            product.analyze({"theses": product.THESES, "quarters": json.dumps(mismatch)})

    def test_each_assessment_explains_break_and_reversal(self):
        result = product.analyze({"theses": product.THESES, "quarters": product.QUARTERS})
        t1 = result["items"][0]
        self.assertIn("two consecutive", t1["break_condition"])
        self.assertIn("one flat or rising", t1["reversal_condition"])

    def test_one_rebound_restores_intact_under_stateless_rule(self):
        quarters = json.loads(product.QUARTERS)
        quarters.append({
            "quarter": "2026-Q2",
            "overseas_ratio": 38,
            "operating_margin": 13.0,
            "free_cash_flow": 450,
            "source": "fixtures/FY2026-Q2-results.md#page-10",
        })
        result = product.analyze({
            "theses": product.THESES,
            "quarters": json.dumps(quarters),
        })
        t1 = next(item for item in result["items"] if item["id"] == "T-1")
        self.assertEqual(t1["status"], "INTACT")
        self.assertIn("one flat or rising", t1["reversal_condition"])

    def test_supported_rule_parser_is_explicit(self):
        self.assertEqual(product.parse_rule("two_consecutive_declines"), ("two_consecutive_declines", None))
        self.assertEqual(product.parse_rule("below:-2.5"), ("below", -2.5))
        with self.assertRaisesRegex(ValueError, "Unsupported rule"):
            product.parse_rule("approximately:12")


if __name__ == "__main__":
    unittest.main()
