import json
from pathlib import Path
import unittest

from codebase.quiz_ai import (
    ChatRequest,
    QuizRequest,
    SYSTEM_PROMPT,
    parse_chat_response,
    parse_quiz_response,
)
from codebase.extract_slides import extract_pages_from_bytes, format_page


class QuizResponseTests(unittest.TestCase):
    def test_system_prompt_hides_correct_answer_patterns(self):
        self.assertIn("randomize the correct-answer position", SYSTEM_PROMPT)
        self.assertIn("vary option lengths naturally", SYSTEM_PROMPT)
        self.assertIn("must not reveal the correct answer", SYSTEM_PROMPT)

    def test_system_prompt_defines_three_cognitive_levels(self):
        self.assertIn("Khái niệm", SYSTEM_PROMPT)
        self.assertIn("Vận dụng", SYSTEM_PROMPT)
        self.assertIn("Vận dụng cao", SYSTEM_PROMPT)
        self.assertIn("tình huống mới", SYSTEM_PROMPT)
        self.assertIn("nhiều bước", SYSTEM_PROMPT)

    def test_accepts_grounded_chat_response(self):
        payload = json.dumps(
            {
                "status": "ok",
                "answer": "Context là lượng nội dung model nhìn thấy.",
                "citations": ["[Slide trang 3]"],
            }
        )

        result = parse_chat_response(payload, allowed_pages={3})

        self.assertEqual("ok", result["status"])
        self.assertEqual(["[Slide trang 3]"], result["citations"])

    def test_chat_rejects_citation_outside_context(self):
        payload = json.dumps(
            {
                "status": "ok",
                "answer": "Nội dung.",
                "citations": ["[Slide trang 99]"],
            }
        )

        with self.assertRaisesRegex(ValueError, "outside supplied context"):
            parse_chat_response(payload, allowed_pages={3})

    def test_chat_request_requires_a_question(self):
        with self.assertRaisesRegex(ValueError, "question must not be empty"):
            ChatRequest(slide_context="[Slide trang 1] Nội dung", question=" ")

    def test_formats_extracted_slide_for_grounded_citation(self):
        self.assertEqual(
            "[Slide trang 3] Token là đơn vị mô hình xử lý.",
            format_page(3, " Token là đơn vị\nmô hình xử lý. "),
        )

    def test_extracts_uploaded_pdf_from_memory(self):
        pdf_path = (
            Path(__file__).resolve().parents[1]
            / "data"
            / "vlearn-pack"
            / "slides"
            / "d1-slide-hackathon.pdf"
        )

        pages = extract_pages_from_bytes(pdf_path.read_bytes())

        self.assertGreater(len(pages), 1)
        self.assertIn(1, pages)

    def test_rejects_invalid_uploaded_pdf(self):
        with self.assertRaisesRegex(ValueError, "Cannot read uploaded PDF"):
            extract_pages_from_bytes(b"not a PDF")

    def test_accepts_grounded_quiz_response(self):
        payload = json.dumps(
            {
                "status": "ok",
                "message": "",
                "questions": [
                    {
                        "question": "Double Diamond có bao nhiêu pha?",
                        "options": ["2", "3", "4", "5"],
                        "correct_answer": "C",
                        "explanation": "Mô hình gồm bốn pha mở rộng và hội tụ.",
                        "slide_reference": "[Slide trang 12]",
                        "confidence": 0.95,
                    }
                ],
            }
        )

        result = parse_quiz_response(payload, allowed_pages={12})

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, len(result["questions"]))

    def test_rejects_reference_to_page_outside_context(self):
        payload = json.dumps(
            {
                "status": "ok",
                "message": "",
                "questions": [
                    {
                        "question": "Câu hỏi?",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": "A",
                        "explanation": "Giải thích.",
                        "slide_reference": "[Slide trang 99]",
                        "confidence": 0.9,
                    }
                ],
            }
        )

        with self.assertRaisesRegex(ValueError, "outside supplied context"):
            parse_quiz_response(payload, allowed_pages={12})

    def test_rejects_wrong_number_of_questions(self):
        payload = json.dumps(
            {"status": "ok", "message": "", "questions": []}
        )

        with self.assertRaisesRegex(ValueError, "expected 2 questions"):
            parse_quiz_response(payload, allowed_pages={12}, expected_count=2)

    def test_quiz_request_rejects_invalid_question_count(self):
        with self.assertRaisesRegex(ValueError, "between 1 and 10"):
            QuizRequest(slide_context="[Slide trang 1] Nội dung", question_count=11)

    def test_accepts_mixed_multiple_choice_and_essay_quiz(self):
        payload = json.dumps(
            {
                "status": "ok",
                "message": "",
                "questions": [
                    {
                        "question_type": "multiple_choice",
                        "question": "Context window là gì?",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": "A",
                        "explanation": "Là lượng nội dung model nhìn thấy.",
                        "slide_reference": "[Slide trang 3]",
                        "confidence": 0.9,
                    },
                    {
                        "question_type": "essay",
                        "question": "Giải thích giới hạn của context window.",
                        "sample_answer": "Context có dung lượng hữu hạn.",
                        "explanation": "Đáp án cần nêu tính hữu hạn.",
                        "slide_reference": "[Slide trang 3]",
                        "confidence": 0.9,
                    },
                ],
            }
        )

        result = parse_quiz_response(
            payload,
            allowed_pages={3},
            expected_count=2,
            expected_multiple_choice_count=1,
            expected_essay_count=1,
        )

        self.assertEqual("essay", result["questions"][1]["question_type"])


if __name__ == "__main__":
    unittest.main()
