# Reflection Cá Nhân - Giáp Quốc Anh (Mã SV: 2A202601522)

## 1. Vai trò và nhiệm vụ đảm nhận
- Vai trò: Leader & Slide Pitch Lead của nhóm 4AM (Zone 3).
- Phần việc phụ trách thực tế:
  * Quản lý tiến độ dự án, phân chia công việc cho 3 thành viên còn lại bám sát 6 checkpoints của hackathon.
  * Biên soạn tài liệu slide thuyết trình 6 trang (demo-slides.pdf) trình bày về Job, Solution, Eval, Gap và Demo theo đúng quy định §5.1.
  * Đại diện nhóm thực hiện bài thuyết trình demo sản phẩm tại CP6 và điều phối các câu trả lời trong lượt Q&A với ban giám khảo.
  * Phụ trách việc triển khai (deploy) ứng dụng web.

## 2. AI đã hỗ trợ thế nào trong công việc
- Hỗ trợ tối ưu hóa nội dung văn bản trên các trang slide thuyết trình để đảm bảo sự cô đọng, mạch lạc và trực quan.
- Giúp thiết lập các câu hỏi giả định và kịch bản Q&A 5 phút với ban giám khảo dựa trên các lỗ hổng kỹ thuật đã ghi nhận trong quá trình kiểm thử.

## 3. Bài học rút ra từ case thất bại của nhóm
- Với tư cách là người điều phối nhóm, việc hệ thống chạy thử nghiệm cuối cùng chỉ đạt 86.36% mà không chạm mốc Quality Bar 90% là bài học lớn về việc phân bổ thời gian. Nhóm đã dành quá nhiều thời gian cho việc xây dựng frontend và thu thập khảo sát ban đầu mà chưa ưu tiên thực hiện vòng lặp "Chạy thử -> Đánh giá -> Sửa prompt -> Chạy lại" đủ sớm.
- Bài học cho tôi là trong các dự án ứng dụng AI, chất lượng prompt và bộ eval tự động cần phải được ưu tiên hoàn thiện sớm nhất có thể để có đủ thời gian lặp và tinh chỉnh trước khi khóa mốc nộp bài.
