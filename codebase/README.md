# VLearn Self-Quiz

Prototype Streamlit tạo quiz và hỗ trợ hỏi đáp dựa trên **slide PDF có sẵn trong dự án**.
Ứng dụng không đọc transcript và không hỗ trợ tải tài liệu từ thiết bị.

## Chạy ứng dụng

```bash
pip install -r codebase/requirements.txt
copy codebase\.env.example codebase\.env
streamlit run codebase/app.py
```

Điền `OPENROUTER_API_KEY` vào `codebase/.env`. Model được cố định là
`openai/gpt-4o-mini` để giữ trải nghiệm đơn giản và chi phí ổn định.

## Giao diện

Dựng theo bản thiết kế `VLearn Study Buddy.dc.html` (design system `_ds/modernist-*`):
thanh nav trên cùng với ba trang, cột trái hai bước cấu hình.

| Trang | Nội dung |
|---|---|
| **Ôn tập** | Bộ câu hỏi dạng thẻ, khoá đáp án ngay khi chọn, kèm giải thích và trang slide nguồn. |
| **Hỏi đáp** | Hội thoại về đúng phạm vi trang đang chọn, trích dẫn hiện dưới mỗi câu trả lời. |
| **Tiến độ** | Số liệu các bộ quiz đã làm **trong phiên hiện tại** (không lưu qua phiên — xem non-goal trong `spec.md`). |

Hộp thoại hướng dẫn ba bước mở ở lần vào đầu tiên; bấm **Hướng dẫn** trên nav để mở lại.

## Luồng sử dụng

1. Chọn một bộ slide có sẵn.
2. Chọn khoảng trang, mức độ nhận thức và yêu cầu bổ sung (nếu có).
3. Tạo bộ câu hỏi rồi làm bài — mỗi câu hiện đúng/sai, giải thích và trang slide nguồn
   ngay khi chọn đáp án, **không đổi lại được**.
4. Trả lời hết các câu trắc nghiệm thì thanh kết quả hiện ở đầu trang, kèm nút tạo bộ khác.
5. Hỏi đáp về phần slide đang chọn.

## Cấu trúc mã nguồn

| File | Vai trò |
|---|---|
| `app.py` | Giao diện Streamlit và điều phối trạng thái học tập. |
| `quiz_ai.py` | OpenRouter client, prompt, schema và kiểm tra JSON phản hồi. |
| `extract_slides.py` | Đọc PDF, chuẩn hoá thành mã nguồn `[Slide trang N]`. |
| `app_support.py` | Hàm thuần cho ngữ cảnh, loại câu hỏi và chấm điểm. |

Prompt hỏi đáp chỉ hỗ trợ nội dung học tập có căn cứ trong slide và giao tiếp cơ bản.
Phản hồi phải phù hợp pháp luật Việt Nam; yêu cầu không an toàn, gian lận hoặc ngoài
phạm vi sẽ bị từ chối.
