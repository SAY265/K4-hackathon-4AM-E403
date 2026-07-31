import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


class StreamlitUiTests(unittest.TestCase):
    def test_demo_interface_renders_without_errors(self):
        app = AppTest.from_file(
            str(ROOT / "codebase" / "app.py"),
            default_timeout=20,
        ).run()

        self.assertEqual([], list(app.exception))
        self.assertTrue(
            {
                "Giải thích nhanh",
                "Kiểm tra grounding",
                "Thử guardrail",
                "Tạo quiz 5 câu",
            }.issubset({button.label for button in app.button}),
        )
        self.assertEqual(
            ["Hỏi về các trang đang chọn…"],
            [chat_input.placeholder for chat_input in app.chat_input],
        )
        self.assertEqual(
            ["Tải bài giảng từ máy"],
            [uploader.label for uploader in app.get("file_uploader")],
        )


if __name__ == "__main__":
    unittest.main()
