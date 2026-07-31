# Reflection Cá Nhân - Hà Xuân Sơn (Mã SV: 2A202601904)

## 1. Vai trò và nhiệm vụ đảm nhận
- Vai trò: Streamlit App Developer của nhóm 4AM (Zone 3).
- Phần việc phụ trách thực tế:
  * Xây dựng giao diện ứng dụng Streamlit trong file codebase/app.py thân thiện với người dùng.
  * Tích hợp gọi OpenRouter API REST Endpoint để lấy dữ liệu câu hỏi từ mô hình LLM.
  * Thiết kế UI/UX cho phép học viên lựa chọn bài học, tùy chỉnh số lượng câu hỏi và độ khó của bộ quiz.
  * Lập trình xử lý các kịch bản trải nghiệm bao gồm happy path, màn hình thông báo lỗi (low-confidence) và từ chối.

## 2. AI đã hỗ trợ thế nào trong công việc
- Hỗ trợ viết nhanh cấu trúc các component giao diện của Streamlit như sidebar cấu hình, khu vực hiển thị quiz trắc nghiệm, và hiển thị phần giải thích đáp án đúng dưới dạng các khối collapse tiện lợi.
- Gợi ý cách quản lý state (session_state) trong Streamlit để giữ nguyên trạng thái làm bài của học viên khi họ bấm chọn đáp án.

## 3. Bài học rút ra từ case thất bại của nhóm
- Ứng dụng bị sập hoặc gặp lỗi hiển thị ở case GS-020 khi AI trả về chuỗi text từ chối thay vì một JSON hợp lệ để frontend parse và hiển thị.
- Bài học lập trình của tôi là không bao giờ tin tưởng hoàn toàn vào định dạng đầu ra của mô hình LLM bên thứ ba. Ở phía ứng dụng, tôi cần phải xây dựng cơ chế kiểm tra định dạng (validation schema) ở tầng nhận dữ liệu đầu vào và luôn bọc các khối mã xử lý JSON bằng try-except, đồng thời chuẩn bị sẵn các câu thông báo lỗi thân thiện để hiển thị thay vì để ứng dụng bị crash.
