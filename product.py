from __future__ import annotations

import json
import math
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
    operands = problem_operands(problem)
    if operands is None:
        return False
    try:
        return Fraction(answer) == sum(operands, Fraction())
    except (ValueError, ZeroDivisionError):
        return False


def problem_operands(problem: str) -> tuple[Fraction, Fraction] | None:
    match = re.fullmatch(r"\s*(\d+/\d+)\s*\+\s*(\d+/\d+)\s*", problem)
    if not match:
        return None
    try:
        return Fraction(match.group(1)), Fraction(match.group(2))
    except (ValueError, ZeroDivisionError):
        return None


def is_different_problem(original: str, replay: str) -> bool:
    original_operands = problem_operands(original)
    replay_operands = problem_operands(replay)
    return (
        original_operands is not None
        and replay_operands is not None
        and sorted(original_operands) != sorted(replay_operands)
    )


def reasoning_supports_answer(problem: str, answer: str, reasoning: str) -> bool:
    operands = problem_operands(problem)
    if operands is None or not answer_is_correct(problem, answer):
        return False
    left, right = operands
    denominator = math.lcm(left.denominator, right.denominator)
    left_numerator = left.numerator * (denominator // left.denominator)
    right_numerator = right.numerator * (denominator // right.denominator)
    text = reasoning.lower()
    if Fraction(answer) == 1:
        unit_names = {2: "halves", 3: "thirds", 4: "fourths", 5: "fifths"}
        count_names = {
            2: ("2", "two", "both"),
            3: ("3", "three"),
            4: ("4", "four"),
            5: ("5", "five"),
        }
        unit = unit_names.get(denominator)
        counts = count_names.get(left_numerator + right_numerator, ())
        return (
            unit is not None
            and unit in text
            and any(f"{count} {unit}" in text for count in counts)
            and ("one whole" in text or "make one" in text)
        )
    expected_sum = f"{left_numerator}/{denominator} + {right_numerator}/{denominator}"
    return (
        f"common denominator is {denominator}" in text
        and expected_sum in text
        and answer in text
    )


def counterexample_for(misconception: str, replay_problem: str, replay_answer: str) -> str:
    if misconception == "ADD_BOTH_PARTS":
        return f"Try {replay_problem}. Adding numerators and denominators directly does not produce {replay_answer}."
    if misconception == "INVERTED_FRACTION":
        return f"Try {replay_problem}. Addition uses equivalent fractions; no fraction is inverted. The answer is {replay_answer}."
    return f"Show equivalent fractions for {replay_problem}, then justify why the answer is {replay_answer}."


def evaluation_errors(cases: Any) -> list[str]:
    if not isinstance(cases, list):
        return ["Cases must be a JSON array."]
    errors = []
    if len(cases) != 20:
        errors.append(f"Expected exactly 20 cases; got {len(cases)}.")
    required = {
        "id", "problem", "answer", "reasoning", "label",
        "replay_problem", "replay_answer", "replay_reasoning",
    }
    invalid_rows = [
        index
        for index, case in enumerate(cases, start=1)
        if not isinstance(case, dict)
        or any(not isinstance(case.get(key), str) or not case[key].strip() for key in required)
    ]
    if invalid_rows:
        errors.append(f"Missing or non-text fields in cases: {invalid_rows}.")
        return errors
    ids = [case["id"] for case in cases]
    if len(set(ids)) != len(ids):
        errors.append("Case IDs must be unique.")
    unique_problems = {case["problem"] for case in cases}
    if len(unique_problems) < 5:
        errors.append(f"Expected at least 5 distinct starting problems; got {len(unique_problems)}.")
    label_counts = {
        label: sum(case["label"] == label for case in cases)
        for label in ("ADD_BOTH_PARTS", "CORRECT")
    }
    unsupported_labels = sorted({
        case["label"] for case in cases
        if case["label"] not in label_counts
    })
    if unsupported_labels:
        errors.append(f"Unsupported ground-truth labels: {', '.join(unsupported_labels)}.")
    if label_counts != {"ADD_BOTH_PARTS": 5, "CORRECT": 15}:
        errors.append(f"Expected ground truth 5 ADD_BOTH_PARTS / 15 CORRECT; got {label_counts}.")
    return errors


def analyze(payload: dict[str, str]) -> dict[str, Any]:
    cases = json.loads(payload["cases"])
    errors = evaluation_errors(cases)
    if errors:
        case_count = len(cases) if isinstance(cases, list) else 0
        unique_problems = (
            len({
                case.get("problem")
                for case in cases
                if isinstance(case, dict) and isinstance(case.get("problem"), str)
            })
            if isinstance(cases, list)
            else 0
        )
        return {
            "status": "INVALID_EVALUATION",
            "headline": errors[0],
            "metrics": {
                "cases": case_count,
                "f1": None,
                "misconceptions": 0,
                "resolved": 0,
                "unique_problems": unique_problems,
            },
            "items": [],
            "evidence": [],
            "artifact": {
                "evaluation_errors": errors,
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "exact_classification": False,
                "all_final_answers_correct": False,
                "expected_misconceptions": 0,
                "replay_outcomes": {"resolved": 0, "unresolved": 0},
            },
        }
    items, tp, fp, fn = [], 0, 0, 0
    for case in cases:
        predicted = classify(case["reasoning"])
        expected_positive, predicted_positive = case["label"] != "CORRECT", predicted not in ("CORRECT", "UNRESOLVED")
        tp += expected_positive and predicted_positive
        fp += not expected_positive and predicted_positive
        fn += expected_positive and not predicted_positive
        replay_correct = answer_is_correct(case["replay_problem"], case["replay_answer"])
        replay_is_different = is_different_problem(case["problem"], case["replay_problem"])
        replay_explanation_correct = reasoning_supports_answer(
            case["replay_problem"], case["replay_answer"], case["replay_reasoning"]
        )
        replay_status = (
            "RESOLVED"
            if replay_is_different and replay_correct and replay_explanation_correct
            else "UNRESOLVED"
        )
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
            "replay_is_different": replay_is_different,
            "replay_status": replay_status,
        })
    precision, recall = tp / (tp + fp) if tp + fp else 1.0, tp / (tp + fn) if tp + fn else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    flagged = [item for item in items if item["predicted"] not in ("CORRECT", "UNRESOLVED")]
    resolved = sum(item["replay_status"] == "RESOLVED" for item in flagged)
    exact_classification = all(item["predicted"] == item["expected"] for item in items)
    all_final_answers_correct = all(item["final_answer_correct"] for item in items)
    expected_misconceptions = sum(item["expected"] != "CORRECT" for item in items)
    return {
        "status": (
            "EVAL_PASS"
            if exact_classification
            and all_final_answers_correct
            and expected_misconceptions == 5
            and len(flagged) == 5
            and resolved == len(flagged)
            else "EVAL_FAIL"
        ),
        "headline": f"{resolved} of {len(flagged)} detected misconceptions resolved on a different problem",
        "metrics": {"cases": len(cases), "f1": round(f1, 2), "misconceptions": len(flagged), "resolved": resolved, "unique_problems": len({case["problem"] for case in cases})},
        "items": items,
        "evidence": [{"label": "taxonomy", "value": "ADD_BOTH_PARTS · INVERTED_FRACTION · UNRESOLVED"}],
        "artifact": {
            "evaluation_errors": [],
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "exact_classification": exact_classification,
            "all_final_answers_correct": all_final_answers_correct,
            "expected_misconceptions": expected_misconceptions,
            "replay_outcomes": {"resolved": resolved, "unresolved": len(flagged) - resolved},
        },
    }


def acceptance(result: dict[str, Any]) -> tuple[bool, dict[str, bool]]:
    flagged = [item for item in result["items"] if item["predicted"] == "ADD_BOTH_PARTS"]
    checks = {
        "evaluation_valid": result["status"] == "EVAL_PASS" and not result["artifact"]["evaluation_errors"],
        "twenty_cases": result["metrics"]["cases"] == 20,
        "five_distinct_problems": result["metrics"]["unique_problems"] >= 5,
        "all_final_answers_correct": (
            result["artifact"]["all_final_answers_correct"]
            and all(item["final_answer_correct"] for item in result["items"])
        ),
        "exact_ground_truth": (
            result["artifact"]["exact_classification"]
            and result["artifact"]["precision"] == 1.0
            and result["artifact"]["recall"] == 1.0
            and result["artifact"]["expected_misconceptions"] == 5
        ),
        "correct_answer_wrong_reasoning": len(flagged) == 5 and all(item["final_answer_correct"] for item in flagged),
        "replay_resolved": (
            len(flagged) == 5
            and all(item["replay_is_different"] and item["replay_status"] == "RESOLVED" for item in flagged)
        ),
    }
    return all(checks.values()), checks
