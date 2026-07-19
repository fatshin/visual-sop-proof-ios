import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import server


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.sop = {
            "title": "Test",
            "sourceFileName": "test.pdf",
            "steps": [
                {
                    "id": f"step_{index}",
                    "order": index,
                    "title": f"Step {index}",
                    "observableCriteria": "A visible criterion",
                    "requiredViews": ["box"],
                    "riskNote": "",
                }
                for index in range(1, 5)
            ],
        }
        self.analysis = {
            "results": [
                {
                    "stepID": f"step_{index}",
                    "status": "verified",
                    "supportingFrameIDs": ["frame_000"],
                    "contradictingFrameIDs": [],
                    "contextFrameIDs": [],
                    "observedFacts": ["Visible."],
                    "missingViewCodes": [],
                    "coverage": "Sampled.",
                    "confidence": "high",
                    "reviewReason": "",
                }
                for index in range(1, 5)
            ]
        }

    def test_valid_compiled_sop(self):
        validated = server.validate_compiled_sop(copy.deepcopy(self.sop))
        self.assertEqual([step["order"] for step in validated["steps"]], [1, 2, 3, 4])

    def test_duplicate_step_rejected(self):
        invalid = copy.deepcopy(self.sop)
        invalid["steps"][1]["id"] = "step_1"
        with self.assertRaises(server.ClientError):
            server.validate_compiled_sop(invalid)

    def test_unknown_frame_rejected(self):
        invalid = copy.deepcopy(self.analysis)
        invalid["results"][0]["supportingFrameIDs"] = ["frame_999"]
        with self.assertRaises(server.ClientError):
            server.validate_analysis(invalid, self.sop, {"frame_000"})

    def test_verified_requires_support(self):
        invalid = copy.deepcopy(self.analysis)
        invalid["results"][0]["supportingFrameIDs"] = []
        with self.assertRaises(server.ClientError):
            server.validate_analysis(invalid, self.sop, {"frame_000"})

    def test_not_evidenced_can_cite_context_only(self):
        valid = copy.deepcopy(self.analysis)
        valid["results"][0]["status"] = "not_evidenced"
        valid["results"][0]["supportingFrameIDs"] = []
        valid["results"][0]["contextFrameIDs"] = ["frame_000"]
        valid["results"][0]["missingViewCodes"] = ["side_views"]
        valid["results"][0]["confidence"] = "medium"
        valid["results"][0]["reviewReason"] = "Side views require human review."
        results = server.validate_analysis(valid, self.sop, {"frame_000"})
        self.assertEqual(results[0]["status"], "not_evidenced")

    def test_not_evidenced_rejects_supporting_evidence(self):
        invalid = copy.deepcopy(self.analysis)
        invalid["results"][0]["status"] = "not_evidenced"
        with self.assertRaises(server.ClientError):
            server.validate_analysis(invalid, self.sop, {"frame_000"})

    def test_not_evidenced_rejects_ungrounded_or_high_confidence_result(self):
        invalid = copy.deepcopy(self.analysis)
        invalid["results"][0].update({
            "status": "not_evidenced",
            "supportingFrameIDs": [],
            "contextFrameIDs": [],
            "observedFacts": [],
            "missingViewCodes": [],
            "confidence": "high",
            "reviewReason": "",
        })
        with self.assertRaisesRegex(server.ClientError, "grounded"):
            server.validate_analysis(invalid, self.sop, {"frame_000"})

    def test_sha256_requires_lowercase_hex(self):
        self.assertEqual(server.require_sha256("a" * 64, "digest"), "a" * 64)
        with self.assertRaises(server.ClientError):
            server.require_sha256("not-a-digest", "digest")


if __name__ == "__main__":
    unittest.main()
