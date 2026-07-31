# VLearn Study Buddy

Chatbot học tập giúp học viên hỏi đáp trên slide, nhận câu trả lời có citation,
và tạo quiz tự luyện ngay trong cuộc trò chuyện.

## Chạy prototype

Yêu cầu Python 3.11+ và OpenRouter API key.

```powershell
python -m pip install -r codebase/requirements.txt
$env:OPENROUTER_API_KEY = "..."
python -m streamlit run codebase/app.py
```

API key cũng có thể đặt trong `.streamlit/secrets.toml`:

```toml
OPENROUTER_API_KEY = "..."
```

Không commit file secrets hoặc API key.

Trong sidebar, có thể tải PDF bài giảng từ máy (tối đa 20 MB), chọn phạm vi
trang rồi đặt câu hỏi. PDF được xử lý trong bộ nhớ của phiên hiện tại, không
được ghi vào repo. PDF scan ảnh chưa có lớp OCR nên cần chuyển thành PDF có text.

## Prototype đang làm thật gì?

- Đọc hai PDF trong data pack và tách context theo từng trang.
- Cho phép tải PDF bài giảng từ máy và dùng ngay làm context.
- Chat hỏi–đáp theo nội dung slide bằng OpenRouter model `openai/gpt-4o-mini`.
- Giữ tối đa sáu tin nhắn gần nhất để hội thoại có ngữ cảnh.
- Hiển thị trạng thái xử lý sau khi gửi: đọc slide, phân loại yêu cầu và kiểm tra
  citation; không hiển thị chain-of-thought nội bộ của model.
- Nhận diện yêu cầu “tạo quiz” và hiển thị quiz ngay trong luồng chat.
- Hỗ trợ bộ đề trộn câu trắc nghiệm và tự luận; trắc nghiệm được chấm tự động,
  tự luận có đáp án gợi ý.
- Bắt model trả JSON có cấu trúc, giải thích, confidence và citation
  `[Slide trang N]`.
- Câu trả lời chat cũng bắt buộc citation; citation ngoài context bị chặn.
- Có ba trạng thái: thành công, thiếu context và từ chối yêu cầu ngoài phạm vi.
- Cho học viên trả lời, chấm điểm và xem giải thích theo đúng trang.

Không có câu trả lời/câu hỏi hardcode. Khi thiếu API key, chatbot hướng dẫn nhập
key; không chuyển sang kết quả AI giả.

## Kiểm thử

```powershell
python -m unittest discover -s tests -v
$env:OPENROUTER_API_KEY = "..."
python -m eval.run_eval --output eval/results/cp3-run-01.json
```

Golden Set có 22 case: 10 thường, 8 khó, 4 hiếm; 13 case phát triển từ
chatlog thật. Không sửa file kết quả của lượt cũ.

## Cấu trúc nộp bài

| Artifact | Nội dung |
|---|---|
| `spec.md` | Chuỗi quyết định sản phẩm, rủi ro, flow và quality bar |
| `codebase/` | Streamlit app, OpenRouter client, trích xuất slide |
| `eval/` | Golden Set, evaluator và kết quả từng lượt |
| `evidence/` | Phương pháp mining và script kiểm lại số liệu |
| `validation/` | Protocol và feedback log user test |
| `reflection/` | Khung reflection riêng cho từng thành viên |
| `demo-slides.pdf` | Deck demo 6 trang |

## Thành viên và phân công

Điền tên/mã học viên thật trước CP4; không để placeholder khi nộp.

| Thành viên | Mã học viên | Phần chịu trách nhiệm |
|---|---|---|
| `[Điền tên 1]` | `[Điền mã]` | Product Lead · evidence · spec §1–§2 |
| `[Điền tên 2]` | `[Điền mã]` | AI & Eval · prompt · Golden Set · eval |
| `[Điền tên 3]` | `[Điền mã]` | Streamlit · OpenRouter integration · UX |
| `[Điền tên 4]` | `[Điền mã]` | Spec owner · validation · demo deck |

## Trạng thái trung thực

- Code và unit test: hoàn thành.
- AI call/eval thật: cần `OPENROUTER_API_KEY` để sinh artifact kết quả.
- Khảo sát và user validation: chưa được thực hiện; repo có protocol/log trống
  để nhóm thu dữ liệu thật.
- Tên thành viên: chưa được cung cấp.
