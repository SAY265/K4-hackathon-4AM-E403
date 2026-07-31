import unittest

from codebase.app_support import (
    build_context,
    is_quiz_request,
    option_letter,
    parse_quiz_composition,
    score_answers,
)


class AppSupportTests(unittest.TestCase):
    def test_build_context_selects_requested_page_range(self):
        pages = {1: "Nội dung một", 2: "Nội dung hai", 3: "Nội dung ba"}

        context = build_context(pages, first_page=2, last_page=3)

        self.assertEqual(
            "[Slide trang 2] Nội dung hai\n\n[Slide trang 3] Nội dung ba",
            context,
        )

    def test_score_answers_counts_correct_choices(self):
        questions = [
            {"correct_answer": "B"},
            {"correct_answer": "A"},
            {"correct_answer": "D"},
        ]

        score = score_answers(questions, {0: "B", 1: "C", 2: "D"})

        self.assertEqual(2, score)

    def test_option_letter_maps_zero_based_index(self):
        self.assertEqual("C", option_letter(2))

    def test_detects_quiz_request_in_chat(self):
        self.assertTrue(is_quiz_request("Tạo cho mình 5 câu trắc nghiệm nhé"))
        self.assertFalse(is_quiz_request("Giải thích context window là gì"))

    def test_parses_mixed_quiz_composition(self):
        composition = parse_quiz_composition(
            "Tạo 1 bộ đề gồm 4 câu trắc nghiệm + 5 câu tự luận, kèm đáp án"
        )

        self.assertEqual(4, composition.multiple_choice_count)
        self.assertEqual(5, composition.essay_count)
        self.assertEqual(9, composition.total_count)

    def test_defaults_to_five_multiple_choice_questions(self):
        composition = parse_quiz_composition("Tạo quiz cho mình")

        self.assertEqual(5, composition.multiple_choice_count)
        self.assertEqual(0, composition.essay_count)


if __name__ == "__main__":
    unittest.main()
