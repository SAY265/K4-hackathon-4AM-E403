# Role 2 — AI Prompt & Evaluation

## Artifact

- `chat_golden_set.json`: 24 case kiểm thử chatbot, gồm đủ bốn kiểu tình huống
  bắt buộc của checkpoint và 15 case bắt nguồn từ quan sát thực tế.
- `run_chat_eval.py`: chạy toàn bộ bộ thử chatbot và lưu cả case đạt lẫn case
  không đạt.
- `chat_evaluator.py`: chấm status, citation, từ khóa bắt buộc và nội dung cấm.
- `checkpoint_answers.md`: câu trả lời sẵn cho sáu mục checkpoint, không điền
  thay kết quả model khi chưa chạy thật.
- `golden_set.json`: 22 case, gồm 10 case thường, 8 case khó (2 case cho
  mỗi lớp chỗ khó) và 4 case hiếm. Có 12 case phát triển từ chatlog thật;
  chỉ lưu mã turn và trích đoạn context tối thiểu.
- `run_eval.py`: gọi OpenRouter thật, chấm từng case và lưu toàn bộ output,
  kể cả case fail.
- `evaluator.py`: các kiểm tra tất định cho hành vi, schema, citation và
  từ khóa grounding.
- `results/`: nơi lưu các lượt đo. Không sửa file của lượt cũ.

## Bốn lớp chỗ khó

| Lớp | Case | Rủi ro chính |
|---|---|---|
| Chất lượng dữ liệu | GS-011–012 | Slide quá ít chữ hoặc không có nội dung |
| Citation/grounding | GS-013–014 | User yêu cầu trang sai hoặc trang mâu thuẫn |
| Instruction safety | GS-015–016 | Prompt injection và yêu cầu lộ chỉ dẫn |
| User control | GS-017–018 | Số câu, ngôn ngữ và mức độ phải theo lựa chọn mới |

Các case hiếm GS-019–022 bổ sung out-of-scope, gian lận học thuật và context
nhiều trang.

## Chạy

PowerShell:

```powershell
$env:OPENROUTER_API_KEY = "..."
python -m eval.run_eval --output eval/results/cp3-run-01.json
python -m eval.run_eval --output eval/results/cp5-final.json
python -m eval.run_chat_eval --output eval/results/chat-cp3-run-01.json
```

Mặc định dùng `openai/gpt-4o-mini`, temperature 0 và JSON mode. Có thể đổi model:

```powershell
python -m eval.run_eval --model anthropic/claude-3.5-sonnet --output eval/results/cp5-final.json
```

Quality bar đã đề xuất trong kế hoạch:

- ≥90% câu hỏi có citation đúng trang thuộc context.
- 100% giải thích có bằng chứng từ slide.
- 0% thông tin ngoài context.

Evaluator tự động bắt schema/citation và kiểm tra từ khóa grounding. Hai người
trong nhóm vẫn cần chấm độc lập các case khó để xác nhận tiêu chí “không có
thông tin ngoài context”, vì tiêu chí này không thể chứng minh hoàn toàn bằng
regex.
