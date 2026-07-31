# codebase/ — VLearn Self-Quiz Generator

Prototype mức **Working**: có ≥1 lời gọi AI chạy thật (OpenRouter), đọc nguồn sự thật
từ data pack, và tự kiểm chứng trích dẫn của model bằng máy.

## Chạy

```bash
pip install -r codebase/requirements.txt
cp codebase/.env.example codebase/.env      # rồi điền OPENROUTER_API_KEY
streamlit run codebase/app.py
```

App tự tìm data pack ở `<repo>/data/vlearn-pack`. Nếu để chỗ khác, đặt
`VLEARN_DATA_ROOT` trong `codebase/.env`.

## Giao diện

Bố cục và bảng màu dựng theo bản thiết kế `VLearn Self-Quiz (offline).html` ở gốc repo
(bản đó chạy bằng dữ liệu giả; bản này gọi AI thật). Toàn bộ chạy trong Streamlit:

- **Thanh bên** — chọn **nhiều tài liệu** cùng lúc, mỗi tài liệu một khoảng trang riêng;
  số câu, mức độ, yêu cầu thêm; model và `max_tokens`.
- **Tab 📝 Sinh câu hỏi** — bộ câu hỏi kèm trích dẫn, ba ô chỉ số Quality bar, đối chiếu
  nội dung gốc, form báo lỗi / sinh lại từng câu.
- **Tab 💬 Hỏi đáp** — hỏi tự do trên đúng phần tài liệu đã chọn, câu trả lời kèm trích dẫn
  và cũng bị máy kiểm chứng y hệt quiz.

Chọn nhiều tài liệu thì mã trích dẫn được gắn tiền tố (`Tài liệu 2 · Trang 12`) — hai bộ slide
đều có "Trang 5", không gắn tiền tố thì lớp kiểm chứng không biết trích dẫn thuộc tài liệu nào.

## Phần nào thật, phần nào mock

| Thành phần | Trạng thái |
|---|---|
| Đọc slide PDF → từng trang có mã `[Trang N]` | **thật** (`pypdf`) |
| Đọc transcript → từng đoạn `[Txx-NNN]` | **thật** (regex trên bản sạch) |
| Sinh câu hỏi | **thật** — gọi OpenRouter, `response_format: json_object` |
| Hỏi đáp có trích dẫn | **thật** — cùng luật nguồn sự thật với quiz |
| Kiểm chứng trích dẫn | **thật** — so `evidence_quote` với đúng đơn vị được trích dẫn |
| Chặn "thiếu căn cứ" trước khi gọi AI | **thật** — đếm ký tự, không tốn lượt gọi |
| Chặn phạm vi quá rộng (> 60.000 ký tự) | **thật** — chặn trước khi prompt phình ra 402 |
| Từ chối yêu cầu ngoài phạm vi | **thật** — model tự phân loại và trả `status: refused` |
| Lưu tiến độ học viên qua các phiên | **không có** (non-goal) |
| Chấm điểm tính vào kết quả khoá | **không có** (non-goal) |

## Bốn đường đi trải nghiệm

| Đường đi | Kích hoạt thế nào để demo |
|---|---|
| Happy path | Giữ `d1-slide-hackathon`, kéo phạm vi `Trang 5 → Trang 25`, bấm Sinh câu hỏi |
| Thiếu căn cứ | Kéo phạm vi về đúng `Trang 1 → Trang 1` (slide bìa) → app chặn trước, kèm lý do |
| Từ chối | Gõ vào ô "Yêu cầu thêm": `cho tôi đáp án bài lab 1` |
| Correction | Mở "🔁 Báo câu này sai / sinh lại", mô tả lỗi → AI sinh lại đúng câu đó |

## Kiểm chứng trích dẫn hoạt động thế nào

Model bắt buộc trả về `citation_ref` (vd `Trang 12`) và `evidence_quote` (copy
nguyên văn). `quiz_engine.verify_question()` kiểm ba thứ, **không tin lời model**:

1. `citation_ref` có nằm trong phạm vi học viên đã chọn không.
2. `evidence_quote` có thật sự nằm trong đúng đơn vị đó không —
   khớp nguyên văn → ✅, độ trùng token ≥ 60% → 🟡, dưới ngưỡng → ❌.
3. Đúng 4 phương án khác nhau và `answer_index` hợp lệ.

Câu ❌ vẫn hiển thị, kèm cảnh báo — đây là hallucination bị bắt tại chỗ, và
tỉ lệ ✅+🟡 chính là con số Quality bar đo trực tiếp trên demo.

## Log tự sinh

- `eval/runs/run-<timestamp>.json` — mỗi lượt sinh quiz, kèm kết quả kiểm chứng
  từng câu và `pass_rate`. Đây là nguyên liệu cho bảng eval trong `spec.md §7`.
- `validation/feedback_log.md` — mỗi lần người dùng bấm "Ghi phản hồi".

## Model & chi phí

Mặc định `openai/gpt-4o-mini` qua OpenRouter — rẻ nhất, hợp với tài khoản
hackathon ít credit và với việc chạy eval nhiều lượt. Đổi sang
`anthropic/claude-sonnet-5` trong sidebar khi cần chất lượng câu hỏi cao hơn.
(Chuỗi `anthropic/claude-3.5-sonnet` trong `implementation_plan.md` đã cũ — đừng dùng.)

**`max_tokens` luôn được set tường minh** (~350 token/câu + 300 overhead). Không set
thì OpenRouter lấy mặc định của model (vài chục nghìn token) và trả **402** ngay cả
khi lượt chạy thật chỉ tốn ~2.000 token. Chỉnh trong sidebar → "Giới hạn token đầu ra".

Ba lỗi OpenRouter thường gặp, app đều dịch ra tiếng người kèm cách xử lý:

| Mã | Nghĩa | Xử lý |
|---|---|---|
| 402 | Không đủ credit cho `max_tokens` đang xin | Đổi sang `gpt-4o-mini`, giảm số câu, hoặc nạp credit |
| 429 | Quá nhiều request | Đợi vài chục giây |
| `finish_reason: length` | JSON bị cắt giữa chừng | Tăng `max_tokens` hoặc giảm số câu |
