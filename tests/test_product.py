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

    def test_policy_values_are_compiled_instead_of_hardcoded(self):
        policy = product.POLICY.replace("$500", "$1000").replace(
            "Support may use lookup_customer and draft_reply.",
            "Support may use lookup_customer, draft_reply and issue_refund.",
        )
        ir = product.compile_policy(policy)
        self.assertEqual(ir["refund_approval_above"], 1000)
        self.assertIn("issue_refund", ir["role_allowlists"]["support"])
        decision = product.evaluate(
            ir,
            {"role": "support", "tool": "issue_refund", "amount": 900},
        )
        self.assertEqual(decision["decision"], "ALLOW")

    def test_refund_threshold_is_strictly_above_500(self):
        ir = product.compile_policy(product.POLICY)
        at_threshold = product.evaluate(
            ir,
            {"role": "finance", "tool": "issue_refund", "amount": 500},
        )
        above_threshold = product.evaluate(
            ir,
            {"role": "finance", "tool": "issue_refund", "amount": 500.01},
        )
        self.assertEqual(at_threshold["decision"], "ALLOW")
        self.assertEqual(above_threshold["decision"], "APPROVAL_REQUIRED")
        self.assertEqual(above_threshold["reason"], ir["citations"]["POL-02"])

    def test_every_non_allow_decision_has_an_exact_source_citation(self):
        result = product.analyze(
            {field.name: field.value for field in product.PRODUCT.fields}
        )
        citations = result["artifact"]["citations"]
        for item in result["items"]:
            if item["decision"] != "ALLOW":
                self.assertIn(item["rule"], citations)
                self.assertEqual(item["reason"], citations[item["rule"]])
        support_denial = next(item for item in result["items"] if item["id"] == "S5")
        self.assertEqual(support_denial["rule"], "POL-03")
        finance_denial = product.evaluate(
            result["artifact"],
            {"role": "finance", "tool": "draft_reply", "amount": 0},
        )
        self.assertEqual(finance_denial["rule"], "POL-04")
        self.assertEqual(
            finance_denial["reason"],
            result["artifact"]["citations"]["POL-04"],
        )

    def test_public_fixture_matches_engine_fixture(self):
        site = Path("site/app/product-data.ts").read_text()
        result = product.analyze({field.name: field.value for field in product.PRODUCT.fields})
        for line in product.POLICY.splitlines():
            self.assertIn(line, site)
        for scenario in __import__("json").loads(product.SCENARIOS):
            self.assertIn(f'"id":"{scenario["id"]}"', site)
            self.assertIn(f'"tool":"{scenario["tool"]}"', site)
        self.assertIn(result["status"], site)
        self.assertIn('value: "3 / 2 / 2"', site)
        self.assertIn("S2 is blocked by POL-01", site)
        self.assertIn("S4 crosses the $500 threshold", site)
        self.assertIn("S5 cites the exact POL-03 support allowlist sentence", site)


if __name__ == "__main__":
    unittest.main()
