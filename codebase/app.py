"""VLearn Student Self-Quiz Generator — demo web (Streamlit).

Lát cắt: học viên chọn một phần slide/transcript của buổi học · AI sinh câu hỏi
trắc nghiệm tự luyện kèm trích dẫn [Trang N] · học viên biết mình hổng chỗ nào
và quay lại đúng trang đó.

Giao diện dựng theo thiết kế trong `VLearn Self-Quiz (offline).html` — cùng bảng
màu, cùng bố cục, nhưng chạy trên lời gọi AI thật của `quiz_engine.py`.

Chạy:  streamlit run codebase/app.py
"""

from __future__ import annotations

import os
from html import escape
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

import quiz_engine as qe

load_dotenv(Path(__file__).with_name(".env"))

st.set_page_config(
    page_title="VLearn Self-Quiz",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL_CHOICES = [
    "openai/gpt-4o-mini",  # rẻ nhất — mặc định cho tài khoản OpenRouter ít credit
    "anthropic/claude-sonnet-5",
    "anthropic/claude-opus-5",
]

DIFFICULTIES = ["nhớ lại khái niệm", "hiểu và áp dụng", "phân tích tình huống"]

KIND_LABEL = {"slide": "Slide", "transcript": "Transcript"}

LETTERS = "ABCD"

# Trần ngữ cảnh: chọn cả chục tài liệu một lúc thì prompt phình ra vài trăm nghìn
# ký tự, OpenRouter trả 402 trước khi kịp sinh câu nào. Chặn sớm, nói rõ lý do.
MAX_CONTEXT_CHARS = 60_000

PATH_META = {
    "happy": ("✅ Happy path", "happy"),
    "low_confidence": ("⚠️ Thiếu căn cứ", "low"),
    "refused": ("⛔ Từ chối", "bad"),
    "error": ("⛔ Lỗi", "bad"),
}

BADGE_TEXT = {
    "exact": "✅ khớp nguyên văn",
    "partial": "🟡 khớp một phần",
    "missing": "❌ không tìm thấy dẫn chứng",
}


# --------------------------------------------------------------------------
# Thiết kế — bảng màu và kiểu chữ lấy từ bản mock offline
# --------------------------------------------------------------------------

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@700;800&display=swap');

:root {
  --bg: oklch(98% 0.005 90);
  --surface: oklch(100% 0 0);
  --surface-alt: oklch(99.5% 0.003 90);
  --surface-muted: oklch(97% 0.005 90);
  --border: oklch(91% 0.008 90);
  --text: oklch(22% 0.01 90);
  --text-soft: oklch(40% 0.01 90);
  --text-muted: oklch(50% 0.01 90);
  --accent: oklch(52% 0.15 290);
  --accent-dark: oklch(45% 0.15 290);
  --accent-soft: oklch(96% 0.03 290);
  --ok: oklch(45% 0.14 145);
  --sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --display: 'Manrope', var(--sans);
}

html, body, [class*="css"], .stApp { font-family: var(--sans); }
.stApp { background: var(--bg); color: var(--text); }
.block-container { padding-top: 1.6rem; max-width: 980px; }

h1, h2, h3 { font-family: var(--display) !important; font-weight: 800 !important; }

/* Thanh bên */
section[data-testid="stSidebar"] { background: var(--surface-alt); border-right: 1px solid var(--border); }
section[data-testid="stSidebar"] .block-container { padding-top: 1.2rem; }
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .55rem; }

/* Nút */
.stButton > button {
  border-radius: 12px;
  font-family: var(--sans);
  font-weight: 500;
  border: 1px solid oklch(88% 0.01 90);
  transition: border-color .12s, color .12s;
}
.stButton > button:hover { border-color: var(--accent); color: var(--accent-dark); }
.stButton > button[kind="primary"] {
  background: var(--accent);
  border: none;
  font-family: var(--display);
  font-weight: 700;
  padding: 0.6rem;
}
.stButton > button[kind="primary"]:hover { background: var(--accent-dark); color: #fff; }

/* Khối viền của st.container(border=True) */
div[data-testid="stVerticalBlockBorderWrapper"] {
  border-radius: 16px !important;
  border-color: var(--border) !important;
  background: var(--surface);
}

/* Header ứng dụng */
.vl-header {
  display: flex; align-items: center; gap: 12px;
  padding: 0 0 16px; margin-bottom: 20px;
  border-bottom: 1px solid var(--border);
}
.vl-mark {
  width: 36px; height: 36px; border-radius: 10px; background: var(--accent);
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-family: var(--display); font-weight: 800; font-size: 18px;
}
.vl-name { font-family: var(--display); font-weight: 800; font-size: 19px; line-height: 1.1; }
.vl-sub { font-size: 12px; color: var(--text-muted); }

/* Nhãn nhóm trong thanh bên */
.vl-label {
  font-family: var(--display); font-weight: 700; font-size: 13px;
  text-transform: uppercase; letter-spacing: 0.04em;
  color: var(--text-muted); margin: 4px 0 2px;
}

/* Thẻ giới thiệu ở màn hình chờ */
.vl-intro { border: 1px solid var(--border); border-radius: 16px; padding: 28px 30px; background: var(--surface); }
.vl-intro p.lead { font-size: 15px; color: oklch(35% 0.01 90); margin: 0 0 18px; }
.vl-intro .row { display: flex; gap: 12px; align-items: flex-start; margin-bottom: 14px; }
.vl-intro .icon {
  width: 28px; height: 28px; border-radius: 8px; flex: 0 0 auto;
  display: flex; align-items: center; justify-content: center; font-size: 14px;
}
.vl-intro .icon.g { background: oklch(90% 0.1 145); }
.vl-intro .icon.p { background: oklch(92% 0.09 290); }
.vl-intro .icon.y { background: oklch(93% 0.1 80); }
.vl-intro .row div:last-child { font-size: 13.5px; color: var(--text-soft); padding-top: 4px; }

/* Banner đường đi */
.vl-banner { padding: 14px 18px; border-radius: 12px; font-size: 14px; margin-bottom: 14px; }
.vl-banner.happy { background: oklch(93% 0.06 145); color: oklch(32% 0.13 145); }
.vl-banner.low { background: oklch(94% 0.08 80); color: oklch(38% 0.13 80); }
.vl-banner.bad { background: oklch(94% 0.07 25); color: oklch(42% 0.16 25); }

.vl-note {
  border-left: 3px solid oklch(70% 0.01 90); padding: 10px 16px; margin: 0 0 14px;
  font-size: 13.5px; color: var(--text-soft); background: var(--surface-muted);
  border-radius: 0 10px 10px 0;
}

/* Ô chỉ số */
.vl-stat { border: 1px solid var(--border); border-radius: 14px; padding: 16px 18px; background: var(--surface); }
.vl-stat .k { font-size: 12px; color: var(--text-muted); margin-bottom: 4px; }
.vl-stat .v { font-family: var(--display); font-weight: 800; font-size: 26px; line-height: 1.1; }
.vl-stat .v.ok { color: var(--ok); }
.vl-stat .v small { font-size: 14px; font-weight: 600; color: var(--text-muted); }

/* Nhãn trích dẫn + kết quả kiểm chứng */
.vl-chip {
  font-size: 12px; font-family: ui-monospace, monospace;
  background: oklch(95% 0.005 90); padding: 3px 8px; border-radius: 6px;
  color: oklch(45% 0.01 90); margin-right: 6px;
}
.vl-badge { font-size: 11.5px; padding: 3px 9px; border-radius: 6px; margin-right: 6px; }
.vl-badge.exact { background: oklch(92% 0.08 145); color: oklch(35% 0.14 145); }
.vl-badge.partial { background: oklch(94% 0.09 80); color: oklch(42% 0.13 80); }
.vl-badge.missing { background: oklch(94% 0.07 25); color: oklch(45% 0.16 25); }
.vl-badge.regen { background: oklch(94% 0.06 290); color: var(--accent-dark); }

.vl-q { font-size: 15px; font-weight: 600; line-height: 1.5; margin-bottom: 6px; }

/* Phương án sau khi đã trả lời */
.vl-opt {
  display: flex; align-items: center; gap: 10px; padding: 10px 14px;
  border-radius: 10px; border: 1px solid oklch(90% 0.01 90);
  font-size: 14px; background: var(--surface); margin-bottom: 8px;
}
.vl-opt .letter {
  width: 22px; height: 22px; border-radius: 50%; flex: 0 0 auto;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; background: oklch(95% 0.005 90); color: var(--text-soft);
}
.vl-opt.correct { background: oklch(94% 0.07 145); border-color: oklch(70% 0.12 145); }
.vl-opt.correct .letter { background: oklch(55% 0.14 145); color: #fff; }
.vl-opt.wrong { background: oklch(95% 0.06 25); border-color: oklch(75% 0.13 25); }
.vl-opt.wrong .letter { background: oklch(55% 0.17 25); color: #fff; }
.vl-opt.dim { opacity: .55; }

.vl-verdict { font-size: 14px; font-weight: 600; margin-top: 12px; }
.vl-verdict.ok { color: oklch(40% 0.14 145); }
.vl-verdict.bad { color: oklch(45% 0.16 25); }
.vl-explain { font-size: 13.5px; color: var(--text-soft); margin-top: 8px; line-height: 1.5; }
.vl-quote {
  font-size: 13px; color: oklch(48% 0.01 90); margin-top: 8px; font-style: italic;
  border-left: 2px solid oklch(88% 0.01 90); padding-left: 10px;
}
.vl-fail {
  margin-top: 10px; font-size: 13px; color: oklch(48% 0.16 25);
  background: oklch(96% 0.05 25); padding: 8px 12px; border-radius: 8px;
}
.vl-source {
  font-size: 13px; color: oklch(42% 0.01 90); background: var(--surface-muted);
  border-radius: 10px; padding: 12px 14px; line-height: 1.5;
  max-height: 280px; overflow-y: auto; white-space: pre-wrap;
}
.vl-runnote { font-size: 12px; color: var(--text-muted); margin-top: 18px; }

/* Trạng thái trước khi gọi AI: giúp người học biết cần làm gì tiếp theo. */
.vl-ready { border: 1px solid var(--border); background: var(--surface); border-radius: 12px;
  padding: 12px 14px; margin: 10px 0 16px; font-size: 13px; color: var(--text-soft); }
.vl-ready strong { color: var(--text); }
.vl-ready.ok { border-color: oklch(75% 0.1 145); background: oklch(97% 0.035 145); }
.vl-ready.warn { border-color: oklch(82% 0.1 80); background: oklch(98% 0.035 80); }
.vl-step { display: flex; gap: 8px; align-items: center; margin: 2px 0 10px; font-size: 12px; color: var(--text-muted); }
.vl-step b { display:inline-flex; align-items:center; justify-content:center; width:20px; height:20px;
  border-radius:50%; background: var(--accent-soft); color: var(--accent-dark); font-size:11px; }

/* Ưu tiên thao tác chạm và chống tràn ở màn hình hẹp. */
@media (max-width: 720px) {
  .block-container { padding: 1rem .8rem 2rem; }
  .vl-header { margin-bottom: 14px; }
  .vl-intro { padding: 20px; }
  .vl-q { font-size: 14px; }
  .stButton > button { min-height: 42px; }
}

/* Tab */
.stTabs [data-baseweb="tab-list"] { gap: 6px; background: oklch(95% 0.005 90); padding: 4px; border-radius: 12px; }
.stTabs [data-baseweb="tab"] {
  border-radius: 9px; padding: 8px 16px; font-family: var(--display);
  font-weight: 700; font-size: 13.5px; color: var(--text-muted);
}
.stTabs [aria-selected="true"] { background: var(--surface); color: oklch(35% 0.15 290); }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Nạp dữ liệu (cache để không đọc lại PDF mỗi lần rerun)
# --------------------------------------------------------------------------


@st.cache_data(show_spinner=False)
def _documents() -> list[dict]:
    return [
        {"doc_id": d.doc_id, "title": d.title, "kind": d.kind, "path": str(d.path)}
        for d in qe.list_documents()
    ]


@st.cache_data(show_spinner="Đang đọc tài liệu…")
def _units(doc_id: str, title: str, kind: str, path: str) -> list[dict]:
    doc = qe.Document(doc_id=doc_id, title=title, kind=kind, path=Path(path))
    return [{"ref": u.ref, "text": u.text} for u in qe.load_units(doc)]


def _short_title(title: str) -> str:
    """`[Slide] d1-slide-hackathon` -> `d1-slide-hackathon` (nhãn kind tách riêng)."""
    return title.split("] ", 1)[-1]


def _safe(value: object) -> str:
    """Escape content returned by the model before placing it in an HTML fragment."""
    return escape(str(value or ""), quote=True)


def _collect_units(picked: list[dict]) -> list[qe.Unit]:
    """Gom đơn vị của nhiều tài liệu thành danh sách có mã trích dẫn DUY NHẤT.

    Hai bộ slide đều có "Trang 5" — không gắn tiền tố thì lớp kiểm chứng không
    biết trích dẫn thuộc tài liệu nào. Một tài liệu thì giữ nguyên "Trang 5".
    """
    multi = len(picked) > 1
    units: list[qe.Unit] = []
    for i, p in enumerate(picked, start=1):
        for u in p["units"]:
            ref = f"Tài liệu {i} · {u['ref']}" if multi else u["ref"]
            units.append(qe.Unit(ref=ref, text=u["text"]))
    return units


def _verified(v: dict) -> bool:
    return (
        v["citation_in_scope"]
        and v["evidence_match"] in ("exact", "partial")
        and v["options_valid"]
    )


# --------------------------------------------------------------------------
# Thanh bên — chọn tài liệu & cấu hình
# --------------------------------------------------------------------------

docs = _documents()
if not docs:
    st.error(
        f"Không tìm thấy tài liệu trong `{qe.DATA_ROOT}`.\n\n"
        "Đặt biến môi trường `VLEARN_DATA_ROOT` trỏ tới thư mục `vlearn-pack`."
    )
    st.stop()

with st.sidebar:
    st.markdown('<div class="vl-step"><b>1</b> Chọn nội dung muốn ôn</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="vl-label">Tài liệu buổi học <span style="text-transform:none;'
        'font-weight:500;color:oklch(60% 0.01 90);">(chọn nhiều)</span></div>',
        unsafe_allow_html=True,
    )

    picked: list[dict] = []
    for i, d in enumerate(docs):
        raw_units = _units(d["doc_id"], d["title"], d["kind"], d["path"])
        refs = [u["ref"] for u in raw_units]
        checked = st.checkbox(
            f"{_short_title(d['title'])}  ·  {KIND_LABEL.get(d['kind'], d['kind'])}",
            value=(i == 0),
            key=f"doc_{d['doc_id']}",
            help=f"{len(refs)} đơn vị nội dung",
        )
        if not checked:
            continue
        default_hi = refs[min(19, len(refs) - 1)]
        lo, hi = st.select_slider(
            "Phạm vi",
            options=refs,
            value=(refs[0], default_hi),
            key=f"range_{d['doc_id']}",
            label_visibility="collapsed",
        )
        i_lo, i_hi = refs.index(lo), refs.index(hi)
        if i_lo > i_hi:
            i_lo, i_hi = i_hi, i_lo
        picked.append(
            {
                "doc": d,
                "title": _short_title(d["title"]),
                "units": raw_units[i_lo : i_hi + 1],
            }
        )

    selected = _collect_units(picked)
    total_chars = sum(u.char_count for u in selected)
    st.caption(
        f"Đã chọn **{len(picked)}** tài liệu · **{len(selected)}** đơn vị · "
        f"**{total_chars:,}** ký tự trích xuất được".replace(",", ".")
    )

    st.divider()

    st.markdown('<div class="vl-step"><b>2</b> Thiết lập bộ câu hỏi</div>', unsafe_allow_html=True)
    st.markdown('<div class="vl-label">Bộ câu hỏi</div>', unsafe_allow_html=True)
    n_questions = st.slider("Số câu hỏi", 3, 10, 5)
    difficulty = st.radio("Mức độ", DIFFICULTIES, index=1)
    extra_request = st.text_input(
        "Yêu cầu thêm (tuỳ chọn)",
        placeholder="vd: tập trung vào phần RAG",
    )

    st.divider()

    # Những thiết lập này chỉ cần khi chạy AI; giữ gọn màn hình học mặc định.
    with st.expander("Cấu hình AI nâng cao", expanded=not bool(os.getenv("OPENROUTER_API_KEY", ""))):
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        if api_key:
            st.caption("🟢 Đã kết nối OpenRouter từ `.env`")
        else:
            api_key = st.text_input(
                "OpenRouter API key", type="password", placeholder="sk-or-v1-...", key="api_key_input"
            )
            st.caption("Key chỉ dùng cho phiên này; không được lưu vào mã nguồn.")

        model = st.selectbox("Model", MODEL_CHOICES, index=0, key="model_choice")
        suggested = qe.estimate_max_tokens(n_questions)
        max_tokens = st.number_input(
            "Giới hạn token đầu ra",
            min_value=500,
            max_value=8000,
            value=suggested,
            step=250,
            key="max_tokens_input",
            help="Gợi ý khoảng 350 token mỗi câu, giúp tránh lỗi thiếu credit.",
        )
        st.caption(f"Gợi ý cho {n_questions} câu: **{suggested:,}** token.")

    # Giá trị mặc định vẫn tồn tại khi expander đóng với key đã có trong .env.
    api_key = os.getenv("OPENROUTER_API_KEY", "") or st.session_state.get("api_key_input", "")
    model = st.session_state.get("model_choice", MODEL_CHOICES[0])
    max_tokens = st.session_state.get("max_tokens_input", qe.estimate_max_tokens(n_questions))


# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------

st.markdown(
    """
    <div class="vl-header">
      <div class="vl-mark">V</div>
      <div>
        <div class="vl-name">VLearn Self-Quiz</div>
        <div class="vl-sub">Tự luyện có trích dẫn kiểm chứng</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_quiz, tab_chat = st.tabs(["📝  Sinh câu hỏi", "💬  Hỏi đáp"])

# Hiển thị trước điều kiện chạy để người học không phải bấm rồi mới biết thiếu gì.
preflight_reason = ""
if not selected:
    preflight_reason = "Chọn ít nhất một tài liệu ở thanh bên."
elif total_chars > MAX_CONTEXT_CHARS:
    preflight_reason = "Thu hẹp phạm vi: phần chọn hiện vượt giới hạn ngữ cảnh."
else:
    preflight_reason = qe.precheck_context(selected, n_questions) or ""
can_generate = not preflight_reason and bool(api_key)


# --------------------------------------------------------------------------
# Tab 1 — sinh quiz
# --------------------------------------------------------------------------


def _run_generation() -> None:
    """Một lượt sinh quiz: precheck của mình trước, rồi mới tốn lượt gọi AI."""
    st.session_state.pop("answers", None)

    if not selected:
        st.session_state["result"] = {
            "path": "low_confidence",
            "reason": "Chưa chọn tài liệu nào ở thanh bên.",
            "questions": [],
            "verifications": [],
        }
        return

    if total_chars > MAX_CONTEXT_CHARS:
        st.session_state["result"] = {
            "path": "low_confidence",
            "reason": (
                f"Phạm vi đã chọn có {total_chars:,} ký tự — vượt trần "
                f"{MAX_CONTEXT_CHARS:,} ký tự mỗi lượt. Bỏ bớt tài liệu hoặc thu hẹp "
                "khoảng trang để không đốt credit vào một prompt khổng lồ."
            ).replace(",", "."),
            "questions": [],
            "verifications": [],
        }
        return

    blocker = qe.precheck_context(selected, n_questions)
    if blocker:
        # Đường đi Thiếu căn cứ — chặn trước, không tốn một lượt gọi AI.
        st.session_state["result"] = {
            "path": "low_confidence",
            "reason": blocker,
            "questions": [],
            "verifications": [],
            "prechecked": True,
        }
        return

    if not api_key:
        st.session_state["result"] = {
            "path": "error",
            "reason": "Cần OpenRouter API key trước khi gọi AI.",
            "questions": [],
            "verifications": [],
        }
        return

    with st.spinner("Đang gọi AI và kiểm chứng trích dẫn…"):
        try:
            result = qe.generate_quiz(
                units=selected,
                n_questions=n_questions,
                difficulty=difficulty,
                model=model,
                api_key=api_key,
                extra_request=extra_request,
                max_tokens=int(max_tokens),
            )
        except qe.LLMError as exc:
            st.session_state["result"] = {
                "path": "error",
                "reason": str(exc),
                "questions": [],
                "verifications": [],
            }
            return

        log_path = qe.log_run(
            result,
            doc_title=" + ".join(p["title"] for p in picked),
            refs=[u.ref for u in selected],
            note=extra_request,
        )
        st.session_state["result"] = {
            "path": result.path,
            "reason": result.reason,
            "questions": result.questions,
            "verifications": [v.__dict__ for v in result.verifications],
            "model": result.model,
            "usage": result.usage,
            "log_path": str(log_path.relative_to(qe.REPO_ROOT)),
        }


def _render_question(i: int, q: dict, v: dict, units_by_ref: dict[str, qe.Unit]) -> None:
    answers = st.session_state.setdefault("answers", {})
    answered = i in answers
    options = q.get("options") or []
    correct_idx = q.get("answer_index")

    with st.container(border=True):
        st.markdown(f'<div class="vl-q">Câu {i + 1}. {_safe(q.get("question"))}</div>', unsafe_allow_html=True)

        badge_cls = v["evidence_match"]
        badge_text = BADGE_TEXT[badge_cls]
        if badge_cls == "partial":
            badge_text += f" ({v['overlap']:.0%})"
        regen = '<span class="vl-badge regen">🔁 đã sinh lại</span>' if q.get("_regenerated") else ""
        st.markdown(
            f'<div style="margin-bottom:14px;"><span class="vl-chip">[{_safe(q.get("citation_ref", "?"))}]</span>'
            f'<span class="vl-badge {badge_cls}">{badge_text}</span>{regen}</div>',
            unsafe_allow_html=True,
        )

        if len(options) != 4:
            st.markdown(
                '<div class="vl-fail">Câu này có phương án không hợp lệ — không cho làm.</div>',
                unsafe_allow_html=True,
            )
        elif not answered:
            # Chưa trả lời: mỗi phương án là một nút bấm, bấm xong mới lộ đáp án.
            for j, opt in enumerate(options):
                if st.button(f"{LETTERS[j]}.  {opt}", key=f"opt_{i}_{j}", use_container_width=True):
                    answers[i] = j
                    st.rerun()
        else:
            chosen = answers[i]
            for j, opt in enumerate(options):
                cls = "correct" if j == correct_idx else ("wrong" if j == chosen else "dim")
                st.markdown(
                    f'<div class="vl-opt {cls}"><span class="letter">{LETTERS[j]}</span>'
                    f"<span>{_safe(opt)}</span></div>",
                    unsafe_allow_html=True,
                )
            ok = chosen == correct_idx
            verdict = (
                "Đúng."
                if ok
                else f"Chưa đúng. Đáp án: {LETTERS[correct_idx]}. {options[correct_idx]}"
            )
            st.markdown(
                f'<div class="vl-verdict {"ok" if ok else "bad"}>{_safe(verdict)}</div>'
                f'<div class="vl-explain"><strong>Giải thích:</strong> {_safe(q.get("explanation"))}</div>'
                f'<div class="vl-quote">Dẫn chứng từ [{_safe(q.get("citation_ref"))}]: '
                f'“{_safe(q.get("evidence_quote"))}”</div>',
                unsafe_allow_html=True,
            )

        if not _verified(v):
            st.markdown(
                f'<div class="vl-fail">{" · ".join(v["notes"])}</div>', unsafe_allow_html=True
            )

        with st.expander("Đối chiếu với nội dung gốc"):
            unit = units_by_ref.get(q.get("citation_ref", ""))
            body = (unit.text[:2000] if unit else "") or "(không có đơn vị nào mang mã trích dẫn này)"
            st.markdown(f'<div class="vl-source">{_safe(body)}</div>', unsafe_allow_html=True)

        # --- Đường đi Correction ---
        with st.expander("🔁 Báo câu này sai / sinh lại"):
            who = st.text_input("Tên bạn", key=f"who_{i}", placeholder="vd: Sơn")
            issue = st.text_area(
                "Sai ở đâu?",
                key=f"issue_{i}",
                placeholder="vd: slide không hề nói ý này / hai đáp án cùng đúng",
            )
            c1, c2 = st.columns(2)
            if c1.button("Ghi phản hồi", key=f"log_{i}", use_container_width=True):
                if issue.strip():
                    qe.log_feedback(
                        who,
                        " + ".join(p["title"] for p in picked),
                        q.get("citation_ref", "?"),
                        q.get("question", ""),
                        issue,
                    )
                    st.success("Đã ghi vào `validation/feedback_log.md`.")
                else:
                    st.warning("Nhập nội dung phản hồi trước đã.")
            if c2.button("Sinh lại câu này", key=f"regen_{i}", type="primary", use_container_width=True):
                if not issue.strip():
                    st.warning("Cần mô tả lỗi để AI biết sửa gì.")
                elif not api_key:
                    st.error("Cần OpenRouter API key trước khi gọi AI.")
                else:
                    with st.spinner("Đang sinh lại…"):
                        try:
                            new = qe.regenerate_one(
                                selected,
                                q,
                                issue,
                                difficulty,
                                model,
                                api_key,
                                max_tokens=qe.estimate_max_tokens(1),
                            )
                        except qe.LLMError as exc:
                            st.error(f"Lỗi: {exc}")
                        else:
                            qe.log_run(
                                new,
                                doc_title=" + ".join(p["title"] for p in picked),
                                refs=[u.ref for u in selected],
                                note=f"correction cho câu {i + 1}: {issue}",
                            )
                            if new.questions:
                                res = st.session_state["result"]
                                res["questions"][i] = {**new.questions[0], "_regenerated": True}
                                res["verifications"][i] = new.verifications[0].__dict__
                                st.session_state["result"] = res
                                st.session_state.get("answers", {}).pop(i, None)
                                st.rerun()
                            else:
                                st.warning(f"AI không sinh được câu thay thế: {new.reason}")


with tab_quiz:
    st.markdown("### Sinh câu hỏi tự luyện")
    st.caption(
        "Chọn nội dung → thiết lập độ khó → làm quiz. Mỗi câu luôn có nguồn để bạn tự đối chiếu."
    )

    if preflight_reason:
        ready_text = f"<strong>Chưa sẵn sàng.</strong> { _safe(preflight_reason) }"
        ready_class = "warn"
    elif not api_key:
        ready_text = "<strong>Cần kết nối AI.</strong> Mở “Cấu hình AI nâng cao” ở thanh bên và nhập OpenRouter API key."
        ready_class = "warn"
    else:
        ready_text = (
            f"<strong>Sẵn sàng sinh {n_questions} câu.</strong> "
            f"{len(selected)} phần nội dung đã chọn · {total_chars:,} ký tự nguồn."
        ).replace(",", ".")
        ready_class = "ok"
    st.markdown(f'<div class="vl-ready {ready_class}">{ready_text}</div>', unsafe_allow_html=True)

    col_run, col_reset, _ = st.columns([1.6, 1, 2.8])
    if col_run.button(
        "🎯 Sinh câu hỏi", type="primary", use_container_width=True, disabled=not can_generate
    ):
        _run_generation()
    if col_reset.button("Xoá kết quả", use_container_width=True):
        st.session_state.pop("result", None)
        st.session_state.pop("answers", None)
        st.rerun()

    st.write("")

    res = st.session_state.get("result")
    if not res:
        st.markdown(
            """
            <div class="vl-intro">
              <p class="lead">Bắt đầu bằng ba bước ngắn — hệ thống chỉ gọi AI khi phạm vi có đủ căn cứ.</p>
              <div class="row"><div class="icon g">✅</div>
                <div><strong>1. Chọn phạm vi:</strong> lấy đúng phần bạn vừa học, không cần nạp cả kho tài liệu.</div></div>
              <div class="row"><div class="icon p">🔍</div>
                <div><strong>2. Sinh và làm quiz:</strong> đáp án chỉ hiện sau khi bạn chọn phương án.</div></div>
              <div class="row"><div class="icon y">🎯</div>
                <div><strong>3. Đối chiếu nguồn:</strong> máy kiểm chứng trích dẫn; câu chưa chắc chắn sẽ được đánh dấu rõ.</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        label, cls = PATH_META.get(res["path"], ("—", "low"))
        reason = res.get("reason") or "Sinh câu hỏi thành công."
        st.markdown(
            f'<div class="vl-banner {cls}"><strong>{label}</strong> — {reason}</div>',
            unsafe_allow_html=True,
        )

        if res["path"] == "refused":
            st.markdown(
                '<div class="vl-note">Công cụ này chỉ sinh <strong>câu hỏi tự luyện</strong> từ '
                "tài liệu bài giảng. Nó không đưa đáp án bài lab, không làm bài nộp điểm hộ bạn.</div>",
                unsafe_allow_html=True,
            )

        if res["questions"]:
            # Bảng chỉ số — chính là Quality bar đang được đo trực tiếp trên demo.
            n = len(res["questions"])
            verifs = res["verifications"]
            n_pass = sum(1 for v in verifs if _verified(v))
            n_exact = sum(1 for v in verifs if v["evidence_match"] == "exact")

            m1, m2, m3 = st.columns(3)
            m1.markdown(
                f'<div class="vl-stat"><div class="k">Câu sinh ra</div><div class="v">{n}</div></div>',
                unsafe_allow_html=True,
            )
            m2.markdown(
                f'<div class="vl-stat"><div class="k">Trích dẫn kiểm chứng được</div>'
                f'<div class="v ok">{n_pass}/{n} <small>{n_pass / n:.0%}</small></div></div>',
                unsafe_allow_html=True,
            )
            m3.markdown(
                f'<div class="vl-stat"><div class="k">Khớp nguyên văn</div>'
                f'<div class="v">{n_exact}</div></div>',
                unsafe_allow_html=True,
            )
            st.write("")

            if n_pass < n:
                st.warning(
                    f"{n - n_pass} câu KHÔNG kiểm chứng được — đã đánh dấu bên dưới. "
                    "Đây là hallucination bị bắt tại chỗ, không phải bug hiển thị."
                )

            units_by_ref = {u.ref: u for u in selected}
            for i, (q, v) in enumerate(zip(res["questions"], verifs)):
                _render_question(i, q, v, units_by_ref)

        if res.get("log_path"):
            st.markdown(
                f'<div class="vl-runnote">Lượt chạy đã ghi vào <code>{res["log_path"]}</code>'
                + (f' · model <code>{res.get("model")}</code>' if res.get("model") else "")
                + "</div>",
                unsafe_allow_html=True,
            )


# --------------------------------------------------------------------------
# Tab 2 — hỏi đáp có trích dẫn
# --------------------------------------------------------------------------

CHAT_BADGE = {
    "ok": ("exact", "✅ có căn cứ trong tài liệu"),
    "unverified": ("partial", "🟡 trích dẫn không kiểm chứng được"),
    "not_found": ("missing", "❌ không tìm thấy dẫn chứng"),
    "refused": ("missing", "⛔ ngoài phạm vi"),
    "error": ("missing", "⛔ lỗi"),
}


with tab_chat:
    st.markdown("### Hỏi đáp tài liệu")
    st.caption(
        "Đặt câu hỏi tự do về nội dung các tài liệu đã chọn ở bên trái. "
        "Câu trả lời luôn kèm trích dẫn nguồn — không tìm thấy căn cứ thì hệ thống nói rõ "
        "thay vì đoán bừa."
    )

    chat: list[dict] = st.session_state.setdefault("chat", [])

    if chat and st.button("Xoá hội thoại"):
        st.session_state["chat"] = []
        st.rerun()

    for m in chat:
        with st.chat_message("user" if m["role"] == "user" else "assistant"):
            st.markdown(m["text"])
            if m["role"] == "assistant":
                cls, text = CHAT_BADGE.get(m.get("status", "error"), CHAT_BADGE["error"])
                chip = f'<span class="vl-chip">[{m["citation_ref"]}]</span>' if m.get("citation_ref") else ""
                st.markdown(f'{chip}<span class="vl-badge {cls}">{text}</span>', unsafe_allow_html=True)
                if m.get("status") == "ok" and m.get("quote"):
                    st.markdown(f'<div class="vl-quote">“{m["quote"]}”</div>', unsafe_allow_html=True)

    prompt = st.chat_input("Nhập câu hỏi về nội dung bài giảng…")
    if prompt:
        chat.append({"role": "user", "text": prompt})
        if not selected:
            reply = {"role": "assistant", "text": "Chưa chọn tài liệu nào ở thanh bên.", "status": "error"}
        elif not api_key:
            reply = {"role": "assistant", "text": "Cần OpenRouter API key trước khi gọi AI.", "status": "error"}
        elif total_chars > MAX_CONTEXT_CHARS:
            reply = {
                "role": "assistant",
                "text": (
                    f"Phạm vi đang chọn có {total_chars:,} ký tự — quá rộng cho một lượt hỏi đáp. "
                    "Thu hẹp lại rồi hỏi lại."
                ).replace(",", "."),
                "status": "error",
            }
        else:
            with st.spinner("Đang tra tài liệu…"):
                try:
                    ans = qe.answer_question(selected, prompt, model=model, api_key=api_key)
                except qe.LLMError as exc:
                    reply = {"role": "assistant", "text": str(exc), "status": "error"}
                else:
                    reply = {
                        "role": "assistant",
                        "text": ans.answer,
                        "status": ans.status,
                        "citation_ref": ans.citation_ref,
                        "quote": ans.evidence_quote,
                    }
        chat.append(reply)
        st.session_state["chat"] = chat
        st.rerun()
