# AI SPEC — Sinh Quiz ôn tập từ Slide kèm trích dẫn trang giúp học viên tự lấp lỗ hổng kiến thức · Nhóm [4AM] · Zone [3]
Hướng: [X] A — VLearn  [ ] B — Trợ lý Học viên  [ ] C — Làn mở
Loại: [ ] Tối ưu tính năng có sẵn  [X] Tính năng mới

## §1. User & Job
- Job executor + workflow (đính kèm worksheet JTBD / ảnh sơ đồ): Học viên đã học xong bài giảng cần kiểm tra kiến thức. Quy trình chi tiết được đính kèm tại [worksheet-jtbd.md](/K4-hackathon-4AM-E403/worksheet-jtbd.md).
- Core JTBD (không tên sản phẩm/AI trong câu): Đo lường mức độ nắm bắt kiến thức lý thuyết từ slide bài giảng để tự đánh giá và củng cố hiểu biết bài học.
- Problem statement (KHÔNG chữ AI): Học viên thiếu phương pháp tự đánh giá khách quan mức độ nắm bắt kiến thức sau khi học xong slide bài giảng được cung cấp bởi nền tàng của BTC chương trình, dẫn đến việc tích tụ các lỗ hổng lý thuyết âm thầm và mất nhiều thời gian loay hoay, tra cứu lại.
- Evidence (chuẩn A và/hoặc B — log đầy đủ trong repo):
  - Số liệu mining / kết quả khảo sát (n = ?, % xác nhận):
  - ≥5 quote/ví dụ nguyên văn + nguồn:

## §2. Impact & quyết định chọn
- Bảng impact ≥3 ứng viên:

| Ứng viên | Bao nhiêu người gặp | Tần suất | Mỗi lần tốn gì | Khả thi (Build nổi) | Chọn? |
|---|---|---|---|---|---|
| 1. Tự sinh Quiz ôn tập từ Slide bài giảng | | Hàng ngày, sau mỗi buổi lý thuyết | 15-20 phút tự ôn nhẩm, hoặc 30-60 phút sửa bài thực hành LAB bị lỗi | Rất cao (Đã có sẵn data slide, luồng Streamlit và gọi LLM đơn giản) | Chọn |
| 2. Hỏi đáp và tóm tắt video bài giảng dài | | 1-2 lần/tuần | Mất 1-2 tiếng tua và xem lại video bài giảng dài 2-3 tiếng | Thấp (Xử lý file video/audio lớn tốn API cost, latency cao, khó eval nhanh) | Loại |
| 3. Bản đồ chẩn đoán lỗ hổng kiến thức lớp học | | 1 lần/tuần | TA mất 2-3 tiếng tổng hợp thủ công các câu hỏi của học sinh | Trung bình (Cần gom lượng dữ liệu lớn từ nhiều kênh học tập) | Loại |

- Ứng viên ĐÃ LOẠI + vì sao:
  * Ứng viên 2 (Hỏi đáp video bài giảng): Loại vì tính khả thi thấp trong khung thời gian hackathon 1.5 ngày do xử lý dữ liệu đa phương tiện kích thước lớn tốn chi phí và độ trễ cao, khó xây dựng bộ eval chất lượng.
  * Ứng viên 3 (Bản đồ lỗ hổng kiến thức cho TA): Loại vì tập người dùng quá hẹp (chỉ phục vụ vài TA/giảng viên), không giải quyết trực tiếp pain point tự học hàng ngày của số đông học viên.

- Ứng viên CHỌN + vì sao (bằng số): 
  * Chọn Ứng viên 1 (Tự sinh Quiz ôn tập từ Slide bài giảng) vì có điểm khả thi kỹ thuật cao nhất (100% tài liệu slide đã được cấp sẵn dạng văn bản sạch trong data pack).
  * Giải quyết trực tiếp pain point cho hơn 75% học viên (dựa trên dữ liệu khảo sát nhanh) ở tần suất cao (hàng ngày) ngay trước khi làm bài LAB chiều, giúp tiết kiệm trung bình 30-60 phút loay hoay sửa lỗi do hổng lý thuyết.

## §3. Giải pháp tương tự đã nghiên cứu
- NotebookLM (Google):
  * Flow: User tải tài liệu học tập lên -> AI tự động tạo bộ câu hỏi kiểm tra dựa trên tài liệu nguồn.
  * Đáng học: Các câu hỏi bám rất sát tài liệu nguồn và có hiển thị trích dẫn nguồn cụ thể kèm theo câu trả lời để user dễ dàng đối chiếu.
  * Đáng né: Giao diện và các tính năng đi kèm quá phức tạp, cồng kềnh cho nhu cầu kiểm tra nhanh ngay sau buổi học.
  * Mình khác gì: Tối ưu hóa tối đa quy trình: học viên chỉ cần chọn đúng bài giảng trong danh sách, hệ thống tự động sinh 5 câu hỏi nhanh bám sát slide mà không bắt user tự upload hay copy tài liệu.
- Quizlet AI:
  * Flow: User nhập văn bản hoặc tải tài liệu -> Quizlet AI tự sinh bộ flashcard và đề trắc nghiệm tự luyện.
  * Đáng học: Có cơ chế chấm điểm tức thì và đưa ra giải thích lý thuyết chi tiết ngay sau khi user chọn đáp án.
  * Đáng né: Yêu cầu học viên phải chủ động copy-paste văn bản slide thủ công vào trang web ngoài; phần giải thích đôi khi bị lan man hoặc bịa đặt kiến thức ngoài lề.
  * Mình khác gì: Tích hợp sẵn trong hệ thống VLearn, đảm bảo các câu hỏi và giải thích bắt buộc phải đối chiếu khớp với slide của giảng viên và đi kèm trích dẫn số trang slide gốc.

## §4. Thiết kế
- Lát cắt MỘT CÂU (1 user · 1 việc · 1 quyết định AI · 1 kết quả): Một học viên đã học xong bài giảng chọn tính năng và cấu hình bộ câu hỏi (số câu, độ khó,...) trên slide VLearn, AI tự động sinh các câu hỏi trắc nghiệm tự luyện kèm trích dẫn số trang slide gốc [Trang N], giúp học viên phát hiện lỗ hổng lý thuyết và ôn lại đúng trang slide trước khi làm bài LAB.
- Non-goals (≥3 thứ KHÔNG build):
  * Không tính điểm chính thức của học viên vào kết quả học tập của khóa học.
  * Không tạo ra câu hỏi từ các nguồn tài liệu nằm ngoài slide bài học được lựa chọn.
  * Không bắt buộc học viên phải thực hiện làm bài.
- Mức prototype nhắm tới: [ ] Sketch [ ] Mock [X] Working — phần nào mock, phần nào thật:
  * Phần mock: Giao diện hiển thị PDF slide lớp học và danh sách các bài giảng được lưu trữ tĩnh.
  * Phần thật: Gọi API OpenRouter thật để tự động trích xuất nội dung văn bản slide, sinh câu hỏi trắc nghiệm, chấm điểm đáp án và đưa ra lời giải thích chi tiết.
- Automation: [ ] augment [ ] conditional [X] automate — lý do theo cost-of-error: Chi phí sai sót thấp do đây là công cụ tự luyện phi chính thức, học viên có thể tự đối chiếu slide gốc qua số trang trích dẫn đi kèm để đính chính nếu AI sinh sai.
- §4b. Nguyên tắc đã áp dụng (≥4 — HAX/PAIR, xem guide):
  | Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  |---|---|
  | G1: Làm rõ hệ thống làm được gì | Hiển thị thông báo ở màn hình bắt đầu: hệ thống chỉ hỗ trợ tạo quiz tự luyện từ nội dung slide bài học đã chọn. |
  | G2: Làm rõ hệ thống làm tốt đến đâu | Ghi chú rõ các câu hỏi được tạo ra hoàn toàn bám sát slide, khuyên học viên nên đối chiếu lại trang slide nguồn được dẫn kèm. |
  | G10: Thu hẹp phạm vi khi nghi ngờ | Khi slide được chọn chứa quá ít thông tin chữ, AI sẽ không cố sinh quiz mà hiển thị thông báo slide không đủ dữ liệu. |
  | G11: Giải thích vì sao | Hiển thị phần giải thích đáp án đúng chi tiết kèm số trang slide nguồn để học viên biết tại sao mình trả lời đúng hoặc sai. |
  | PAIR: Feedback & Control | Cung cấp nút bấm báo lỗi hoặc phản hồi trực tiếp cạnh mỗi câu hỏi để học viên có quyền đóng góp ý kiến khi AI hoạt động chưa tốt. |

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản (≥8) [bảng theo guide §2.5]

## §6. Bốn đường đi của trải nghiệm
- Happy path: · Low-confidence (②): · Failure/không căn cứ (①): · Correction (user sửa):
- Khi bị đòi ngoài phạm vi (③): · Case đặc thù domain (④):

## §7. Kiểm thử
- Chiều chất lượng + định nghĩa kiểm chứng được:
- Golden set (≥20 case theo cơ cấu trong guide §2.6, file trong eval/):
- Quality bar (chốt từ 23:59, giữ nguyên sau đó): "Đạt khi ≥ ___% qua bộ, và ___"
- Kết quả các lượt chạy (bảng % — cập nhật đến trước CP6):

## §8. Phân công & kế hoạch
- Phân công có tên: spec / evidence / prompt / code / demo
- Willing users (≥3 tên) + kế hoạch vòng validation CP5 (3 câu hỏi, ai log):
- Multi-prototype (nếu làm): trục khác biệt của ≥2 phương án + lý do chọn:

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
```
