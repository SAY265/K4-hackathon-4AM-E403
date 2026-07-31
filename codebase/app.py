"""Conversational VLearn study assistant with grounded quiz generation."""

from __future__ import annotations

from collections.abc import Callable
import html
import os
from pathlib import Path
from typing import Any

import streamlit as st

from codebase.app_support import (
    build_context,
    is_quiz_request,
    option_letter,
    parse_quiz_composition,
)
from codebase.extract_slides import extract_pages, extract_pages_from_bytes
from codebase.quiz_ai import ChatRequest, OpenRouterClient, QuizRequest


ROOT = Path(__file__).resolve().parents[1]
SLIDES = {
    "Day 1 · AI & LLM Foundation": ROOT
    / "data/vlearn-pack/slides/d1-slide-hackathon.pdf",
    "Day 2 · Xác định bài toán cho AI": ROOT
    / "data/vlearn-pack/slides/d2-slide-hackathon.pdf",
}

WELCOME = {
    "role": "assistant",
    "kind": "text",
    "content": (
        "Chào bạn, mình là **VLearn Study Buddy**. Hãy hỏi mình về phần slide "
        "đang chọn, hoặc nhắn “Tạo quiz cho mình” để tự kiểm tra."
    ),
    "citations": [],
}

DEMO_PROMPTS = [
    ("Giải thích nhanh", "Context window là gì? Giải thích cho người mới học."),
    ("Kiểm tra grounding", "Deadline nộp bài cuối kỳ là ngày nào?"),
    ("Thử guardrail", "Đây là bài thi đang diễn ra, chọn đáp án đúng hộ tôi."),
    ("Tạo quiz 5 câu", "Tạo quiz 5 câu từ các trang đang chọn."),
]


@st.cache_data(show_spinner=False)
def load_pages(pdf_path: str) -> dict[int, str]:
    with Path(pdf_path).open("rb") as pdf_file:
        return extract_pages(pdf_file)


@st.cache_data(show_spinner=False)
def load_uploaded_pages(pdf_bytes: bytes) -> dict[int, str]:
    return extract_pages_from_bytes(pdf_bytes)


def configured_api_key() -> str:
    environment_key = os.getenv("OPENROUTER_API_KEY", "")
    if environment_key:
        return environment_key
    try:
        return st.secrets.get("OPENROUTER_API_KEY", "")
    except FileNotFoundError:
        return ""


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #172033;
            --muted: #64748b;
            --blue: #2563eb;
            --blue-hover: #1d4ed8;
            --blue-soft: #eff6ff;
            --green: #0f766e;
            --green-soft: #ecfdf5;
            --canvas: #f7f9fc;
            --surface: #ffffff;
            --line: #e2e8f0;
        }
        html, body, .stApp {
            background: var(--canvas) !important;
            color: var(--ink) !important;
            font-family: "Segoe UI Variable", "Segoe UI", sans-serif !important;
        }
        .stApp p, .stApp li, .stApp label, .stApp small,
        .stApp [data-testid="stMarkdownContainer"] {
            color: var(--ink) !important;
        }
        .block-container {
            max-width: 980px !important;
            padding-top: 1.6rem !important;
            padding-bottom: 8rem !important;
        }
        h1, h2, h3 {
            color: var(--ink) !important;
            letter-spacing: -.02em;
        }
        .product-header {
            display: flex;
            align-items: center;
            gap: .85rem;
            margin-bottom: .4rem;
        }
        .product-mark {
            display: grid;
            place-items: center;
            width: 2.65rem;
            height: 2.65rem;
            border-radius: 12px;
            background: var(--blue);
            color: #fff;
            font: 800 1.05rem Bahnschrift, sans-serif;
            box-shadow: 0 5px 14px rgba(37,99,235,.22);
        }
        .product-name {
            color: var(--ink);
            font: 700 1.45rem/1.15 Bahnschrift, sans-serif;
            letter-spacing: -.025em;
        }
        .product-tagline {
            color: var(--muted) !important;
            font-size: .91rem;
            margin-top: .15rem;
        }
        .evidence-rail {
            display: flex;
            flex-wrap: wrap;
            gap: .45rem;
            padding: .65rem .75rem;
            border: 1px solid var(--line);
            border-radius: 10px;
            background: var(--surface);
            box-shadow: 0 2px 8px rgba(15,23,42,.04);
            margin: 1rem 0 1.25rem;
        }
        .rail-chip {
            display: inline-flex;
            align-items: center;
            gap: .4rem;
            padding: .32rem .55rem;
            border-radius: 7px;
            background: #f8fafc;
            color: #475569;
            font-size: .78rem;
            font-weight: 600;
        }
        .rail-dot {
            width: .5rem;
            height: .5rem;
            border-radius: 50%;
            background: var(--green);
        }
        .rail-dot.warn { background: #f59e0b; }
        [data-testid="stSidebar"] {
            background: #ffffff !important;
            border-right: 1px solid var(--line);
        }
        [data-testid="stSidebar"] * {
            color: var(--ink) !important;
        }
        [data-testid="stSidebar"] h2 {
            font-size: 1.25rem !important;
            margin-bottom: .4rem !important;
        }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
            color: var(--muted) !important;
        }
        .side-kicker {
            color: var(--blue) !important;
            font-size: .68rem;
            font-weight: 750;
            letter-spacing: .08em;
            text-transform: uppercase;
        }
        .side-status {
            padding: .7rem .75rem;
            background: var(--green-soft);
            border: 1px solid #a7f3d0;
            border-radius: 8px;
            font-size: .84rem;
            line-height: 1.5;
        }
        [data-testid="stFileUploaderDropzone"] {
            background: #f8fafc !important;
            border: 1px dashed #94a3b8 !important;
            border-radius: 10px !important;
        }
        [data-testid="stStatusWidget"] {
            background: var(--blue-soft) !important;
            border: 1px solid #bfdbfe !important;
            border-radius: 10px !important;
        }
        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] [data-baseweb="select"] > div {
            background: #ffffff !important;
            color: var(--ink) !important;
            border-color: #cbd5e1 !important;
        }
        [data-testid="stSidebar"] input {
            -webkit-text-fill-color: var(--ink) !important;
        }
        [data-testid="stSidebar"] svg {
            fill: currentColor !important;
        }
        [data-testid="stSidebar"] [role="slider"] {
            background: var(--blue) !important;
        }
        [data-testid="stChatMessage"] {
            border: 1px solid var(--line);
            background: var(--surface) !important;
            color: var(--ink) !important;
            padding: .85rem 1rem;
            border-radius: 12px;
            box-shadow: 0 2px 7px rgba(15,23,42,.035);
            margin-bottom: .75rem;
        }
        [data-testid="stChatMessage"] * {
            color: var(--ink) !important;
        }
        [data-testid="stChatMessage"]:has(
            [data-testid="chatAvatarIcon-user"]
        ) {
            background: var(--blue-soft) !important;
            border-color: #bfdbfe;
        }
        .citation-tab {
            display: inline-block;
            margin: .45rem .3rem 0 0;
            padding: .24rem .58rem;
            border-radius: 6px;
            background: var(--green-soft);
            color: #065f46;
            font: 650 .76rem "Cascadia Mono", Consolas, monospace;
        }
        .demo-label {
            color: var(--muted) !important;
            font-size: .8rem;
            font-weight: 650;
            margin: .15rem 0 .3rem;
        }
        [data-testid="stHorizontalBlock"] .stButton > button {
            min-height: 2.8rem;
            text-align: left;
            justify-content: flex-start;
        }
        [data-testid="stBottom"] {
            background: linear-gradient(
                180deg,
                rgba(247,249,252,0) 0%,
                var(--canvas) 30%
            ) !important;
        }
        [data-testid="stChatInput"] {
            background: var(--surface) !important;
            border: 1px solid #94a3b8 !important;
            border-radius: 12px !important;
            box-shadow: 0 8px 24px rgba(15,23,42,.1) !important;
        }
        [data-testid="stChatInput"] textarea {
            background: var(--surface) !important;
            color: var(--ink) !important;
            caret-color: var(--blue) !important;
            font-size: 1rem !important;
            -webkit-text-fill-color: var(--ink) !important;
        }
        [data-testid="stChatInput"] textarea::placeholder {
            color: #64748b !important;
            opacity: 1 !important;
        }
        [data-testid="stChatInput"] button {
            color: var(--blue) !important;
        }
        [data-testid="stChatInput"] button svg {
            fill: var(--blue) !important;
            color: var(--blue) !important;
        }
        input:focus, textarea:focus, button:focus-visible,
        [data-baseweb="select"] > div:focus-within {
            outline: 3px solid rgba(37,99,235,.28) !important;
            outline-offset: 2px !important;
        }
        .stButton > button {
            border-radius: 8px;
            border: 1px solid var(--line);
            background: var(--surface);
            color: #334155 !important;
            font-weight: 600;
            transition: border-color .14s ease, background .14s ease;
        }
        .stButton > button:hover {
            border-color: #93c5fd;
            background: var(--blue-soft);
            color: var(--blue-hover) !important;
        }
        .stButton > button[kind="primary"] {
            background: var(--blue);
            color: white !important;
            border-color: var(--blue);
        }
        textarea, input {
            font-family: "Segoe UI", sans-serif !important;
            color: var(--ink) !important;
        }
        @media (prefers-reduced-motion: reduce) {
            * { transition: none !important; scroll-behavior: auto !important; }
        }
        @media (max-width: 720px) {
            .block-container { padding-top: 1rem !important; }
            [data-testid="stChatMessage"] { padding: .6rem .75rem; }
            .evidence-rail { gap: .35rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [WELCOME.copy()]
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None


def sidebar() -> tuple[str, dict[int, str], tuple[int, int], str]:
    st.sidebar.markdown('<p class="side-kicker">Thiết lập phiên học</p>', unsafe_allow_html=True)
    st.sidebar.markdown("## Bàn học")
    uploaded_pdf = st.sidebar.file_uploader(
        "Tải bài giảng từ máy",
        type=["pdf"],
        help="PDF tối đa 20 MB. File chỉ được xử lý trong phiên hiện tại.",
    )
    if uploaded_pdf is not None:
        lesson, pages = uploaded_lesson(uploaded_pdf)
    else:
        lesson = st.sidebar.selectbox("Hoặc dùng bài giảng mẫu", list(SLIDES))
        pages = load_pages(str(SLIDES[lesson]))
    page_range = st.sidebar.slider(
        "Trang AI được phép đọc",
        min_value=1,
        max_value=len(pages),
        value=(1, min(5, len(pages))),
    )
    entered_key = st.sidebar.text_input(
        "OpenRouter API key",
        type="password",
        help="Không được ghi vào repo; key chỉ dùng trong phiên này.",
    )
    api_key = entered_key or configured_api_key()
    key_status = "AI đã sẵn sàng" if api_key else "Cần API key để hỏi AI"
    st.sidebar.markdown(
        f'<div class="side-status"><b>{key_status}</b><br>'
        f'AI chỉ đọc trang {page_range[0]}–{page_range[1]} và phải dẫn nguồn.</div>',
        unsafe_allow_html=True,
    )
    with st.sidebar.expander("Xem context AI sẽ đọc"):
        context_preview = build_context(pages, page_range[0], page_range[1])
        st.caption(context_preview[:1200] or "Các trang này chưa có văn bản để đọc.")
    if st.sidebar.button("Xoá hội thoại", use_container_width=True):
        st.session_state.messages = [WELCOME.copy()]
        st.rerun()
    st.sidebar.caption("Key chỉ được gửi tới OpenRouter và không xuất hiện trong lịch sử chat.")
    return lesson, pages, page_range, api_key


def uploaded_lesson(uploaded_pdf: Any) -> tuple[str, dict[int, str]]:
    pdf_bytes = uploaded_pdf.getvalue()
    if len(pdf_bytes) > 20 * 1024 * 1024:
        st.sidebar.error("PDF vượt quá giới hạn 20 MB.")
        st.stop()
    try:
        pages = load_uploaded_pages(pdf_bytes)
    except (ValueError, RuntimeError, OSError) as error:
        st.sidebar.error(f"Không thể đọc PDF: {error}")
        st.stop()
    if not pages or not any(text.strip() for text in pages.values()):
        st.sidebar.error(
            "PDF không có văn bản có thể đọc. "
            "Hãy dùng PDF có text thay vì bản scan ảnh."
        )
        st.stop()
    return f"PDF · {uploaded_pdf.name}", pages


def render_header(
    lesson: str, page_range: tuple[int, int], api_key_configured: bool
) -> None:
    st.markdown(
        '<div class="product-header">'
        '<div class="product-mark">VL</div>'
        '<div>'
        '<div class="product-name">VLearn Study Buddy</div>'
        '<div class="product-tagline">'
        'Hỏi bài, kiểm tra nguồn và luyện tập ngay trên slide.'
        '</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    safe_lesson = html.escape(lesson)
    status_text = "AI sẵn sàng" if api_key_configured else "Chưa có API key"
    status_class = "" if api_key_configured else " warn"
    st.markdown(
        '<div class="evidence-rail">'
        f'<span class="rail-chip"><i class="rail-dot"></i>{safe_lesson}</span>'
        f'<span class="rail-chip"><i class="rail-dot"></i>Trang '
        f'{page_range[0]:02d}–{page_range[1]:02d}</span>'
        f'<span class="rail-chip"><i class="rail-dot{status_class}"></i>'
        f'{status_text}</span>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_demo_prompts() -> str | None:
    if len(st.session_state.messages) > 1:
        return None
    st.markdown(
        '<p class="demo-label">Bắt đầu nhanh — chọn một tình huống để thử</p>',
        unsafe_allow_html=True,
    )
    columns = st.columns(2)
    selected_prompt: str | None = None
    for index, (label, prompt) in enumerate(DEMO_PROMPTS):
        with columns[index % 2]:
            if st.button(label, key=f"demo-{index}", use_container_width=True):
                selected_prompt = prompt
    return selected_prompt


def render_messages() -> None:
    for message_index, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            if message.get("kind") == "quiz":
                render_quiz(message_index, message["quiz"])
                continue
            st.markdown(message["content"])
            render_citations(message.get("citations", []))


def render_citations(citations: list[str]) -> None:
    if not citations:
        return
    tabs = "".join(
        f'<span class="citation-tab">{citation}</span>' for citation in citations
    )
    st.markdown(tabs, unsafe_allow_html=True)


def render_quiz(message_index: int, quiz: dict[str, Any]) -> None:
    st.markdown("### Bộ câu hỏi luyện tập")
    answers: dict[int, str] = {}
    for question_index, question in enumerate(quiz["questions"]):
        question_type = question.get("question_type", "multiple_choice")
        type_label = "Trắc nghiệm" if question_type == "multiple_choice" else "Tự luận"
        st.caption(type_label)
        st.markdown(f"**Câu {question_index + 1}. {question['question']}**")
        if question_type == "essay":
            st.text_area(
                "Câu trả lời của bạn",
                key=f"essay-{message_index}-{question_index}",
                placeholder="Viết câu trả lời trước khi xem đáp án gợi ý…",
            )
            continue
        choice = st.radio(
            "Chọn một đáp án",
            question["options"],
            index=None,
            key=f"quiz-{message_index}-{question_index}",
            label_visibility="collapsed",
        )
        if choice is not None:
            answers[question_index] = option_letter(question["options"].index(choice))
    if st.button(
        "Chấm bài và xem đáp án gợi ý",
        key=f"grade-{message_index}",
        type="primary",
        use_container_width=True,
    ):
        show_quiz_result(quiz["questions"], answers)


def show_quiz_result(
    questions: list[dict[str, Any]], answers: dict[int, str]
) -> None:
    multiple_choice_questions = [
        (index, question)
        for index, question in enumerate(questions)
        if question.get("question_type", "multiple_choice") == "multiple_choice"
    ]
    score = sum(
        answers.get(index) == question["correct_answer"]
        for index, question in multiple_choice_questions
    )
    if multiple_choice_questions:
        st.success(
            f"Bạn đúng {score}/{len(multiple_choice_questions)} câu trắc nghiệm."
        )
    for index, question in enumerate(questions):
        is_essay = question.get("question_type") == "essay"
        answer_label = (
            "đáp án gợi ý" if is_essay else f"đáp án {question['correct_answer']}"
        )
        with st.expander(f"Câu {index + 1} · {answer_label}"):
            if is_essay:
                st.write(question["sample_answer"])
            st.caption(question["explanation"])
            render_citations([question["slide_reference"]])


def recent_chat_history() -> list[dict[str, str]]:
    history: list[dict[str, str]] = []
    for message in st.session_state.messages:
        if message.get("kind") != "text" or not message.get("content"):
            continue
        history.append({"role": message["role"], "content": message["content"]})
    return history[-6:]


def handle_message(
    prompt: str,
    api_key: str,
    pages: dict[int, str],
    page_range: tuple[int, int],
    progress: Callable[[str], None],
) -> bool:
    progress(
        f"Đang đọc trang {page_range[0]}–{page_range[1]} "
        "và chuẩn bị ngữ cảnh…"
    )
    context = build_context(pages, page_range[0], page_range[1])
    if not api_key:
        append_error("Hãy nhập OpenRouter API key ở thanh bên để mình trả lời.")
        return False
    try:
        progress("Đang xác định loại yêu cầu và kiểm tra phạm vi…")
        if is_quiz_request(prompt):
            composition = parse_quiz_composition(prompt)
            if not 1 <= composition.total_count <= 10:
                append_error(
                    "Mỗi lần có thể tạo từ 1 đến 10 câu. "
                    "Hãy giảm số câu rồi thử lại."
                )
                return False
            progress(
                f"Đang tạo {composition.multiple_choice_count} câu trắc nghiệm "
                f"và {composition.essay_count} câu tự luận…"
            )
            quiz = OpenRouterClient(api_key).generate_quiz(
                QuizRequest(
                    context,
                    question_count=composition.total_count,
                    user_instruction=prompt,
                    multiple_choice_count=composition.multiple_choice_count,
                    essay_count=composition.essay_count,
                )
            )
            st.session_state.messages.append(
                {"role": "assistant", "kind": "quiz", "quiz": quiz}
            )
            return True
        progress("Đang tạo câu trả lời và kiểm tra dẫn nguồn…")
        response = OpenRouterClient(api_key).answer(
            ChatRequest(context, prompt),
            history=recent_chat_history(),
        )
        st.session_state.messages.append(
            {
                "role": "assistant",
                "kind": "text",
                "content": response["answer"],
                "citations": response["citations"],
            }
        )
        return True
    except (RuntimeError, ValueError, KeyError) as error:
        append_error(f"Không thể xử lý câu hỏi: {error}")
        return False


def queue_prompt(prompt: str) -> None:
    st.session_state.messages.append(
        {"role": "user", "kind": "text", "content": prompt, "citations": []}
    )
    st.session_state.pending_prompt = prompt


def process_pending_prompt(
    api_key: str,
    pages: dict[int, str],
    page_range: tuple[int, int],
) -> None:
    prompt = st.session_state.pending_prompt
    if not prompt:
        return
    succeeded = False
    with st.chat_message("assistant"):
        with st.status("Bot đang suy nghĩ…", expanded=True) as status:
            succeeded = handle_message(
                prompt,
                api_key,
                pages,
                page_range,
                status.write,
            )
            final_label = "Đã hoàn tất" if succeeded else "Cần bạn kiểm tra lại"
            final_state = "complete" if succeeded else "error"
            status.update(label=final_label, state=final_state, expanded=False)
    st.session_state.pending_prompt = None
    st.rerun()


def append_error(message: str) -> None:
    st.session_state.messages.append(
        {
            "role": "assistant",
            "kind": "text",
            "content": message,
            "citations": [],
        }
    )


def main() -> None:
    st.set_page_config(
        page_title="VLearn Study Buddy",
        page_icon="✦",
        layout="centered",
        initial_sidebar_state="expanded",
    )
    apply_theme()
    initialize_state()
    lesson, pages, page_range, api_key = sidebar()
    render_header(lesson, page_range, bool(api_key))
    demo_prompt = render_demo_prompts()
    render_messages()
    is_processing = bool(st.session_state.pending_prompt)
    prompt = st.chat_input(
        "Hỏi về các trang đang chọn…",
        max_chars=500,
        disabled=is_processing,
    )
    prompt = demo_prompt or prompt
    if prompt:
        queue_prompt(prompt)
        st.rerun()
    process_pending_prompt(api_key, pages, page_range)


if __name__ == "__main__":
    main()
