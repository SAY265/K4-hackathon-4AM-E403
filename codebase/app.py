"""VLearn Study Buddy — Streamlit interface backed by the slide-only quiz service.

Giao diện bám theo bản thiết kế `VLearn Study Buddy.dc.html` (design system
"modernist" trong `_ds/`): thanh nav trên cùng, cột trái 2 bước cấu hình, ba
trang Ôn tập · Hỏi đáp · Tiến độ.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from html import escape
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
    page_title="VLearn Study Buddy",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Token và class lấy nguyên từ design system trong `_ds/` + phần bo góc 10px mà
# bản thiết kế override trong helmet. Đổi màu thì đổi ở đây, đừng rải rác dưới.
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;800&display=swap');
:root {
  --color-bg:#f3f2f2; --color-surface:#eae9e9; --color-text:#201e1d;
  --color-accent:#2f6fed; --color-accent-600:#1f56c4; --color-accent-100:#eef4ff;
  --color-accent-700:#163f94;
  --color-divider:color-mix(in srgb,#201e1d 40%,transparent);
  --color-neutral-700:#605d5d;
  --color-success:oklch(58% 0.15 145); --color-success-tint:oklch(94% 0.045 145);
  --color-danger:oklch(58% 0.19 25); --color-danger-tint:oklch(94% 0.04 25);
  --shadow-sm:0 1px 2px color-mix(in srgb,#2d2b2b 14%,transparent);
  --shadow-lg:0 12px 32px color-mix(in srgb,#2d2b2b 22%,transparent);
  --font:"Archivo",system-ui,sans-serif;
}
html, body, [class*="css"], .stApp { font-family:var(--font); }
.stApp { background:var(--color-bg); color:var(--color-text); }
.block-container { max-width:1240px; padding:0 2rem 2.5rem; }
section[data-testid="stSidebar"] { display:none; }
#MainMenu, footer, header[data-testid="stHeader"] { visibility:hidden; height:0; }

h1,h2,h3,h4 { font-family:var(--font); font-weight:800!important; letter-spacing:-.015em; line-height:1.12; color:var(--color-text); }
h1 { font-size:28px!important; margin-bottom:4px!important; }
.lede { color:var(--color-neutral-700); font-size:14px; margin:0 0 4px; }

/* — thanh nav — */
.nav-shell { border-bottom:2px solid var(--color-divider); margin-bottom:4px; }
.brand { display:flex; align-items:center; gap:10px; }
.brand-mark { width:34px; height:34px; border-radius:10px; display:grid; place-items:center;
  color:var(--color-bg); background:var(--color-accent); font-weight:800; font-size:16px; flex:none; }
.brand-title { font-weight:800; font-size:16px; line-height:1.2; }
.brand-sub { color:var(--color-neutral-700); font-size:11px; }

div[class*="st-key-nav_"] button {
  background:transparent!important; border:none!important; padding:6px 0!important;
  font-size:14px!important; font-weight:400!important; color:var(--color-text)!important;
  box-shadow:none!important; width:auto!important;
}
div[class*="st-key-nav_"] button:hover { color:var(--color-accent)!important; }
div[class*="st-key-nav_quiz_on"] button, div[class*="st-key-nav_chat_on"] button,
div[class*="st-key-nav_progress_on"] button, div[class*="st-key-nav_help"] button {
  color:var(--color-accent)!important; font-weight:800!important; }

/* — cột cấu hình bên trái — */
.side-col { border-right:2px solid var(--color-divider); padding-right:24px; }
.step { color:var(--color-neutral-700); font-size:12px; font-weight:700; margin:0 0 8px; }
.step b { color:var(--color-accent); margin-right:6px; }
.range-ends { display:flex; justify-content:space-between; font-size:12px;
  color:var(--color-accent-700); font-weight:700; margin:-6px 0 2px; }
.summary { font-size:11px; color:var(--color-neutral-700); margin:2px 0 10px; }
.hr { height:2px; border:0; margin:16px 0; background:var(--color-divider); }
.side-note { font-size:12px; color:var(--color-neutral-700); }

/* — form — */
.stSelectbox label, .stRadio label, .stTextInput label, .stTextArea label, .stSlider label {
  font-size:12px!important; color:color-mix(in srgb,var(--color-text) 70%,transparent)!important; }
.stSelectbox div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
  background:var(--color-surface); border-radius:10px; border:1px solid var(--color-divider); font-size:14px; }
.stSlider [data-baseweb="slider"] div[role="slider"] { border-color:var(--color-accent); }

/* — nút — */
.stButton > button {
  border-radius:10px; font-family:var(--font); font-weight:800; font-size:14px;
  border:1px solid var(--color-divider); background:transparent; color:var(--color-text); }
.stButton > button:hover { border-color:var(--color-accent); color:var(--color-accent); }
.stButton > button[kind="primary"] { background:var(--color-accent); color:var(--color-bg); border-color:var(--color-accent); }
.stButton > button[kind="primary"]:hover { background:var(--color-accent-600); color:var(--color-bg); }
div[class*="st-key-generate"] button { justify-content:flex-start; text-align:left; }

/* — thẻ — */
/* Mọi st.container(border=True) trong app này đều là thẻ câu hỏi. */
div[data-testid="stVerticalBlockBorderWrapper"] {
  background:var(--color-surface); border:0; border-radius:10px; box-shadow:var(--shadow-sm); }
.card { display:flex; flex-direction:column; gap:8px; padding:12px 16px;
  background:var(--color-surface); border-radius:10px; box-shadow:var(--shadow-sm); }
.card-kicker { font-size:10px; letter-spacing:.1em; text-transform:uppercase; color:var(--color-accent); }
.card-title { font-family:var(--font); font-weight:800; font-size:17px; line-height:1.2; }
.card-body { font-size:13px; opacity:.8; margin:0; }
.score-banner { display:flex; align-items:center; justify-content:space-between; gap:16px;
  border:2px solid var(--color-text); background:var(--color-surface); border-radius:10px;
  padding:12px 16px; box-shadow:var(--shadow-sm); }
.score-banner .card-title { font-size:16px; }

/* — phương án trắc nghiệm — */
div[class*="st-key-opt_"] button {
  width:100%; justify-content:flex-start; text-align:left; font-weight:400!important;
  background:var(--color-surface); border:1px solid var(--color-divider); border-radius:10px;
  padding:10px 12px; margin-bottom:2px; }
div[class*="st-key-opt_"] button:hover { border-color:var(--color-accent); background:var(--color-accent-100); }
.option-row { display:flex; align-items:center; gap:10px; padding:10px 12px; margin-bottom:8px;
  border:1px solid var(--color-divider); border-radius:10px; background:var(--color-surface);
  color:var(--color-text); font-size:14px; }
.option-row .letter { font-weight:800; font-size:13px; width:18px; flex:none; }
.option-row .mark { margin-left:auto; font-weight:800; font-size:15px; }
.option-row.correct { border:2px solid var(--color-success); background:var(--color-success-tint); color:var(--color-success); }
.option-row.wrong { border-color:var(--color-danger); background:var(--color-danger-tint); color:var(--color-danger); }
.option-row.muted { opacity:.55; }
.result-line { font-size:13px; font-weight:600; }
.explain { font-size:13px; color:var(--color-neutral-700); }
.tag-outline { display:inline-flex; align-items:center; font-size:11px; padding:3px 10px;
  border-radius:999px; border:1px solid var(--color-accent); color:var(--color-accent); }

/* — hỏi đáp — */
.msg { display:flex; flex-direction:column; margin-bottom:14px; }
.msg.user { align-items:flex-end; }
.msg.bot { align-items:flex-start; }
.bubble { max-width:80%; padding:10px 14px; font-size:14px; line-height:1.5; border-radius:14px; }
.msg.user .bubble { background:var(--color-text); color:var(--color-bg); }
.msg.bot .bubble { background:var(--color-surface); border:1px solid var(--color-divider); }
.cites { display:flex; gap:6px; flex-wrap:wrap; margin-top:6px; }
div[data-testid="stChatInput"] { background:var(--color-surface); border-radius:10px; border:1px solid var(--color-divider); }

/* — tiến độ — */
.stat-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:2px; background:var(--color-divider);
  border:2px solid var(--color-divider); margin-bottom:24px; }
.stat-grid .card { background:var(--color-bg); border-radius:0; box-shadow:none; }
.stat-grid .card-title { font-size:28px; }
table.table { width:100%; border-collapse:collapse; font-size:14px; }
table.table th { text-align:left; font-size:11px; letter-spacing:.08em; text-transform:uppercase;
  color:color-mix(in srgb,var(--color-text) 60%,transparent); padding:8px; border-bottom:2px solid var(--color-divider); }
table.table td { padding:8px; border-bottom:1px solid var(--color-divider); }

@media (max-width:720px) {
  .block-container { padding:0 1rem 2rem; }
  .side-col { border-right:0; padding-right:0; border-bottom:2px solid var(--color-divider); padding-bottom:16px; }
  .stat-grid { grid-template-columns:1fr; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

DATA_ROOT = ROOT / "data" / "vlearn-pack" / "slides"
DEFAULT_SLIDES = {
    "Buổi 1 · AI Product Hackathon": DATA_ROOT / "d1-slide-hackathon.pdf",
    "Buổi 2 · AI Product Hackathon": DATA_ROOT / "d2-slide-hackathon.pdf",
}
DIFFICULTIES = ("Khái niệm", "Vận dụng", "Vận dụng cao")
TABS = (("quiz", "Ôn tập"), ("chat", "Hỏi đáp"), ("progress", "Tiến độ"))


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


def mcq_indexes(questions: list[dict]) -> list[int]:
    return [
        index
        for index, question in enumerate(questions)
        if question.get("question_type", "multiple_choice") == "multiple_choice"
    ]


# --------------------------------------------------------------------------
# Onboarding — bản thiết kế mở hộp thoại 3 bước ngay lần đầu vào app
# --------------------------------------------------------------------------


@st.dialog("Chào mừng đến với VLearn")
def onboarding_dialog() -> None:
    st.markdown(
        "<div style='font-size:14px;opacity:.85;display:flex;flex-direction:column;gap:10px;'>"
        "<div><b style='color:var(--color-accent);'>1.</b> Chọn bài giảng và phạm vi trang bạn vừa học.</div>"
        "<div><b style='color:var(--color-accent);'>2.</b> Chọn số câu hỏi rồi tạo quiz, hoặc mở tab "
        "Hỏi đáp để hỏi trực tiếp.</div>"
        "<div><b style='color:var(--color-accent);'>3.</b> Xem đúng/sai và trang slide nguồn ngay khi "
        "chọn đáp án — không sửa lại được.</div></div>",
        unsafe_allow_html=True,
    )
    if st.button("Bắt đầu", type="primary", key="onboarding_start"):
        st.session_state["onboarded"] = True
        st.rerun()


# --------------------------------------------------------------------------
# Thanh nav
# --------------------------------------------------------------------------

tab = st.session_state.setdefault("tab", "quiz")

st.markdown("<div class='nav-shell'>", unsafe_allow_html=True)
nav_cols = st.columns([3.4, 0.9, 1.0, 0.9, 3.4, 1.2], vertical_alignment="center")
nav_cols[0].markdown(
    "<div class='brand'><div class='brand-mark'>V</div><div>"
    "<div class='brand-title'>VLearn Study Buddy</div>"
    "<div class='brand-sub'>Ôn tập có căn cứ từ slide</div></div></div>",
    unsafe_allow_html=True,
)
for column, (key, label) in zip(nav_cols[1:4], TABS):
    # Key đổi theo trạng thái để CSS tô đậm mục đang mở — nút không giữ state nên đổi key vô hại.
    if column.button(label, key=f"nav_{key}{'_on' if tab == key else ''}"):
        st.session_state["tab"] = key
        st.rerun()
if nav_cols[5].button("Hướng dẫn", key="nav_help"):
    st.session_state["onboarded"] = False
    st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state.get("onboarded", False):
    onboarding_dialog()


# --------------------------------------------------------------------------
# Bố cục: cột cấu hình + nội dung (trang Tiến độ chiếm trọn chiều ngang)
# --------------------------------------------------------------------------

if tab == "progress":
    side_col, content_col = None, st.container()
else:
    side_col, content_col = st.columns([0.28, 0.72], gap="large")

context = ""
current_pages: dict[int, str] = {}
source_name = list(DEFAULT_SLIDES)[0]
difficulty = DIFFICULTIES[1]
question_count = 3
extra_request = ""

if side_col is not None:
    with side_col:
        st.markdown("<div class='side-col'>", unsafe_allow_html=True)
        st.markdown("<div class='step'><b>1</b>Chọn slide muốn ôn</div>", unsafe_allow_html=True)
        source_name = st.selectbox("Bài giảng", list(DEFAULT_SLIDES))
        pages = load_default_pages(source_name)

        if not pages:
            st.warning("Chưa đọc được nội dung slide có sẵn.")
            first_page = last_page = 1
        else:
            page_numbers = sorted(pages)
            st.markdown(
                f"<div class='step' style='margin-bottom:2px;'>Phạm vi slide</div>"
                f"<div class='range-ends'><span>{page_numbers[0]}</span>"
                f"<span>{page_numbers[-1]}</span></div>",
                unsafe_allow_html=True,
            )
            first_page, last_page = st.select_slider(
                "Phạm vi slide",
                options=page_numbers,
                value=(page_numbers[0], page_numbers[-1]),
                label_visibility="collapsed",
            )
            current_pages = selected_pages(pages, first_page, last_page)
            st.markdown(
                f"<div class='summary'>{len(current_pages)} trang có nội dung · {escape(source_name)}</div>",
                unsafe_allow_html=True,
            )
            context = build_context(current_pages, first_page, last_page)

        st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
        st.markdown("<div class='step'><b>2</b>Tạo bộ câu hỏi</div>", unsafe_allow_html=True)
        difficulty = st.radio("Mức độ", DIFFICULTIES, index=1, label_visibility="collapsed")

        if tab == "quiz":
            question_count = st.slider("Số câu hỏi", min_value=1, max_value=10, value=3)
        extra_request = st.text_input(
            "Yêu cầu bổ sung (tuỳ chọn)",
            placeholder="Ví dụ: tập trung vào quy trình và tình huống thực tế",
        )

        if tab == "quiz":
            generate = st.button(
                "Tạo quiz",
                type="primary",
                use_container_width=True,
                disabled=not bool(context),
                key="generate",
            )
        else:
            generate = False
            st.markdown(
                "<div class='side-note'>Nội dung chat sẽ dựa trên đúng phạm vi trang này.</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
else:
    generate = False


# --------------------------------------------------------------------------
# Tạo quiz
# --------------------------------------------------------------------------


def create_quiz(context: str, question_count: int, difficulty: str, extra_request: str) -> None:
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        st.error("Thiếu OPENROUTER_API_KEY trong codebase/.env.")
        return
    try:
        instruction = (
            f"Tạo {question_count} câu trắc nghiệm tự luyện từ các slide đã chọn. "
            f"Tất cả câu hỏi phải ở cấp độ: {difficulty}."
        )
        if extra_request.strip():
            instruction += f" Yêu cầu bổ sung của học viên: {extra_request.strip()}"
        quiz = OpenRouterClient(api_key=api_key).generate_quiz(
            QuizRequest(
                slide_context=context,
                question_count=question_count,
                user_instruction=instruction,
            )
        )
    except (RuntimeError, ValueError) as error:
        st.error(f"Không thể tạo quiz: {error}")
        return

    st.session_state["quiz"] = quiz
    st.session_state["quiz_answers"] = {}
    st.session_state["essay_revealed"] = {}

    # Lịch sử của phiên này — nguồn số liệu cho trang Tiến độ.
    history = st.session_state.setdefault("history", [])
    history.append(
        {
            "at": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "deck": source_name,
            "difficulty": difficulty,
            "correct": 0,
            "total": len(mcq_indexes(quiz.get("questions", []))),
        }
    )
    st.session_state["history_index"] = len(history) - 1


def sync_history_score() -> None:
    """Ghi lại điểm của bộ quiz đang làm sau mỗi lần chọn đáp án."""
    quiz = st.session_state.get("quiz")
    index = st.session_state.get("history_index")
    history = st.session_state.get("history", [])
    if not quiz or index is None or index >= len(history):
        return
    history[index]["correct"] = score_answers(
        quiz.get("questions", []), st.session_state.get("quiz_answers", {})
    )


if generate:
    with st.spinner("Đang tạo quiz từ slide…"):
        create_quiz(context, question_count, difficulty, extra_request)


# --------------------------------------------------------------------------
# Trang Ôn tập
# --------------------------------------------------------------------------


def render_question(index: int, question: dict) -> None:
    answers = st.session_state.setdefault("quiz_answers", {})
    is_essay = question.get("question_type", "multiple_choice") == "essay"

    with st.container(border=True):
        st.markdown(
            f"<div class='card-kicker'>Câu {index + 1} · {'Tự luận' if is_essay else 'Trắc nghiệm'}</div>"
            f"<div class='card-title'>{escape(question['question'])}</div>",
            unsafe_allow_html=True,
        )

        if is_essay:
            st.text_area("Câu trả lời của bạn", key=f"essay_{index}", label_visibility="collapsed",
                         placeholder="Nhập câu trả lời của bạn")
            revealed = st.session_state.setdefault("essay_revealed", {})
            if not revealed.get(index):
                if st.button("Xem đáp án tham khảo", key=f"reveal_{index}"):
                    revealed[index] = True
                    st.rerun()
            else:
                st.markdown(
                    f"<div style='font-size:13px;'><b>Đáp án tham khảo:</b> "
                    f"{escape(question['sample_answer'])}</div>"
                    f"<div class='explain'>Giải thích: {escape(question.get('explanation', ''))}</div>"
                    f"<span class='tag-outline'>{escape(question['slide_reference'])}</span>",
                    unsafe_allow_html=True,
                )
            return

        options = question["options"]
        chosen = answers.get(index)
        correct = question["correct_answer"]

        if chosen is None:
            # Chưa chọn: mỗi phương án là một nút. Chọn xong là khoá, không sửa lại.
            for option_index, option in enumerate(options):
                letter = option_letter(option_index)
                if st.button(f"{letter}.  {option}", key=f"opt_{index}_{option_index}",
                             use_container_width=True):
                    answers[index] = letter
                    sync_history_score()
                    st.rerun()
            return

        for option_index, option in enumerate(options):
            letter = option_letter(option_index)
            if letter == correct:
                state, mark = "correct", "✓"
            elif letter == chosen:
                state, mark = "wrong", "✕"
            else:
                state, mark = "muted", ""
            st.markdown(
                f"<div class='option-row {state}'><span class='letter'>{letter}</span>"
                f"<span style='flex:1;'>{escape(option)}</span><span class='mark'>{mark}</span></div>",
                unsafe_allow_html=True,
            )

        result = "Đúng." if chosen == correct else f"Chưa đúng. Đáp án đúng là {correct}."
        st.markdown(
            f"<div class='result-line'>{result}</div>"
            f"<div class='explain'>Giải thích: {escape(question.get('explanation', ''))}</div>"
            f"<span class='tag-outline'>{escape(question['slide_reference'])}</span>",
            unsafe_allow_html=True,
        )


def render_quiz_page() -> None:
    st.markdown("<h1>Ôn đúng phần bạn vừa học</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='lede'>Chọn phạm vi slide bên trái, tạo quiz, rồi xem đúng/sai ngay khi chọn "
        "đáp án — không đổi lại được sau khi chọn.</p>",
        unsafe_allow_html=True,
    )

    quiz = st.session_state.get("quiz")
    if not quiz:
        st.markdown(
            "<div class='card' style='padding:32px;'><div class='card-title'>Chưa có quiz nào</div>"
            "<div class='card-body'>Chọn phạm vi slide và mức độ ở bên trái, sau đó bấm "
            "&quot;Tạo quiz&quot;.</div></div>",
            unsafe_allow_html=True,
        )
        return

    questions = quiz.get("questions", [])
    if not questions:
        st.info(quiz.get("message") or "Chưa tạo được câu hỏi từ phần slide này.")
        return

    answers = st.session_state.setdefault("quiz_answers", {})
    mcq = mcq_indexes(questions)
    if mcq and all(index in answers for index in mcq):
        correct = score_answers(questions, answers)
        banner, action = st.columns([3, 1], vertical_alignment="center")
        banner.markdown(
            f"<div class='score-banner'><div class='card-title'>Kết quả: {correct}/{len(mcq)} "
            "câu trắc nghiệm đúng</div></div>",
            unsafe_allow_html=True,
        )
        if action.button("Tạo bộ khác", key="regenerate", use_container_width=True):
            with st.spinner("Đang tạo quiz từ slide…"):
                create_quiz(context, question_count, difficulty, extra_request)
            st.rerun()

    for index, question in enumerate(questions):
        render_question(index, question)


# --------------------------------------------------------------------------
# Trang Hỏi đáp
# --------------------------------------------------------------------------


def render_chat_page() -> None:
    st.markdown("<h1>Hỏi về các slide đang chọn</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='lede'>Nội dung học tập có căn cứ sẽ kèm trang slide; chào hỏi cơ bản "
        "không cần trích dẫn.</p>",
        unsafe_allow_html=True,
    )

    history = st.session_state.setdefault("chat", [])
    if not history:
        st.markdown(
            "<div class='msg bot'><div class='bubble'>Chào bạn! Chọn phạm vi slide bên trái "
            "rồi đặt câu hỏi nhé.</div></div>",
            unsafe_allow_html=True,
        )
    for message in history:
        role = "user" if message["role"] == "user" else "bot"
        cites = "".join(
            f"<span class='tag-outline'>{escape(c)}</span>" for c in message.get("citations", [])
        )
        st.markdown(
            f"<div class='msg {role}'><div class='bubble'>{escape(message['content'])}</div>"
            + (f"<div class='cites'>{cites}</div>" if cites else "")
            + "</div>",
            unsafe_allow_html=True,
        )

    question = st.chat_input("Hỏi về các trang đang chọn…")
    if not question:
        return

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


# --------------------------------------------------------------------------
# Trang Tiến độ — số liệu của phiên đang chạy, không bịa lịch sử
# --------------------------------------------------------------------------


def render_progress_page() -> None:
    st.markdown("<h1>Tiến độ học tập</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='lede' style='margin-bottom:20px;'>Theo dõi các bộ quiz đã làm trong phiên này. "
        "Đóng trình duyệt là số liệu được làm mới — app không lưu tiến độ giữa các phiên.</p>",
        unsafe_allow_html=True,
    )

    history = st.session_state.get("history", [])
    graded = [entry for entry in history if entry["total"]]
    total_quiz = len(history)
    answered = sum(entry["correct"] for entry in graded)
    possible = sum(entry["total"] for entry in graded)
    # Trung bình số câu đúng mỗi bộ, trên số câu trung bình của một bộ.
    average = (
        f"{answered / len(graded):.1f}/{round(possible / len(graded))}" if graded else "—"
    )

    st.markdown(
        "<div class='stat-grid'>"
        f"<div class='card'><div class='card-kicker'>Tổng số quiz</div>"
        f"<div class='card-title'>{total_quiz}</div></div>"
        f"<div class='card'><div class='card-kicker'>Điểm trung bình</div>"
        f"<div class='card-title'>{average}</div></div>"
        f"<div class='card'><div class='card-kicker'>Câu đúng / đã làm</div>"
        f"<div class='card-title'>{answered}/{possible}</div></div>"
        "</div>",
        unsafe_allow_html=True,
    )

    if not history:
        st.markdown(
            "<div class='card' style='padding:32px;'><div class='card-title'>Chưa có lượt ôn nào</div>"
            "<div class='card-body'>Mở tab Ôn tập, tạo một bộ quiz rồi quay lại đây.</div></div>",
            unsafe_allow_html=True,
        )
        return

    rows = "".join(
        f"<tr><td>{escape(e['at'])}</td><td>{escape(e['deck'])}</td>"
        f"<td>{escape(e['difficulty'])}</td><td>{e['correct']}/{e['total']}</td></tr>"
        for e in reversed(history)
    )
    st.markdown(
        "<table class='table'><thead><tr><th>Thời điểm</th><th>Bài giảng</th>"
        f"<th>Mức độ</th><th>Điểm</th></tr></thead><tbody>{rows}</tbody></table>",
        unsafe_allow_html=True,
    )


with content_col:
    if tab == "quiz":
        render_quiz_page()
    elif tab == "chat":
        render_chat_page()
    else:
        render_progress_page()
