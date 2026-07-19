from __future__ import annotations

import json
import re
from fractions import Fraction
from typing import Any

from runtime.contracts import Field, Product


PROBLEMS = [
    ("1/2 + 1/3", "5/6", "The common denominator is 6, so 3/6 + 2/6 = 5/6.", "1/2 + 1/2", "1", "Both halves make one whole."),
    ("2/3 + 1/4", "11/12", "The common denominator is 12, so 8/12 + 3/12 = 11/12.", "2/3 + 1/3", "1", "Three thirds make one whole."),
    ("3/4 + 1/6", "11/12", "The common denominator is 12, so 9/12 + 2/12 = 11/12.", "3/4 + 1/4", "1", "Four fourths make one whole."),
    ("1/5 + 1/2", "7/10", "The common denominator is 10, so 2/10 + 5/10 = 7/10.", "1/5 + 4/5", "1", "Five fifths make one whole."),
    ("2/5 + 1/3", "11/15", "The common denominator is 15, so 6/15 + 5/15 = 11/15.", "2/5 + 3/5", "1", "Five fifths make one whole."),
]

CASES = []
for problem_index, (problem, answer, reasoning, replay_problem, replay_answer, replay_reasoning) in enumerate(PROBLEMS):
    for repetition in range(4):
        misconception = repetition == 0
        CASES.append({
            "id": f"M{problem_index * 4 + repetition + 1:02}",
            "problem": problem,
            "answer": answer,
            "reasoning": f"I added both numerators and both denominators, then changed it to {answer}." if misconception else reasoning,
            "label": "ADD_BOTH_PARTS" if misconception else "CORRECT",
            "replay_problem": replay_problem,
            "replay_answer": replay_answer,
            "replay_reasoning": replay_reasoning,
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
    if re.search(r"common denominator|equivalent fraction|\b(one whole|make one)\b", text):
        return "CORRECT"
    if "invert" in text:
        return "INVERTED_FRACTION"
    return "UNRESOLVED"


def answer_is_correct(problem: str, answer: str) -> bool:
    match = re.fullmatch(r"\s*(\d+/\d+)\s*\+\s*(\d+/\d+)\s*", problem)
    if not match:
        return False
    try:
        return Fraction(answer) == Fraction(match.group(1)) + Fraction(match.group(2))
    except (ValueError, ZeroDivisionError):
        return False


def counterexample_for(misconception: str, replay_problem: str, replay_answer: str) -> str:
    if misconception == "ADD_BOTH_PARTS":
        return f"Try {replay_problem}. Adding numerators and denominators directly does not produce {replay_answer}."
    if misconception == "INVERTED_FRACTION":
        return f"Try {replay_problem}. Addition uses equivalent fractions; no fraction is inverted. The answer is {replay_answer}."
    return f"Show equivalent fractions for {replay_problem}, then justify why the answer is {replay_answer}."


def analyze(payload: dict[str, str]) -> dict[str, Any]:
    cases = json.loads(payload["cases"])
    items, tp, fp, fn = [], 0, 0, 0
    for case in cases:
        predicted = classify(case["reasoning"])
        expected_positive, predicted_positive = case["label"] != "CORRECT", predicted not in ("CORRECT", "UNRESOLVED")
        tp += expected_positive and predicted_positive
        fp += not expected_positive and predicted_positive
        fn += expected_positive and not predicted_positive
        replay_correct = answer_is_correct(case["replay_problem"], case["replay_answer"])
        replay_explanation_correct = classify(case["replay_reasoning"]) == "CORRECT"
        replay_status = "RESOLVED" if replay_correct and replay_explanation_correct else "UNRESOLVED"
        items.append({
            "id": case["id"],
            "problem": case["problem"],
            "answer": case["answer"],
            "final_answer_correct": answer_is_correct(case["problem"], case["answer"]),
            "expected": case["label"],
            "predicted": predicted,
            "counterexample": counterexample_for(predicted, case["replay_problem"], case["replay_answer"]),
            "replay_problem": case["replay_problem"],
            "replay_answer": case["replay_answer"],
            "replay_reasoning": case["replay_reasoning"],
            "replay_status": replay_status,
        })
    precision, recall = tp / (tp + fp) if tp + fp else 1.0, tp / (tp + fn) if tp + fn else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    flagged = [item for item in items if item["predicted"] not in ("CORRECT", "UNRESOLVED")]
    resolved = sum(item["replay_status"] == "RESOLVED" for item in flagged)
    return {
        "status": "EVAL_PASS" if f1 >= 0.8 and resolved == len(flagged) else "EVAL_FAIL",
        "headline": f"{resolved} of {len(flagged)} detected misconceptions resolved on a different problem",
        "metrics": {"cases": len(cases), "f1": round(f1, 2), "misconceptions": len(flagged), "resolved": resolved, "unique_problems": len({case["problem"] for case in cases})},
        "items": items,
        "evidence": [{"label": "taxonomy", "value": "ADD_BOTH_PARTS · INVERTED_FRACTION · UNRESOLVED"}],
        "artifact": {"precision": precision, "recall": recall, "f1": f1, "replay_outcomes": {"resolved": resolved, "unresolved": len(flagged) - resolved}},
    }


def acceptance(result: dict[str, Any]) -> tuple[bool, dict[str, bool]]:
    flagged = [item for item in result["items"] if item["predicted"] == "ADD_BOTH_PARTS"]
    checks = {
        "twenty_cases": result["metrics"]["cases"] == 20,
        "five_distinct_problems": result["metrics"]["unique_problems"] >= 5,
        "f1_target": result["metrics"]["f1"] >= 0.8,
        "correct_answer_wrong_reasoning": len(flagged) == 5 and all(item["final_answer_correct"] for item in flagged),
        "replay_resolved": len(flagged) == 5 and all(item["replay_status"] == "RESOLVED" for item in flagged),
    }
    return all(checks.values()), checks
