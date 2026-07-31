"""Pure helpers shared by the Streamlit interface and tests."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import re
from typing import Any


@dataclass(frozen=True)
class QuizComposition:
    multiple_choice_count: int
    essay_count: int

    @property
    def total_count(self) -> int:
        return self.multiple_choice_count + self.essay_count


def build_context(
    pages: Mapping[int, str], first_page: int, last_page: int
) -> str:
    selected = (
        f"[Slide trang {page_number}] {pages[page_number].strip()}"
        for page_number in range(first_page, last_page + 1)
        if pages.get(page_number, "").strip()
    )
    return "\n\n".join(selected)


def option_letter(option_index: int) -> str:
    if not 0 <= option_index <= 3:
        raise ValueError("option_index must be between 0 and 3")
    return "ABCD"[option_index]


def is_quiz_request(message: str) -> bool:
    return bool(
        re.search(
            r"(?i)\b(quiz|quizz|bộ đề|trắc nghiệm|tự luận|"
            r"kiểm tra (?:mình|tôi)|tạo câu hỏi)\b",
            message,
        )
    )


def parse_quiz_composition(message: str) -> QuizComposition:
    normalized = message.lower()
    multiple_choice_count = _count_for_type(normalized, r"trắc\s*nghiệm")
    essay_count = _count_for_type(normalized, r"tự\s*luận")
    if multiple_choice_count is not None or essay_count is not None:
        return QuizComposition(multiple_choice_count or 0, essay_count or 0)

    total_match = re.search(r"\b(\d{1,2})\s*câu\b", normalized)
    default_count = int(total_match.group(1)) if total_match else 5
    return QuizComposition(default_count, 0)


def _count_for_type(message: str, question_type: str) -> int | None:
    before_type = re.search(rf"\b(\d{{1,2}})\s*câu\s*{question_type}\b", message)
    if before_type:
        return int(before_type.group(1))
    after_type = re.search(rf"\b{question_type}\s*(\d{{1,2}})\s*câu\b", message)
    if after_type:
        return int(after_type.group(1))
    return None


def score_answers(
    questions: list[dict[str, Any]], answers: Mapping[int, str]
) -> int:
    return sum(
        answers.get(index) == question["correct_answer"]
        for index, question in enumerate(questions)
        if question.get("question_type", "multiple_choice") == "multiple_choice"
    )
