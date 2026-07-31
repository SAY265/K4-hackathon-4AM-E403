"""Deterministic scoring for grounded chatbot responses."""

from __future__ import annotations

import re
from typing import Any


def evaluate_chat_case(
    case: dict[str, Any], output: dict[str, Any]
) -> dict[str, Any]:
    failures: list[str] = []
    if output.get("status") != case["expected_status"]:
        failures.append(f"expected status {case['expected_status']}")

    answer = output.get("answer", "")
    if not isinstance(answer, str) or not answer.strip():
        failures.append("answer is empty")

    citations = output.get("citations", [])
    failures.extend(_citation_failures(case, citations))
    answer_lower = answer.lower()
    for keyword in case.get("required_keywords", []):
        if keyword.lower() not in answer_lower:
            failures.append(f"missing keyword: {keyword}")
    for keyword in case.get("forbidden_keywords", []):
        if keyword.lower() in answer_lower:
            failures.append(f"contains forbidden keyword: {keyword}")

    return {
        "case_id": case["id"],
        "passed": not failures,
        "failures": failures,
        "checks": {
            "behavior": output.get("status") == case["expected_status"],
            "citation": not any("citation" in item for item in failures),
            "content": not any("keyword" in item for item in failures),
        },
    }


def _citation_failures(
    case: dict[str, Any], citations: Any
) -> list[str]:
    if not isinstance(citations, list):
        return ["citations is not a list"]
    if case["expected_status"] != "ok":
        return []
    if not citations:
        return ["citation is missing"]

    allowed_pages = set(case["allowed_pages"])
    for citation in citations:
        match = re.fullmatch(r"\[Slide trang (\d+)]", citation)
        if not match:
            return ["citation format is invalid"]
        if int(match.group(1)) not in allowed_pages:
            return ["citation outside context"]
    return []
