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
        self.assertIn('value: "3", label: "failure modes"', site)
        for title in ("Customer context drift", "Duplicate refund side effect", "$750 limit bypass"):
            self.assertIn(title, site)

    def test_diagnosis_changes_when_duplicate_is_removed(self):
        events = json.loads(product.TRACE)[:-1]
        result = product.analyze({"trace": json.dumps(events)})
        ids = {item["id"] for item in result["items"]}
        self.assertNotIn("DUPLICATE_SIDE_EFFECT", ids)
        self.assertEqual(result["metrics"]["findings"], 2)

    def test_duplicate_read_only_lookup_is_not_a_duplicate_side_effect(self):
        events = [
            {"seq": 1, "type": "context", "customer_id": "CUS-1", "verified": True},
            {"seq": 2, "type": "tool", "name": "lookup_customer", "args": {"customer_id": "CUS-1"}},
            {"seq": 3, "type": "tool", "name": "lookup_customer", "args": {"customer_id": "CUS-1"}},
        ]
        ids = {item["id"] for item in product.diagnose(events)}
        self.assertNotIn("DUPLICATE_SIDE_EFFECT", ids)

    def test_unknown_tool_effect_fails_closed(self):
        events = [
            {"seq": 1, "type": "context", "customer_id": "CUS-1", "verified": True},
            {"seq": 2, "type": "tool", "name": "mystery_tool", "args": {"customer_id": "CUS-1"}},
        ]
        ids = {item["id"] for item in product.diagnose(events)}
        self.assertIn("UNKNOWN_TOOL_EFFECT", ids)

    def test_high_value_refund_requires_complete_approval_schema(self):
        base = [
            {"seq": 1, "type": "context", "customer_id": "CUS-1", "verified": True},
            {
                "seq": 2,
                "type": "tool",
                "name": "issue_refund",
                "args": {"customer_id": "CUS-1", "amount": 750},
                "approval": {"present": True},
            },
        ]
        self.assertIn(
            "REFUND_LIMIT_BYPASS",
            {item["id"] for item in product.diagnose(base)},
        )
        base[1]["approval"] = {
            "present": True,
            "approved_by": "manager-7",
            "approval_id": "APR-42",
            "tool": "issue_refund",
            "customer_id": "CUS-1",
            "amount": 750,
            "action": "APPROVE",
        }
        self.assertNotIn(
            "REFUND_LIMIT_BYPASS",
            {item["id"] for item in product.diagnose(base)},
        )

    def test_approval_must_bind_to_refund_semantics(self):
        event = {
            "seq": 2,
            "type": "tool",
            "name": "issue_refund",
            "args": {"customer_id": "CUS-1", "amount": 750},
            "approval": {
                "present": True,
                "approved_by": "manager-7",
                "approval_id": "APR-42",
                "tool": "issue_refund",
                "customer_id": "CUS-2",
                "amount": 750,
                "action": "APPROVE",
            },
        }
        self.assertFalse(product.has_valid_approval(event))

    def test_irrelevant_note_cannot_hide_duplicate_refund(self):
        events = [
            {"seq": 1, "type": "context", "customer_id": "CUS-1", "verified": True},
            {"seq": 2, "type": "tool", "name": "issue_refund", "args": {"customer_id": "CUS-1", "amount": 100}},
            {"seq": 3, "type": "tool", "name": "issue_refund", "args": {"customer_id": "CUS-1", "amount": 100, "note": ""}},
        ]
        ids = {item["id"] for item in product.diagnose(events)}
        self.assertIn("DUPLICATE_SIDE_EFFECT", ids)

    def test_side_effect_target_must_match_verified_customer(self):
        events = [
            {"seq": 1, "type": "context", "customer_id": "CUS-1", "verified": True},
            {"seq": 2, "type": "tool", "name": "send_email", "args": {"customer_id": "CUS-2"}},
        ]
        ids = {item["id"] for item in product.diagnose(events)}
        self.assertIn("CUSTOMER_CONTEXT_DRIFT", ids)

    def test_invalid_sequence_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid trace sequence"):
            product.diagnose([
                {"seq": 1, "type": "context", "customer_id": "CUS-1", "verified": True},
                {"seq": 3, "type": "tool", "name": "lookup_customer", "args": {"customer_id": "CUS-1"}},
            ])

    def test_event_type_allowlist_fails_closed(self):
        events = [
            {"seq": 1, "type": "context", "customer_id": "CUS-1", "verified": True},
            {
                "seq": 2,
                "type": "TOOL",
                "name": "issue_refund",
                "args": {"customer_id": "CUS-1", "amount": 750},
            },
        ]
        result = product.analyze({"trace": json.dumps(events)})
        self.assertEqual(result["status"], "INVALID_INPUT")
        self.assertIn("unsupported type", result["headline"])

    def test_refund_amount_must_be_finite_numeric_value(self):
        for amount in (float("nan"), float("inf"), "750", True):
            events = [
                {"seq": 1, "type": "context", "customer_id": "CUS-1", "verified": True},
                {
                    "seq": 2,
                    "type": "tool",
                    "name": "issue_refund",
                    "args": {"customer_id": "CUS-1", "amount": amount},
                },
            ]
            result = product.analyze({"trace": json.dumps(events)})
            self.assertEqual(result["status"], "INVALID_INPUT")
            self.assertEqual(result["items"], [])

    def test_rerun_is_not_claimed_without_execution(self):
        result = product.analyze(
            {field.name: field.value for field in product.PRODUCT.fields}
        )
        self.assertEqual(result["artifact"]["rerun"], "NOT_RUN")


if __name__ == "__main__":
    unittest.main()
