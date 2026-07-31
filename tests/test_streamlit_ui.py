import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


def _app():
    """App đã bỏ qua hộp thoại hướng dẫn — trạng thái người dùng thường gặp."""
    app = AppTest.from_file(str(ROOT / "codebase" / "app.py"), default_timeout=20).run()
    app.button(key="onboarding_start").click().run()
    # Lượt chạy vừa rồi vẫn còn phần tử của hộp thoại; chạy thêm một lượt cho sạch.
    return app.run()


class StreamlitUiTests(unittest.TestCase):
    def test_demo_interface_renders_without_errors(self):
        app = _app()

        self.assertEqual([], list(app.exception))
        self.assertEqual(
            ["Ôn tập", "Hỏi đáp", "Tiến độ", "Hướng dẫn", "Tạo quiz"],
            [button.label for button in app.button],
        )
        self.assertEqual([], list(app.get("file_uploader")))
        self.assertEqual(["Bài giảng"], [selectbox.label for selectbox in app.selectbox])
        self.assertEqual(
            ["Khái niệm", "Vận dụng", "Vận dụng cao"],
            list(app.radio[0].options),
        )
        self.assertEqual(
            ["Yêu cầu bổ sung (tuỳ chọn)"],
            [text_input.label for text_input in app.text_input],
        )
        self.assertEqual(["Số câu hỏi"], [slider.label for slider in app.slider])

    def test_onboarding_dialog_opens_on_first_visit(self):
        app = AppTest.from_file(str(ROOT / "codebase" / "app.py"), default_timeout=20).run()

        self.assertIn("Bắt đầu", [button.label for button in app.button])
        app.button(key="onboarding_start").click().run()
        self.assertTrue(app.session_state["onboarded"])

    def test_chat_page_hides_quiz_only_controls(self):
        app = _app()
        app.button(key="nav_chat").click().run()

        self.assertEqual([], list(app.exception))
        self.assertEqual(
            ["Hỏi về các trang đang chọn…"],
            [chat_input.placeholder for chat_input in app.chat_input],
        )
        self.assertEqual([], [slider.label for slider in app.slider])
        self.assertNotIn("Tạo quiz", [button.label for button in app.button])

    def test_progress_page_hides_the_config_column(self):
        app = _app()
        app.button(key="nav_progress").click().run()

        self.assertEqual([], list(app.exception))
        self.assertEqual([], [selectbox.label for selectbox in app.selectbox])
        self.assertTrue(
            any("Chưa có lượt ôn nào" in block.value for block in app.markdown)
        )


if __name__ == "__main__":
    unittest.main()
