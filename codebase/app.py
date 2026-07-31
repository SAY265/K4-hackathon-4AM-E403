"""VLearn Study Buddy — Streamlit interface backed by the slide-only quiz service.

Giao diện: phong cách hiện đại, tinh gọn, bo góc mềm — nav nổi trên nền sáng,
panel cấu hình dạng thẻ, câu hỏi dạng card, và ba trang Ôn tập · Hỏi đáp · Tiến độ.
Toàn bộ luồng dữ liệu và lời gọi API giữ nguyên như trước.
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

# Hệ thiết kế: một bảng token ở đây, phần dưới chỉ dùng lại class — đổi màu hay
# độ bo góc thì sửa đúng một chỗ này.
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

:root {
  --bg:#f5f6fb;
  --surface:#ffffff;
  --surface-2:#f3f5fa;
  --text:#171a23;
  --text-2:#4b5266;
  --muted:#8c93a6;
  --line:#e9ebf4;
  --line-strong:#cdd3e4;

  --primary:#5457e5;
  --primary-600:#4447cd;
  --primary-tint:#eeefff;

  --success:#0f9a5c;
  --success-tint:#e8f8f0;
  --danger:#dc4b52;
  --danger-tint:#fdeeef;

  --r-sm:12px; --r-md:16px; --r-lg:20px; --r-xl:26px; --r-full:999px;
  --sh-xs:0 1px 2px rgba(23,26,35,.05);
  --sh-sm:0 4px 14px -6px rgba(23,26,35,.14);
  --sh-md:0 18px 40px -22px rgba(23,26,35,.35);

  --font:'Inter',system-ui,-apple-system,sans-serif;
  --display:'Plus Jakarta Sans',var(--font);
}

html, body, [class*="css"], .stApp { font-family:var(--font); }
.stApp { background:var(--bg); color:var(--text); }
.block-container { max-width:1200px; padding:0 2rem 3rem; }
section[data-testid="stSidebar"] { display:none; }
#MainMenu, footer, header[data-testid="stHeader"] { visibility:hidden; height:0; }
h1,h2,h3,h4 { font-family:var(--display); font-weight:800!important; letter-spacing:-.02em; color:var(--text); }
h1 { font-size:30px!important; line-height:1.2; margin:0 0 6px!important; }
.lede { color:var(--text-2); font-size:14.5px; line-height:1.6; margin:0 0 22px; max-width:62ch; }
::selection { background:var(--primary-tint); }

/* ───────── thanh nav nổi ───────── */
div[class*="st-key-navbar"] {
  background:var(--surface); border:1px solid var(--line); border-radius:var(--r-xl);
  box-shadow:var(--sh-sm); padding:10px 18px; margin:10px 0 26px;
}
.brand { display:flex; align-items:center; gap:11px; }
.brand-mark {
  width:38px; height:38px; border-radius:13px; display:grid; place-items:center; flex:none;
  color:#fff; font-family:var(--display); font-weight:800; font-size:17px;
  background:linear-gradient(140deg,#6d6ff0,#4a4dd6); box-shadow:0 6px 14px -6px rgba(84,87,229,.9);
}
.brand-title { font-family:var(--display); font-weight:800; font-size:15.5px; line-height:1.25; letter-spacing:-.01em; }
.brand-sub { color:var(--muted); font-size:11.5px; }

div[class*="st-key-nav_"] button {
  width:100%!important; border:none!important; box-shadow:none!important;
  background:transparent!important; color:var(--text-2)!important;
  font-weight:600!important; font-size:14px!important;
  padding:9px 6px!important; border-radius:var(--r-full)!important;
}
div[class*="st-key-nav_"] button:hover { background:var(--surface-2)!important; color:var(--text)!important; }
div[class*="st-key-nav_quiz_on"] button,
div[class*="st-key-nav_chat_on"] button,
div[class*="st-key-nav_progress_on"] button {
  background:var(--primary-tint)!important; color:var(--primary)!important; font-weight:700!important;
}
div[class*="st-key-nav_help"] button {
  border:1px solid var(--line)!important; color:var(--text-2)!important; background:var(--surface)!important;
}
div[class*="st-key-nav_help"] button:hover { border-color:var(--primary)!important; color:var(--primary)!important; background:var(--surface)!important; }

/* ───────── panel cấu hình ───────── */
div[class*="st-key-sidepanel"] {
  background:var(--surface); border:1px solid var(--line); border-radius:var(--r-xl);
  box-shadow:var(--sh-xs); padding:22px 20px 24px;
}
.step { display:flex; align-items:center; gap:9px; font-size:13px; font-weight:700;
  color:var(--text); margin:0 0 14px; font-family:var(--display); }
.step-num { width:22px; height:22px; border-radius:8px; flex:none; display:grid; place-items:center;
  background:var(--primary-tint); color:var(--primary); font-size:12px; font-weight:800; }
.range-ends { display:flex; justify-content:space-between; margin:-2px 0 -6px; }
.range-ends span { font-size:11.5px; font-weight:700; color:var(--primary);
  background:var(--primary-tint); border-radius:var(--r-full); padding:2px 10px; }
.summary { font-size:12px; color:var(--muted); margin:10px 0 2px; }
.soft-rule { height:1px; background:var(--line); margin:22px 0; border:0; }
.side-note { font-size:12.5px; color:var(--text-2); line-height:1.6;
  background:var(--surface-2); border-radius:var(--r-md); padding:12px 14px; }

/* ───────── form ───────── */
.stSelectbox label, .stRadio label, .stTextInput label, .stTextArea label, .stSlider label {
  font-size:12.5px!important; font-weight:600!important; color:var(--text-2)!important; }
.stSelectbox div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
  background:var(--surface-2)!important; border:1px solid transparent!important;
  border-radius:var(--r-sm)!important; font-size:14px!important; color:var(--text)!important; }
.stSelectbox div[data-baseweb="select"] > div:hover, .stTextInput input:hover, .stTextArea textarea:hover {
  border-color:var(--line)!important; }
.stTextInput input:focus, .stTextArea textarea:focus { border-color:var(--primary)!important; background:var(--surface)!important; }
div[data-baseweb="popover"] li { font-size:14px; }
.stSlider [data-baseweb="slider"] div[role="slider"] {
  background:var(--surface)!important; border:3px solid var(--primary)!important; box-shadow:var(--sh-xs)!important; }

/* mức độ: radio dựng lại thành hàng chip mềm */
div[role="radiogroup"] { gap:7px!important; display:flex; flex-direction:column; }
div[role="radiogroup"] > label {
  width:100%; margin:0!important; padding:10px 13px; border-radius:var(--r-sm);
  background:var(--surface-2); border:1px solid transparent; transition:.14s ease; }
div[role="radiogroup"] > label:hover { border-color:var(--line); background:var(--surface); }
div[role="radiogroup"] > label:has(input:checked) { background:var(--primary-tint); border-color:var(--primary); }
div[role="radiogroup"] > label:has(input:checked) div[data-testid="stMarkdownContainer"] p { color:var(--primary); font-weight:600; }
div[role="radiogroup"] div[data-testid="stMarkdownContainer"] p { font-size:14px!important; color:var(--text-2); }

/* ───────── nút ───────── */
.stButton > button {
  border-radius:var(--r-sm); font-family:var(--font); font-weight:600; font-size:14px;
  border:1px solid var(--line); background:var(--surface); color:var(--text);
  padding:9px 16px; transition:.14s ease; box-shadow:var(--sh-xs); }
.stButton > button:hover { border-color:var(--primary); color:var(--primary); transform:translateY(-1px); }
.stButton > button[kind="primary"] {
  background:linear-gradient(140deg,#6467ee,#4a4dd6); color:#fff; border:none;
  font-weight:700; padding:12px 18px; box-shadow:0 10px 22px -12px rgba(84,87,229,.95); }
.stButton > button[kind="primary"]:hover { filter:brightness(1.05); color:#fff; }
.stButton > button:disabled, .stButton > button[kind="primary"]:disabled {
  background:var(--surface-2); color:var(--muted); box-shadow:none; transform:none; border:1px solid var(--line); }

/* ───────── thẻ câu hỏi ───────── */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.card-kicker) {
  background:var(--surface); border:1px solid var(--line); border-radius:var(--r-lg);
  box-shadow:var(--sh-xs); padding:6px 8px; margin-bottom:16px; }
.card-kicker { display:inline-flex; align-items:center; font-size:11px; font-weight:700;
  letter-spacing:.06em; text-transform:uppercase; color:var(--primary);
  background:var(--primary-tint); border-radius:var(--r-full); padding:4px 11px; margin-bottom:12px; }
.card-title { font-family:var(--display); font-weight:700; font-size:16.5px; line-height:1.45;
  color:var(--text); margin-bottom:14px; }

/* phương án chưa chọn: nút chiếm cả dòng, chữ căn trái như hàng đã khoá */
div[class*="st-key-opt_"] button {
  width:100%!important; justify-content:flex-start!important; text-align:left!important;
  font-weight:500!important; color:var(--text)!important;
  background:var(--surface)!important; border:1.5px solid var(--line-strong)!important;
  border-radius:var(--r-md); padding:13px 16px!important;
  height:auto!important; min-height:0!important; box-shadow:none;
  white-space:normal!important; line-height:1.5; }
/* Nhãn nút bị Streamlit bọc trong một flex container tự căn giữa — ép về bên trái. */
div[class*="st-key-opt_"] button > div,
div[class*="st-key-opt_"] button div[data-testid="stMarkdownContainer"] {
  width:100%!important; display:block!important;
  justify-content:flex-start!important; text-align:left!important; }
div[class*="st-key-opt_"] button p {
  width:100%!important; margin:0!important; text-align:left!important;
  white-space:normal!important; overflow-wrap:anywhere; }
div[class*="st-key-opt_"] button:hover {
  background:var(--primary-tint)!important; border-color:var(--primary)!important;
  color:var(--text)!important; box-shadow:var(--sh-xs); transform:none; }

/* phương án đã khoá */
.option-row { display:flex; align-items:center; gap:12px; padding:13px 16px; margin-bottom:8px;
  border:1.5px solid var(--line-strong); border-radius:var(--r-md); background:var(--surface);
  color:var(--text-2); font-size:14px; line-height:1.5; }
.option-row .letter { width:26px; height:26px; flex:none; border-radius:9px; display:grid; place-items:center;
  font-size:12px; font-weight:700; background:var(--surface-2); color:var(--text-2); }
.option-row .mark { margin-left:auto; font-weight:700; font-size:15px; }
.option-row.correct { background:var(--success-tint); border-color:var(--success); color:var(--success); }
.option-row.correct .letter { background:var(--success); color:#fff; }
.option-row.wrong { background:var(--danger-tint); border-color:var(--danger); color:var(--danger); }
.option-row.wrong .letter { background:var(--danger); color:#fff; }
.option-row.muted { opacity:.7; background:var(--surface-2); }

.verdict { display:inline-flex; align-items:center; font-size:13px; font-weight:700;
  border-radius:var(--r-full); padding:5px 13px; margin:6px 0 10px; }
.verdict.ok { background:var(--success-tint); color:var(--success); }
.verdict.no { background:var(--danger-tint); color:var(--danger); }
.explain { font-size:13.5px; color:var(--text-2); line-height:1.65;
  background:var(--surface-2); border-radius:var(--r-md); padding:12px 14px; margin-bottom:10px; }
.explain b { color:var(--text); }
.cite { display:inline-flex; align-items:center; gap:6px; font-size:11.5px; font-weight:600;
  color:var(--primary); background:var(--primary-tint); border-radius:var(--r-full); padding:5px 12px; }

/* ───────── banner điểm ───────── */
.score-banner { display:flex; align-items:center; border-radius:var(--r-lg); padding:18px 22px;
  background:linear-gradient(135deg,#5f62ea,#4548cf); box-shadow:0 16px 34px -20px rgba(84,87,229,1); }
.score-banner .label { font-size:12px; font-weight:600; color:rgba(255,255,255,.75); letter-spacing:.04em; text-transform:uppercase; }
.score-banner .value { font-family:var(--display); font-weight:800; font-size:22px; color:#fff; line-height:1.25; }

/* ───────── trạng thái rỗng ───────── */
.empty { border:1.5px dashed var(--line); border-radius:var(--r-xl); background:var(--surface);
  padding:44px 32px; text-align:center; }
.empty .icon { width:52px; height:52px; border-radius:18px; margin:0 auto 16px; display:grid; place-items:center;
  background:var(--primary-tint); font-size:22px; }
.empty .title { font-family:var(--display); font-weight:800; font-size:17px; margin-bottom:6px; }
.empty .body { font-size:13.5px; color:var(--muted); max-width:44ch; margin:0 auto; line-height:1.65; }

/* ───────── hỏi đáp ───────── */
.msg { display:flex; flex-direction:column; margin-bottom:16px; }
.msg.user { align-items:flex-end; }
.msg.bot { align-items:flex-start; }
.bubble { max-width:78%; padding:13px 17px; font-size:14px; line-height:1.65; border-radius:var(--r-lg); }
.msg.user .bubble { background:linear-gradient(140deg,#6467ee,#4a4dd6); color:#fff;
  border-bottom-right-radius:7px; box-shadow:0 10px 24px -16px rgba(84,87,229,1); }
.msg.bot .bubble { background:var(--surface); border:1px solid var(--line); color:var(--text);
  border-bottom-left-radius:7px; box-shadow:var(--sh-xs); }
.cites { display:flex; gap:6px; flex-wrap:wrap; margin-top:8px; }
div[data-testid="stChatInput"] { background:var(--surface); border-radius:var(--r-lg);
  border:1px solid var(--line); box-shadow:var(--sh-xs); }
div[data-testid="stChatInput"] textarea { font-size:14px; }

/* ───────── tiến độ ───────── */
.stat-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-bottom:26px; }
.stat { background:var(--surface); border:1px solid var(--line); border-radius:var(--r-lg);
  padding:20px 22px; box-shadow:var(--sh-xs); }
.stat .k { font-size:11.5px; font-weight:600; letter-spacing:.05em; text-transform:uppercase; color:var(--muted); margin-bottom:8px; }
.stat .v { font-family:var(--display); font-weight:800; font-size:30px; line-height:1.1; letter-spacing:-.02em; }
.table-card { background:var(--surface); border:1px solid var(--line); border-radius:var(--r-lg);
  box-shadow:var(--sh-xs); overflow:hidden; }
table.table { width:100%; border-collapse:collapse; font-size:13.5px; }
table.table th { text-align:left; font-size:11px; font-weight:600; letter-spacing:.06em; text-transform:uppercase;
  color:var(--muted); padding:13px 20px; background:var(--surface-2); }
table.table td { padding:14px 20px; border-top:1px solid var(--line); color:var(--text-2); }
table.table td:first-child { color:var(--text); font-weight:500; }
table.table tbody tr:hover td { background:var(--surface-2); }

/* ───────── hộp thoại & alert ───────── */
div[data-testid="stDialog"] div[role="dialog"] { border-radius:var(--r-xl); box-shadow:var(--sh-md); border:1px solid var(--line); }
div[data-testid="stAlert"] { border-radius:var(--r-md); border:1px solid var(--line); }
.dialog-steps { display:flex; flex-direction:column; gap:12px; margin-bottom:4px; }
.dialog-steps > div { display:flex; gap:12px; align-items:flex-start; font-size:14px; color:var(--text-2); line-height:1.6; }
.dialog-steps .n { width:24px; height:24px; flex:none; border-radius:9px; display:grid; place-items:center;
  background:var(--primary-tint); color:var(--primary); font-weight:800; font-size:12px; }

@media (max-width:900px) {
  .block-container { padding:0 1rem 2rem; }
  .stat-grid { grid-template-columns:1fr; }
  .bubble { max-width:92%; }
  div[class*="st-key-navbar"] { border-radius:var(--r-lg); }
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
# Onboarding — hộp thoại ba bước ở lần vào đầu tiên
# --------------------------------------------------------------------------


@st.dialog("Chào mừng đến với VLearn")
def onboarding_dialog() -> None:
    st.markdown(
        "<div class='dialog-steps'>"
        "<div><span class='n'>1</span><span>Chọn bài giảng và phạm vi trang bạn vừa học.</span></div>"
        "<div><span class='n'>2</span><span>Chọn số câu hỏi rồi tạo quiz, hoặc mở tab Hỏi đáp "
        "để hỏi trực tiếp.</span></div>"
        "<div><span class='n'>3</span><span>Xem đúng/sai và trang slide nguồn ngay khi chọn "
        "đáp án — không sửa lại được.</span></div>"
        "</div>",
        unsafe_allow_html=True,
    )
    if st.button("Bắt đầu", type="primary", key="onboarding_start"):
        st.session_state["onboarded"] = True
        st.rerun()


# --------------------------------------------------------------------------
# Thanh nav
# --------------------------------------------------------------------------

tab = st.session_state.setdefault("tab", "quiz")

with st.container(key="navbar"):
    nav_cols = st.columns([3.3, 0.95, 1.0, 0.95, 3.1, 1.25], vertical_alignment="center")
    nav_cols[0].markdown(
        "<div class='brand'><div class='brand-mark'>V</div><div>"
        "<div class='brand-title'>VLearn Study Buddy</div>"
        "<div class='brand-sub'>Ôn tập có căn cứ từ slide</div></div></div>",
        unsafe_allow_html=True,
    )
    for column, (key, label) in zip(nav_cols[1:4], TABS):
        # Key đổi theo trạng thái để CSS tô mục đang mở — nút không giữ state nên đổi key vô hại.
        if column.button(label, key=f"nav_{key}{'_on' if tab == key else ''}"):
            st.session_state["tab"] = key
            st.rerun()
    if nav_cols[5].button("Hướng dẫn", key="nav_help", use_container_width=True):
        st.session_state["onboarded"] = False
        st.rerun()

if not st.session_state.get("onboarded", False):
    onboarding_dialog()


# --------------------------------------------------------------------------
# Bố cục: panel cấu hình + nội dung (trang Tiến độ chiếm trọn chiều ngang)
# --------------------------------------------------------------------------

if tab == "progress":
    side_col, content_col = None, st.container()
else:
    side_col, content_col = st.columns([0.3, 0.7], gap="large")

context = ""
current_pages: dict[int, str] = {}
source_name = list(DEFAULT_SLIDES)[0]
difficulty = DIFFICULTIES[1]
question_count = 3
extra_request = ""

if side_col is not None:
    with side_col, st.container(key="sidepanel"):
        st.markdown(
            "<div class='step'><span class='step-num'>1</span>Chọn slide muốn ôn</div>",
            unsafe_allow_html=True,
        )
        source_name = st.selectbox("Bài giảng", list(DEFAULT_SLIDES))
        pages = load_default_pages(source_name)

        if not pages:
            st.warning("Chưa đọc được nội dung slide có sẵn.")
            first_page = last_page = 1
        else:
            page_numbers = sorted(pages)
            st.markdown(
                "<div style='font-size:12.5px;font-weight:600;color:var(--text-2);"
                "margin:16px 0 6px;'>Phạm vi slide</div>"
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
                f"<div class='summary'>{len(current_pages)} trang có nội dung · "
                f"{escape(source_name)}</div>",
                unsafe_allow_html=True,
            )
            context = build_context(current_pages, first_page, last_page)

        st.markdown("<div class='soft-rule'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='step'><span class='step-num'>2</span>Tạo bộ câu hỏi</div>",
            unsafe_allow_html=True,
        )
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
            st.text_area(
                "Câu trả lời của bạn",
                key=f"essay_{index}",
                label_visibility="collapsed",
                placeholder="Nhập câu trả lời của bạn",
            )
            revealed = st.session_state.setdefault("essay_revealed", {})
            if not revealed.get(index):
                if st.button("Xem đáp án tham khảo", key=f"reveal_{index}"):
                    revealed[index] = True
                    st.rerun()
            else:
                st.markdown(
                    f"<div class='explain'><b>Đáp án tham khảo:</b> "
                    f"{escape(question['sample_answer'])}</div>"
                    f"<div class='explain'>{escape(question.get('explanation', ''))}</div>"
                    f"<span class='cite'>{escape(question['slide_reference'])}</span>",
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
                if st.button(
                    f"{letter}.  {option}",
                    key=f"opt_{index}_{option_index}",
                    use_container_width=True,
                ):
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

        is_correct = chosen == correct
        verdict = "Đúng." if is_correct else f"Chưa đúng. Đáp án đúng là {correct}."
        verdict_class = "ok" if is_correct else "no"
        st.markdown(
            f"<div class='verdict {verdict_class}'>{verdict}</div>"
            f"<div class='explain'><b>Giải thích:</b> {escape(question.get('explanation', ''))}</div>"
            f"<span class='cite'>{escape(question['slide_reference'])}</span>",
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
            "<div class='empty'><div class='icon'>📝</div>"
            "<div class='title'>Chưa có quiz nào</div>"
            "<div class='body'>Chọn phạm vi slide và mức độ ở bên trái, sau đó bấm "
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
        banner, action = st.columns([3, 1.15], vertical_alignment="center")
        banner.markdown(
            "<div class='score-banner'><div>"
            "<div class='label'>Kết quả</div>"
            f"<div class='value'>{correct}/{len(mcq)} câu trắc nghiệm đúng</div>"
            "</div></div>",
            unsafe_allow_html=True,
        )
        if action.button("Tạo bộ khác", key="regenerate", use_container_width=True):
            with st.spinner("Đang tạo quiz từ slide…"):
                create_quiz(context, question_count, difficulty, extra_request)
            st.rerun()
        st.write("")

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
            f"<span class='cite'>{escape(c)}</span>" for c in message.get("citations", [])
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
        "<p class='lede'>Theo dõi các bộ quiz đã làm trong phiên này. Đóng trình duyệt là số liệu "
        "được làm mới — app không lưu tiến độ giữa các phiên.</p>",
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
        f"<div class='stat'><div class='k'>Tổng số quiz</div><div class='v'>{total_quiz}</div></div>"
        f"<div class='stat'><div class='k'>Điểm trung bình</div><div class='v'>{average}</div></div>"
        f"<div class='stat'><div class='k'>Câu đúng / đã làm</div>"
        f"<div class='v'>{answered}/{possible}</div></div>"
        "</div>",
        unsafe_allow_html=True,
    )

    if not history:
        st.markdown(
            "<div class='empty'><div class='icon'>📊</div>"
            "<div class='title'>Chưa có lượt ôn nào</div>"
            "<div class='body'>Mở tab Ôn tập, tạo một bộ quiz rồi quay lại đây.</div></div>",
            unsafe_allow_html=True,
        )
        return

    rows = "".join(
        f"<tr><td>{escape(e['at'])}</td><td>{escape(e['deck'])}</td>"
        f"<td>{escape(e['difficulty'])}</td><td>{e['correct']}/{e['total']}</td></tr>"
        for e in reversed(history)
    )
    st.markdown(
        "<div class='table-card'><table class='table'><thead><tr><th>Thời điểm</th>"
        "<th>Bài giảng</th><th>Mức độ</th><th>Điểm</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div>",
        unsafe_allow_html=True,
    )


with content_col:
    if tab == "quiz":
        render_quiz_page()
    elif tab == "chat":
        render_chat_page()
    else:
        render_progress_page()
