from __future__ import annotations

import json
import re
from fractions import Fraction
from typing import Any

from runtime.contracts import Field, Product


CASES = []
for index in range(20):
    misconception = index % 4 == 0
    CASES.append({
        "id": f"M{index + 1:02}", "problem": "1/2 + 1/3", "answer": "5/6",
        "reasoning": "I added both numerators and both denominators, then changed it to 5/6." if misconception else "The common denominator is 6, so 3/6 + 2/6 = 5/6.",
        "label": "ADD_BOTH_PARTS" if misconception else "CORRECT",
    })
CASE_DATA = json.dumps(CASES, indent=2)

PRODUCT = Product(
    8, "misconception-replay", "Misconception Replay",
    "Check the reasoning behind a correct answer, then test whether the misconception is gone.",
    "#ec4899", (Field("cases", "Student solutions (JSON)", CASE_DATA, 22),),
)


def classify(reasoning: str) -> str:
    text = reasoning.lower()
    if "added both numerators" in text and "both denominators" in text:
        return "ADD_BOTH_PARTS"
    if re.search(r"common denominator|equivalent fraction|3/6\s*\+\s*2/6", text):
        return "CORRECT"
    if "invert" in text:
        return "INVERTED_FRACTION"
    return "UNRESOLVED"


def analyze(payload: dict[str, str]) -> dict[str, Any]:
    cases = json.loads(payload["cases"])
    items, tp, fp, fn = [], 0, 0, 0
    for case in cases:
        predicted = classify(case["reasoning"])
        expected_positive, predicted_positive = case["label"] != "CORRECT", predicted not in ("CORRECT", "UNRESOLVED")
        tp += expected_positive and predicted_positive
        fp += not expected_positive and predicted_positive
        fn += expected_positive and not predicted_positive
        items.append({"id": case["id"], "answer": case["answer"], "final_answer_correct": Fraction(case["answer"]) == Fraction(5, 6), "expected": case["label"], "predicted": predicted, "counterexample": "Try 1/2 + 1/2. Adding both denominators gives 2/4, but the correct answer is 1."})
    precision, recall = tp / (tp + fp) if tp + fp else 1.0, tp / (tp + fn) if tp + fn else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "status": "EVAL_PASS" if f1 >= 0.8 else "EVAL_FAIL",
        "headline": f"Reasoning misconceptions detected at F1 {f1:.2f}",
        "metrics": {"cases": len(cases), "f1": round(f1, 2), "misconceptions": sum(item["predicted"] != "CORRECT" for item in items)},
        "items": items,
        "evidence": [{"label": "taxonomy", "value": "ADD_BOTH_PARTS · INVERTED_FRACTION · UNRESOLVED"}],
        "artifact": {"precision": precision, "recall": recall, "f1": f1},
    }


def acceptance(result: dict[str, Any]) -> tuple[bool, dict[str, bool]]:
    flagged = [item for item in result["items"] if item["predicted"] == "ADD_BOTH_PARTS"]
    checks = {"twenty_cases": result["metrics"]["cases"] == 20, "f1_target": result["metrics"]["f1"] >= 0.8, "correct_answer_wrong_reasoning": len(flagged) == 5 and all(item["final_answer_correct"] for item in flagged)}
    return all(checks.values()), checks

