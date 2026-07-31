# Reflection Cá Nhân - Vũ Quốc Anh (Mã SV: 2A202601080)

## 1. Vai trò và nhiệm vụ đảm nhận
- Vai trò: Product Lead và User Research của nhóm 4AM (Zone 3).
- Phần việc phụ trách thực tế:
  * Thu thập dữ liệu khảo sát người dùng thực tế tại lớp (n = 18 học viên) thông qua biểu mẫu khảo sát để tìm ra nhu cầu thực tế về việc sinh đề ôn tập nhanh.
  * Phân tích dữ liệu chatlog nền tảng VLearn để tìm bằng chứng học viên yêu cầu tạo quiz từ slide.
  * Hoàn thiện tài liệu spec.md (phần §1 User & Job, §2 Impact & Quyết định chọn, §8 Phân công và khảo sát người dùng).
  * Ghi nhận và tổng hợp phản hồi từ willing users trong quá trình chạy thử nghiệm sản phẩm.

## 2. AI đã hỗ trợ thế nào trong công việc
- Giúp phân tích nhanh chóng 200 đoạn chat log thô của nền tảng VLearn để tìm kiếm từ khóa và lọc ra 17 lượt hội thoại của học viên có nhu cầu thực tế về tự ôn lý thuyết.
- Hỗ trợ xây dựng cấu trúc bảng biểu và viết nháp các nội dung của tài liệu đặc tả spec.md bám sát theo các tiêu chí của rubric đề ra.

## 3. Bài học rút ra từ case thất bại của nhóm
- Trong quá trình kiểm thử, nhóm bị thất bại ở hai case GS-013 và GS-014 do AI bị người dùng đánh lừa (prompt injection yêu cầu trích dẫn trang không tồn tại). 
- Bài học của tôi ở vai trò thiết kế sản phẩm là không được tin tưởng hoàn toàn vào khả năng tự bám sát ngữ cảnh của LLM khi đối mặt với dữ liệu nhiễu cố ý từ phía người dùng. Cần thiết kế giao diện giới hạn đầu vào của người dùng (ví dụ: chỉ cho phép chọn trang slide qua dropdown cố định thay vì nhập text tự do) để giảm thiểu không gian lỗi cho mô hình AI.
