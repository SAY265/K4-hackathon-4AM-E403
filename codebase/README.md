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

## Luồng sử dụng

1. Chọn một bộ slide có sẵn.
2. Chọn khoảng trang, mức độ nhận thức và yêu cầu bổ sung (nếu có).
3. Tạo 5 câu trắc nghiệm, làm bài và xem lại trang được trích dẫn.
4. Hỏi đáp về phần slide đang chọn.

Sau khi học viên bấm **Chấm điểm**, ứng dụng hiển thị đúng/sai, giải thích và trang
slide nguồn cho từng câu hỏi.

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
