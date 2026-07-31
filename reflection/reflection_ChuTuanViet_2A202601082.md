# Reflection Cá Nhân - Chu Tuấn Việt (Mã SV: 2A202601082)

## 1. Vai trò và nhiệm vụ đảm nhận
- Vai trò: AI & Eval Engineer của nhóm 4AM (Zone 3).
- Phần việc phụ trách thực tế:
  * Trích xuất nội dung văn bản từ các file slide VLearn được cung cấp sẵn.
  * Thiết kế system prompt cho LLM để tạo quiz tự luyện bám sát ngữ cảnh slide.
  * Xây dựng bộ Golden Set gồm 22 test case trong file eval/golden_set.json bao phủ đủ 4 lớp chỗ khó.
  * Viết mã nguồn run_eval.py và chat_evaluator.py để chạy thử nghiệm tự động và đối chiếu Quality Bar.

## 2. AI đã hỗ trợ thế nào trong công việc
- Hỗ trợ sinh nhanh các trường dữ liệu JSON mẫu cho bộ Golden Set theo đúng schema kỹ thuật quy định.
- Hỗ trợ viết các đoạn mã lập trình Python để kiểm tra regex của citation và grounding keywords trong file chấm điểm tự động evaluator.py.

## 3. Bài học rút ra từ case thất bại của nhóm
- Kết quả kiểm thử CP5 của nhóm đạt 86.36%, chưa đạt Quality Bar 90% do lỗi ở case GS-013, GS-014 (trích dẫn sai trang) và GS-020 (trả về sai format JSON khi từ chối).
- Bài học cốt lõi là tôi đã thiết kế system prompt quá lỏng lẻo ở các trường hợp biên và chỉ tập trung tối ưu hóa cho happy path. Để khắc phục lỗi này, prompt của AI cần phải được phân tách rõ ràng thành hai nhiệm vụ: một phân loại yêu cầu (router prompt) để từ chối sớm các câu hỏi sai phạm vi, và một prompt chuyên biệt để sinh câu hỏi với cấu trúc JSON nghiêm ngặt có bọc khóa kiểm tra chéo trang.
