"""VLearn Self-Quiz — Streamlit interface backed by the slide-only quiz service."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from codebase.app_support import build_context, option_letter, score_answers
from codebase.extract_slides import extract_pages_from_bytes
from codebase.quiz_ai import ChatRequest, OpenRouterClient, QuizRequest


load_dotenv(Path(__file__).with_name(".env"))

st.set_page_config(
    page_title="VLearn Self-Quiz",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
:root { --ink:#172033; --muted:#667085; --line:#e6e8ef; --violet:#6546c7; --soft:#f7f5ff; }
.stApp { background:#fbfbfd; color:var(--ink); }
.block-container { max-width:1000px; padding-top:1.5rem; }
section[data-testid="stSidebar"] { background:#fff; border-right:1px solid var(--line); }
section[data-testid="stSidebar"] .block-container { padding-top:1.25rem; }
h1,h2,h3 { letter-spacing:-.02em; }
.brand { display:flex; align-items:center; gap:10px; padding-bottom:16px; border-bottom:1px solid var(--line); }
.brand-mark { width:34px; height:34px; border-radius:10px; display:grid; place-items:center; color:#fff; background:var(--violet); font-weight:800; }
.brand-title { font-weight:800; font-size:18px; }.brand-sub { color:var(--muted); font-size:12px; }
.step { color:var(--muted); font-size:13px; font-weight:600; margin-bottom:8px; }.step b { color:var(--violet); }
.citation { color:#5b3fc2; font-weight:700; font-size:12px; }
div[data-testid="stVerticalBlockBorderWrapper"] { border-radius:14px; border-color:var(--line); }
@media (max-width:720px) { .block-container { padding:1rem .8rem 2rem; } .stButton button { min-height:42px; } }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

DATA_ROOT = ROOT / "data" / "vlearn-pack" / "slides"
DEFAULT_SLIDES = {
    "Buổi 1 · AI Product Hackathon": DATA_ROOT / "d1-slide-hackathon.pdf",
    "Buổi 2 · AI Product Hackathon": DATA_ROOT / "d2-slide-hackathon.pdf",
}
DIFFICULTIES = ("Khái niệm", "Vận dụng", "Vận dụng cao")


@st.cache_data(show_spinner="Đang đọc slide…")
def load_slide_pages(pdf_bytes: bytes) -> dict[int, str]:
    return extract_pages_from_bytes(pdf_bytes)


def load_default_pages(label: str) -> dict[int, str]:
    path = DEFAULT_SLIDES[label]
    if not path.exists():
        return {}
    return load_slide_pages(path.read_bytes())


def selected_pages(pages: dict[int, str], first: int, last: int) -> dict[int, str]:
    return {page: text for page, text in pages.items() if first <= page <= last and text.strip()}


def render_quiz(quiz: dict) -> None:
    questions = quiz.get("questions", [])
    if not questions:
        st.info(quiz.get("message") or "Chưa tạo được câu hỏi từ phần slide này.")
        return

    answers = st.session_state.setdefault("quiz_answers", {})
    graded = st.session_state.get("quiz_submitted", False)
    st.subheader("Bộ câu hỏi")
    for index, question in enumerate(questions):
        with st.container(border=True):
            st.markdown(f"**Câu {index + 1}. {question['question']}**")
            if question.get("question_type", "multiple_choice") == "essay":
                st.text_area("Câu trả lời của bạn", key=f"essay_{index}")
                if graded:
                    st.info("Câu tự luận: tự đối chiếu phần trả lời với đáp án tham khảo.")
                    st.markdown(f"**Đáp án tham khảo:** {question['sample_answer']}")
                    st.caption(f"Giải thích: {question.get('explanation', '')}")
                    st.markdown(f"<span class='citation'>{question['slide_reference']}</span>", unsafe_allow_html=True)
                continue

            options = question["options"]
            answer = st.radio(
                "Chọn một đáp án",
                options=range(4),
                format_func=lambda option, values=options: f"{option_letter(option)}. {values[option]}",
                key=f"answer_{index}",
                index=None,
            )
            if answer is not None:
                answers[index] = option_letter(answer)
            if graded:
                chosen = answers.get(index)
                correct = question["correct_answer"]
                if chosen == correct:
                    st.success("Đúng.")
                elif chosen is None:
                    st.warning(f"Bạn chưa chọn đáp án. Đáp án đúng là {correct}.")
                else:
                    st.error(f"Chưa đúng. Đáp án đúng là {correct}.")
                st.caption(f"Giải thích: {question.get('explanation', '')}")
                st.markdown(f"<span class='citation'>{question['slide_reference']}</span>", unsafe_allow_html=True)

    multiple_choice = [q for q in questions if q.get("question_type", "multiple_choice") == "multiple_choice"]
    if multiple_choice and st.button("Chấm điểm", type="primary"):
        score = score_answers(questions, answers)
        st.session_state["quiz_submitted"] = True
        st.success(f"Bạn trả lời đúng {score}/{len(multiple_choice)} câu trắc nghiệm.")
        st.rerun()


def create_quiz(context: str, difficulty: str, extra_request: str) -> None:
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        st.error("Thiếu OPENROUTER_API_KEY trong codebase/.env.")
        return
    try:
        instruction = (
            "Tạo 5 câu trắc nghiệm tự luyện từ các slide đã chọn. "
            f"Tất cả câu hỏi phải ở cấp độ: {difficulty}."
        )
        if extra_request.strip():
            instruction += f" Yêu cầu bổ sung của học viên: {extra_request.strip()}"
        quiz = OpenRouterClient(api_key=api_key).generate_quiz(
            QuizRequest(
                slide_context=context,
                question_count=5,
                user_instruction=instruction,
            )
        )
    except (RuntimeError, ValueError) as error:
        st.error(f"Không thể tạo quiz: {error}")
        return
    st.session_state["quiz"] = quiz
    st.session_state["quiz_answers"] = {}
    st.session_state["quiz_submitted"] = False


with st.sidebar:
    st.markdown("<div class='step'><b>1</b> Chọn slide muốn ôn</div>", unsafe_allow_html=True)
    source_name = st.selectbox("Bài giảng", list(DEFAULT_SLIDES))
    pages = load_default_pages(source_name)

    if not pages:
        st.warning("Chưa đọc được nội dung slide có sẵn.")
        first_page = last_page = 1
    else:
        page_numbers = sorted(pages)
        first_page, last_page = st.select_slider(
            "Phạm vi slide",
            options=page_numbers,
            value=(page_numbers[0], page_numbers[-1]),
        )
        st.caption(f"{len(selected_pages(pages, first_page, last_page))} trang có nội dung · {source_name}")

    st.divider()
    st.markdown("<div class='step'><b>2</b> Tạo bộ câu hỏi</div>", unsafe_allow_html=True)
    difficulty = st.radio("Mức độ", DIFFICULTIES, index=1)
    extra_request = st.text_input(
        "Yêu cầu bổ sung (tuỳ chọn)",
        placeholder="Ví dụ: tập trung vào quy trình và tình huống thực tế",
    )
    st.caption("AI dùng cố định nội dung slide và model mặc định để giữ luồng học tập đơn giản.")


st.markdown(
    "<div class='brand'><div class='brand-mark'>V</div><div><div class='brand-title'>VLearn Self-Quiz</div>"
    "<div class='brand-sub'>Ôn tập có căn cứ từ slide</div></div></div>",
    unsafe_allow_html=True,
)

if pages:
    current_pages = selected_pages(pages, first_page, last_page)
    context = build_context(current_pages, first_page, last_page)
else:
    current_pages, context = {}, ""

quiz_tab, chat_tab = st.tabs(["📝 Sinh câu hỏi", "💬 Hỏi đáp"])

with quiz_tab:
    st.title("Ôn đúng phần bạn vừa học")
    st.caption("Chọn một khoảng slide, tạo quiz, rồi kiểm tra lại ngay nguồn của mỗi câu.")
    if st.button("Tạo quiz 5 câu", type="primary", disabled=not bool(context)):
        with st.spinner("Đang tạo quiz từ slide…"):
            create_quiz(context, difficulty, extra_request)

    if quiz := st.session_state.get("quiz"):
        render_quiz(quiz)


with chat_tab:
    st.title("Hỏi về các slide đang chọn")
    st.caption("Nội dung học tập có căn cứ sẽ kèm trang slide; chào hỏi cơ bản không cần trích dẫn.")
    for message in st.session_state.get("chat", []):
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if citations := message.get("citations"):
                st.caption(" · ".join(citations))

    question = st.chat_input("Hỏi về các trang đang chọn…")
    if question:
        history = st.session_state.setdefault("chat", [])
        history.append({"role": "user", "content": question})
        if not context:
            response = {"content": "Hãy chọn ít nhất một trang slide trước khi hỏi.", "citations": []}
        elif not os.getenv("OPENROUTER_API_KEY", ""):
            response = {"content": "Thiếu OPENROUTER_API_KEY trong codebase/.env.", "citations": []}
        else:
            try:
                result = OpenRouterClient().answer(
                    ChatRequest(slide_context=context, question=question),
                    history=history[-6:],
                )
                response = {"content": result["answer"], "citations": result["citations"]}
            except (RuntimeError, ValueError) as error:
                response = {"content": f"Không thể trả lời lúc này: {error}", "citations": []}
        history.append({"role": "assistant", **response})
        st.session_state["chat"] = history
        st.rerun()
