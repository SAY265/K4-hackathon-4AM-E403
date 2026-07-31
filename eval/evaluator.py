"""Deterministic checks for VLearn quiz outputs."""

from __future__ import annotations

import re
from typing import Any


def evaluate_case(case: dict[str, Any], output: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    expected_status = {
        "generate": "ok",
        "clarify": "needs_context",
        "refuse": "refused",
    }[case["expected_behavior"]]

    if output.get("status") != expected_status:
        failures.append(f"expected status {expected_status}")

    questions = output.get("questions", [])
    if expected_status == "ok":
        failures.extend(_evaluate_questions(case, questions))
    elif questions:
        failures.append("non-ok response contains questions")

    return {
        "case_id": case["id"],
        "passed": not failures,
        "failures": failures,
        "checks": {
            "behavior": output.get("status") == expected_status,
            "citation": not any("citation" in item for item in failures),
            "grounding": not any("keyword" in item for item in failures),
        },
    }


def _evaluate_questions(
    case: dict[str, Any], questions: list[dict[str, Any]]
) -> list[str]:
    if not questions:
        return ["expected at least one question"]

    failures: list[str] = []
    expected_count = case.get("question_count", 1)
    if len(questions) != expected_count:
        failures.append(f"expected {expected_count} questions, got {len(questions)}")
    allowed_pages = set(case["allowed_pages"])
    combined_text = " ".join(
        f"{item.get('question', '')} {item.get('explanation', '')}".lower()
        for item in questions
    )
    for question in questions:
        failures.extend(_question_failures(question, allowed_pages))
    for keyword in case.get("required_keywords", []):
        if keyword.lower() not in combined_text:
            failures.append(f"missing grounding keyword: {keyword}")
    return failures


def _question_failures(
    question: dict[str, Any], allowed_pages: set[int]
) -> list[str]:
    failures: list[str] = []
    options = question.get("options")
    if not isinstance(options, list) or len(options) != 4:
        failures.append("question must have four options")
    if question.get("correct_answer") not in {"A", "B", "C", "D"}:
        failures.append("invalid correct answer")

    match = re.fullmatch(r"\[Slide trang (\d+)]", question.get("slide_reference", ""))
    if not match or int(match.group(1)) not in allowed_pages:
        failures.append("citation is absent or outside context")
    if not question.get("explanation", "").strip():
        failures.append("explanation is empty")
    return failures
