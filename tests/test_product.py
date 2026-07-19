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

    def test_browser_crlf_submission_still_builds_patch(self):
        payload = {field.name: field.value.replace("\n", "\r\n") for field in product.PRODUCT.fields}
        result = product.analyze(payload)
        self.assertEqual(result["status"], "READY_FOR_HUMAN_APPLY")
        self.assertIn("idempotency_key", result["artifact"]["patch"])

    def test_fixture_checks_reproduce_failure_and_verify_patch(self):
        self.assertEqual(product.run_fixture_checks(patched=False), [False] * 4)
        self.assertEqual(product.run_fixture_checks(patched=True), [True] * 4)

    def test_empty_order_id_is_rejected_before_charge(self):
        self.assertEqual(product.run_patch_safety_checks(patched=False), [False, False])
        self.assertEqual(product.run_patch_safety_checks(patched=True), [True, True])
        patched = product.checkout_fixture(1, 100, "", "", patched=True)
        self.assertEqual(
            patched,
            {"ok": False, "error": "missing_order_id", "charges": 0},
        )
        result = product.analyze(
            {field.name: field.value for field in product.PRODUCT.fields}
        )
        self.assertEqual(result["status"], "READY_FOR_HUMAN_APPLY")
        self.assertIn("if not order_id", result["artifact"]["patch"])
        self.assertTrue(
            all(result["artifact"]["patch_safety_checks"].values())
        )

    def test_incomplete_duplicate_or_nonsense_requirements_fail_closed(self):
        payload = {field.name: field.value for field in product.PRODUCT.fields}
        payload["transcript"] = product.TRANSCRIPT.replace(
            "[01:48] Ken: REQ-4 Retry must not create a second charge.\n", ""
        )
        self.assertEqual(product.analyze(payload)["status"], "NEEDS_CLARIFICATION")

        payload["transcript"] = product.TRANSCRIPT.replace("REQ-4", "REQ-3")
        duplicate = product.analyze(payload)
        self.assertEqual(duplicate["status"], "NEEDS_CLARIFICATION")
        self.assertTrue(any("Duplicate requirement IDs" in item for item in duplicate["artifact"]["ambiguities"]))

        payload["transcript"] = product.TRANSCRIPT.replace(
            "Checkout must reject a quantity below 1.", "Make checkout nicer."
        )
        nonsense = product.analyze(payload)
        self.assertEqual(nonsense["status"], "NEEDS_CLARIFICATION")
        self.assertTrue(any("Unsupported requirement wording" in item for item in nonsense["artifact"]["ambiguities"]))

    def test_unsupported_source_cannot_be_ready(self):
        payload = {field.name: field.value for field in product.PRODUCT.fields}
        payload["source"] = 'def checkout(quantity, total, manager_token="", order_id=""):\n    return {"ok": True}'
        result = product.analyze(payload)
        self.assertEqual(result["status"], "NEEDS_CLARIFICATION")
        self.assertEqual(result["artifact"]["patch"], "")

        payload["source"] = (
            "def checkout(quantity, total, manager_token=\"\", order_id=\"\"):\n"
            "    return {\"ok\": True}\n\n"
            "def decoy():\n"
            "    approved = total >= 500\n"
            "    charge()\n"
            "    return {\"ok\": True, \"order\": \"\"}\n"
        )
        result = product.analyze(payload)
        self.assertEqual(result["status"], "NEEDS_CLARIFICATION")
        self.assertEqual(result["artifact"]["patch"], "")

    def test_public_fixture_matches_engine_fixture(self):
        site = Path("site/app/product-data.ts").read_text()
        result = product.analyze({field.name: field.value for field in product.PRODUCT.fields})
        for line in product.TRANSCRIPT.splitlines():
            self.assertIn(line, site)
        for line in product.SOURCE.splitlines():
            self.assertIn(line, site)
        self.assertIn(result["status"], site)
        self.assertIn('value: "4", label: "baseline failures"', site)
        self.assertIn('value: "4", label: "scenario passes"', site)
        self.assertIn("Human apply gate preserved", site)
        self.assertIn("deterministic scenario checks", site)
        self.assertIn("Non-empty order ID guard", site)


if __name__ == "__main__":
    unittest.main()
