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
        for decision in json.loads(product.DECISIONS):
            self.assertIn(f'"id":"{decision["id"]}"', site)
            self.assertIn(f'"decision":"{decision["decision"]}"', site)
            self.assertIn(f'"owner":"{decision["owner"]}"', site)
            self.assertIn(f'"decided_at":"{decision["decided_at"]}"', site)
            self.assertIn(decision["invalidate_when"], site)
            self.assertIn(decision["review_when"], site)
        for decision_id, evidence in json.loads(product.EVIDENCE).items():
            self.assertIn(f'"{decision_id}"', site)
            self.assertIn(evidence["source"], site)
        self.assertIn(result["status"], site)
        for title in ("D-1 is invalidated", "D-2 remains valid", "D-3 is at risk"):
            self.assertIn(title, site)
        self.assertIn("duplicate IDs produce INVALID_INPUT", site)

    def test_new_evidence_can_restore_current_status(self):
        evidence = json.loads(product.EVIDENCE)
        evidence["D-1"]["quality"] = 85
        evidence["D-3"]["complaints"] = 2
        result = product.analyze({"decisions": product.DECISIONS, "evidence": json.dumps(evidence)})
        self.assertEqual(result["status"], "CURRENT")
        self.assertEqual(result["metrics"], {"valid": 3, "at_risk": 0, "invalidated": 0, "needs_evidence": 0})

    def test_at_risk_without_invalidation_requires_review(self):
        evidence = json.loads(product.EVIDENCE)
        evidence["D-1"]["quality"] = 85
        result = product.analyze({"decisions": product.DECISIONS, "evidence": json.dumps(evidence)})
        self.assertEqual(result["status"], "REVIEW_REQUIRED")

    def test_missing_decision_evidence_fails_closed(self):
        evidence = json.loads(product.EVIDENCE)
        del evidence["D-2"]
        result = product.analyze({"decisions": product.DECISIONS, "evidence": json.dumps(evidence)})
        d2 = next(item for item in result["items"] if item["id"] == "D-2")
        self.assertEqual(d2["status"], "NEEDS_EVIDENCE")
        self.assertEqual(result["status"], "ACTION_REQUIRED")

        evidence["D-1"]["quality"] = 85
        evidence["D-3"]["complaints"] = 2
        result = product.analyze({"decisions": product.DECISIONS, "evidence": json.dumps(evidence)})
        self.assertEqual(result["status"], "EVIDENCE_REQUIRED")

    def test_missing_condition_value_or_source_fails_closed(self):
        evidence = json.loads(product.EVIDENCE)
        del evidence["D-2"]["uptime"]
        result = product.analyze({"decisions": product.DECISIONS, "evidence": json.dumps(evidence)})
        d2 = next(item for item in result["items"] if item["id"] == "D-2")
        self.assertEqual(d2["status"], "NEEDS_EVIDENCE")
        self.assertIn("Missing evidence for uptime", d2["evidence"])

        evidence = json.loads(product.EVIDENCE)
        del evidence["D-1"]["source"]
        result = product.analyze({"decisions": product.DECISIONS, "evidence": json.dumps(evidence)})
        d1 = next(item for item in result["items"] if item["id"] == "D-1")
        self.assertEqual(d1["status"], "NEEDS_EVIDENCE")
        self.assertEqual(d1["source"], "missing")

    def test_missing_decision_metadata_fails_closed_and_events_are_emitted(self):
        decisions = json.loads(product.DECISIONS)
        del decisions[1]["owner"]
        result = product.analyze({"decisions": json.dumps(decisions), "evidence": product.EVIDENCE})
        d2 = next(item for item in result["items"] if item["id"] == "D-2")
        self.assertEqual(d2["status"], "NEEDS_EVIDENCE")
        self.assertEqual(len(result["artifact"]["events"]), 3)
        self.assertEqual(result["artifact"]["events"][1]["type"], "STATUS_TRANSITION")
        self.assertEqual(result["artifact"]["events"][1]["from"], "UNASSESSED")
        self.assertEqual(result["artifact"]["events"][1]["to"], "NEEDS_EVIDENCE")

    def test_unsupported_condition_fails_closed(self):
        decisions = json.loads(product.DECISIONS)
        decisions[1]["invalidate_when"] = "uptime approximately 99.5"
        result = product.analyze({"decisions": json.dumps(decisions), "evidence": product.EVIDENCE})
        d2 = next(item for item in result["items"] if item["id"] == "D-2")
        self.assertEqual(d2["status"], "NEEDS_EVIDENCE")
        self.assertIn("Unsupported condition", d2["evidence"])

    def test_missing_condition_keys_fail_closed_without_key_error(self):
        for condition_key in ("invalidate_when", "review_when"):
            decisions = json.loads(product.DECISIONS)
            del decisions[0][condition_key]
            result = product.analyze(
                {"decisions": json.dumps(decisions), "evidence": product.EVIDENCE}
            )
            d1 = next(item for item in result["items"] if item["id"] == "D-1")
            self.assertEqual(d1["status"], "NEEDS_EVIDENCE")
            self.assertIn("Missing or non-text condition", d1["evidence"])

    def test_duplicate_decision_ids_are_invalid_input(self):
        decisions = json.loads(product.DECISIONS)
        decisions[1]["id"] = "D-1"
        result = product.analyze(
            {"decisions": json.dumps(decisions), "evidence": product.EVIDENCE}
        )
        self.assertEqual(result["status"], "INVALID_INPUT")
        duplicated = [item for item in result["items"] if item["id"] == "D-1"]
        self.assertEqual(len(duplicated), 2)
        self.assertTrue(all(item["status"] == "NEEDS_EVIDENCE" for item in duplicated))
        self.assertEqual(
            result["artifact"]["input_errors"],
            ["Duplicate decision ID: D-1"],
        )

    def test_missing_decision_id_is_invalid_input(self):
        decisions = json.loads(product.DECISIONS)
        del decisions[0]["id"]
        result = product.analyze(
            {"decisions": json.dumps(decisions), "evidence": product.EVIDENCE}
        )
        self.assertEqual(result["status"], "INVALID_INPUT")
        self.assertEqual(result["items"][0]["id"], "MISSING_ID_1")
        self.assertEqual(result["items"][0]["status"], "NEEDS_EVIDENCE")


if __name__ == "__main__":
    unittest.main()
