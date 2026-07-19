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
        self.assertIn("problemsFixture.flatMap", site)
        self.assertIn("replayProblem", site)
        self.assertIn("I added both numerators and both denominators", site)
        self.assertIn("The common denominator is 15", site)
        self.assertIn(result["status"], site)
        self.assertIn('value: "20", label: "labeled cases"', site)
        self.assertIn('value: "5", label: "hidden misconceptions"', site)
        self.assertIn('value: "5/5", label: "replays resolved"', site)
        self.assertIn("Fixed-set F1 is 1.00", site)

    def test_unresolved_replay_fails_acceptance(self):
        cases = json.loads(product.CASE_DATA)
        cases[0]["replay_reasoning"] = "I added both numerators and both denominators."
        result = product.analyze({"cases": json.dumps(cases)})
        passed, checks = product.acceptance(result)
        self.assertFalse(passed)
        self.assertFalse(checks["replay_resolved"])
        self.assertEqual(result["items"][0]["replay_status"], "UNRESOLVED")

    def test_answer_is_checked_against_each_problem(self):
        cases = json.loads(product.CASE_DATA)
        cases[4]["answer"] = "5/6"
        result = product.analyze({"cases": json.dumps(cases)})
        self.assertFalse(result["items"][4]["final_answer_correct"])

    def test_repeated_problem_fails_diversity_guard(self):
        cases = json.loads(product.CASE_DATA)
        for case in cases:
            case["problem"] = cases[0]["problem"]
        result = product.analyze({"cases": json.dumps(cases)})
        passed, checks = product.acceptance(result)
        self.assertFalse(passed)
        self.assertFalse(checks["five_distinct_problems"])

    def test_counterexample_is_misconception_specific(self):
        inverted = product.counterexample_for("INVERTED_FRACTION", "1/2 + 1/2", "1")
        added = product.counterexample_for("ADD_BOTH_PARTS", "1/2 + 1/2", "1")
        self.assertIn("no fraction is inverted", inverted)
        self.assertIn("Adding numerators and denominators", added)


if __name__ == "__main__":
    unittest.main()
