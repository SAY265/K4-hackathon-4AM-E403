# User Validation Feedback Log - Vlearn Quiz

## 1. Thông tin tổng quan buổi thử nghiệm
- **Sản phẩm thử nghiệm**: Vlearn Quiz (Streamlit Prototype)
- **Số lượng người tham gia**: 5 học viên
- **Mục tiêu**: Đánh giá trải nghiệm người dùng, độ chính xác AI, tính năng tạo quiz và giao diện hệ thống.

---

## 2. Bảng Phản Hồi Chi Tiết (User Feedback Log)

| STT | Người thử (Họ tên & Mã SV) | Task thực hiện | Cảm nhận & Quote nguyên văn | Góp ý / Thiếu sót (Quote nguyên văn) | Mức độ nghiêm trọng |
|---|---|---|---|---|---|
| 1 | **Lê Nhật Minh**<br>`2A202602023` | Tạo quiz & xem đáp án | *"Tôi thấy sản phẩm này hiệu quả, tạo quiz rất tiện, giao diện thân thiện người dùng"* | *"Không"* | Thấp (Low) |
| 2 | **Tạ Đăng Đức**<br>`2A202601772` | Tạo quiz & chọn phạm vi slide | *"App chạy tính năng ổn, giao diện đẹp, thân thiện với người dùng."* | *"Mình muốn hệ thống gợi ý lại học phần hay dlide mà mình đã sai quá nhiều."* | Trung bình (Medium) |
| 3 | **Trần An Thắng**<br>`2A202601756` | Trải nghiệm giao diện | *"sản phẩm này khá hữu ích với tôi"* | *"Tôi muốn UI đẹp hơn nữa"* | Thấp (Low) |
| 4 | **Lương Bảo Long**<br>`2A202601682` | Đặt câu hỏi trong tab Hỏi đáp | *"Đủ ổn so với tính năng cần cải thiện chatbot vấn đáp"* | *"Chatbot vấn đáp không hiểu nhiều ngữ cảnh"* | Trung bình (Medium) |
| 5 | **Lê Trung Kiên**<br>`2A202601182` | Đánh giá tổng thể | *"Hệ thống rất amzing goodjob"* | *"Còn khá thô"* | Thấp (Low) |

---

## 3. Tổng Hợp Đánh Giá Định Lượng (Quantitative Metrics)

### 3.1. Tính ổn định và hiệu năng hệ thống Vlearn Quiz
- **Mức 4/5**: 2/5 lượt đánh giá (40%)
- **Mức 5/5**: 3/5 lượt đánh giá (60%)
- **Điểm đánh giá trung bình**: 4.6 / 5

### 3.2. Đánh giá tính năng của sản phẩm
- **Giao diện người dùng**: 1 Trung bình · 3 Tốt · 1 Xuất sắc
- **Tốc độ tải câu hỏi**: 1 Trung bình · 2 Tốt · 2 Xuất sắc
- **Độ chính xác của kết quả**: 4 Tốt · 1 Xuất sắc
- **Tính năng xem lại đáp án**: 1 Trung bình · 3 Tốt · 1 Xuất sắc

---

## 4. Tổng Hợp & Hành Động (4-Point Synthesis)

1. **Chủ đề lặp nhiều nhất**: Người dùng mong muốn chatbot hiểu rõ ngữ cảnh hơn và giao diện được chăm chút tỉ mỉ, mượt mà hơn.
2. **1–2 Thay đổi đã thực hiện trước Demo (Changelog)**:
   - Nâng cấp toàn bộ hệ thống giao diện UI/UX theo chuẩn hiện đại: bo góc mềm, hiệu ứng hover mượt, loại bỏ các mốc số trùng ở thanh slider phạm vi slide.
   - Thêm hiệu ứng AI suy nghĩ (`🧠 AI đang suy nghĩ...`) khi sinh câu hỏi và trả lời chat; làm sạch tiền tố chữ cái trùng lặp ở các phương án.
3. **Giữ nguyên có lý do**: Giữ nguyên luồng xử lý slide-context để đảm bảo độ chính xác trích dẫn tuyệt đối `[Slide trang N]` và ngăn chặn hallucination.
4. **Đưa vào Backlog (Feature Backlog cho phiên bản tiếp theo)**:
   - Thêm tính năng phân tích điểm yếu và tự động gợi ý ôn tập lại các trang slide/học phần học viên làm sai nhiều (theo góp ý của học viên Tạ Đăng Đức).
   - Tăng cường số lượng tin nhắn lịch sử và kỹ thuật prompt ngữ cảnh rộng hơn cho Chatbot hỏi đáp (theo góp ý của học viên Lương Bảo Long).
