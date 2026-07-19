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
        self.assertIn("Six linked repair instructions", site)

    def test_corrected_notice_clears_the_release_gate(self):
        source = json.loads(product.SOURCE)
        corrected = """Emergency Support Benefit
Apply by 2026-08-31 at 23:59.
Every resident aged 18 or older receives ¥50,000.
You must have lived in the city by 2026-04-01.
Questions: benefits@example.go.jp"""
        result = product.analyze({"notice": corrected, "source": json.dumps(source)})
        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["items"], [])

    def test_issued_date_and_press_email_are_not_mistaken_for_claims(self):
        source = json.loads(product.SOURCE)
        notice = """Emergency Support Benefit
Issued on 2026-01-15.
Apply by 2026-08-31 at 23:59.
Every resident aged 18 or older receives ¥50,000.
You must have lived in the city by 2026-04-01.
Press: press@example.go.jp
Questions: benefits@example.go.jp"""
        self.assertEqual(product.inspect_notice(notice, source), [])

    def test_multiple_labeled_deadlines_fail_closed_as_ambiguous(self):
        source = json.loads(product.SOURCE)
        notice = """Emergency Support Benefit
Apply by 2026-08-31 at 23:59.
Application deadline: 2026-09-30.
Every resident aged 18 or older receives ¥50,000.
You must have lived in the city by 2026-04-01.
Questions: benefits@example.go.jp"""
        deadline = next(
            item
            for item in product.inspect_notice(notice, source)
            if item["id"] == "DEADLINE"
        )
        self.assertEqual(deadline["actual"], "AMBIGUOUS")

    def test_unlabeled_date_and_email_fail_closed_as_missing(self):
        source = json.loads(product.SOURCE)
        notice = """Emergency Support Benefit
Issued on 2026-08-31.
Every resident aged 18 or older receives ¥50,000.
You must have lived in the city by 2026-04-01.
Press: benefits@example.go.jp"""
        findings = {item["id"]: item for item in product.inspect_notice(notice, source)}
        self.assertEqual(findings["DEADLINE"]["actual"], "MISSING")
        self.assertEqual(findings["CONTACT"]["actual"], "MISSING")

    def test_repairs_are_source_linked_instructions_not_publishable_copy(self):
        result = product.analyze(
            {field.name: field.value for field in product.PRODUCT.fields}
        )
        for item in result["items"]:
            self.assertTrue(item["repair"])
            if item["id"] != "UNSUPPORTED_EXCEPTION":
                self.assertIn(f"source.{item['source']}", item["repair"])

    def test_late_application_promise_paraphrases_are_detected(self):
        source = json.loads(product.SOURCE)
        corrected = """Emergency Support Benefit
Apply by 2026-08-31 at 23:59.
Every resident aged 18 or older receives ¥50,000.
You must have lived in the city by 2026-04-01.
Questions: benefits@example.go.jp"""
        for promise in (
            "Late applications will be accepted.",
            "Applications after the deadline can still be accepted.",
            "Applications submitted after the deadline may still be accepted.",
            "Applications received after the deadline may be accepted.",
            "Applications filed after the deadline may be accepted.",
            "We may accept applications received after the deadline.",
            "We may accept applications received after deadline.",
            "We can still accept applications after the deadline.",
        ):
            findings = product.inspect_notice(f"{corrected}\n{promise}", source)
            self.assertIn("UNSUPPORTED_EXCEPTION", {item["id"] for item in findings})

    def test_late_application_rejection_is_not_a_false_positive(self):
        source = json.loads(product.SOURCE)
        notice = """Emergency Support Benefit
Apply by 2026-08-31 at 23:59.
Every resident aged 18 or older receives ¥50,000.
You must have lived in the city by 2026-04-01.
Questions: benefits@example.go.jp
Late applications will not be accepted."""
        self.assertEqual(product.inspect_notice(notice, source), [])

    def test_non_promise_deadline_language_is_not_flagged(self):
        source = json.loads(product.SOURCE)
        corrected = """Emergency Support Benefit
Apply by 2026-08-31 at 23:59.
Every resident aged 18 or older receives ¥50,000.
You must have lived in the city by 2026-04-01.
Questions: benefits@example.go.jp"""
        for statement in (
            "We may accept applications before the deadline.",
            "We may not accept applications after the deadline.",
            "Contact us after the deadline for questions.",
        ):
            self.assertEqual(
                product.inspect_notice(f"{corrected}\n{statement}", source),
                [],
            )


if __name__ == "__main__":
    unittest.main()
