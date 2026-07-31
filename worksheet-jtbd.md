# Worksheet JTBD đầy đủ (tham khảo sâu — bản nhẹ nằm trong 02-guide.md §1)


# Worksheet B1 — Chân dung user & Jobs To Be Done

**Nhóm:** 4AM · **Hướng:** [X] A — VLearn [ ] B — Trợ lý Học viên [ ] C — Làn mở

> Quy tắc xuyên suốt: **không rõ job thì đừng bàn feature.**
> File này điền trực tiếp và nộp kèm trong repo — nó là phần đầu vào của Phiếu nghiệm thu CP1.

## Cách dùng Strategyn Playbook (KHÔNG đọc hết 48 trang)

Chỉ tra 4 thứ: ① cách nhìn thị trường qua JTBD lens · ② `job executor` là ai · ③ cách viết `job statement`: `verb + object + contextual clarifier` · ④ 8 bước `job map`: `define → locate → prepare → confirm → execute → monitor → modify → conclude`. Mở nhiều nhất: **Chapter 2 (Define Your Market)** và **Chapter 3 (Build Your Job Map)**.

## 1. Chọn job executor *(5')*

Job executor = người **trực tiếp** dùng giải pháp để hoàn thành job. Không phải "học viên nói chung" — chọn một vai cụ thể. Gợi ý: học viên đang-trong-buổi-học · học viên ôn tập trước quiz · học viên nghỉ buổi đang catch-up · học viên hỏi bài trên Discord · giảng viên soạn bài/quiz · TA trả lời câu hỏi lặp.

**Job executor của nhóm:** Học viên đã học xong bài giảng cần kiểm tra kiến thức.

**Vì sao là người này:**
* **Áp lực về thời gian & khối lượng kiến thức:** Học viên phải tiếp thu một lượng lớn kiến thức chỉ trong buổi sáng, nhưng phải chuẩn bị đầy đủ nền tảng để thực hành bài LAB ngay vào buổi chiều cùng ngày.
* **Khó khăn khi tự đánh giá:** Học viên khó tự đo lường được mức độ nắm vững bài của mình, dẫn đến việc tích tụ các "lỗ hổng kiến thức" âm thầm.
* **Hậu quả khi làm thực hành:** Khi bước vào bài LAB, việc thiếu hụt kiến thức khiến họ mất nhiều thời gian tra cứu lại từ đầu, dễ gây ra cảm giác chán nản và có nguy cơ bỏ cuộc.
* **Nhu cầu cấp thiết:** Họ cần các bài kiểm tra ngắn (quiz ôn tập nhanh) để khảo nghiệm tức thì và củng cố lại kiến thức ngay sau buổi học thuyết.

## 2. Vẽ workflow thật của họ *(10')*

Vẽ (giấy/whiteboard, chụp ảnh bỏ repo) hành trình của job executor quanh một buổi học: **trước buổi → trong buổi → ngay sau buổi → khi ôn lại**. Ở mỗi chặng: họ làm gì, bằng công cụ gì, kẹt ở đâu. Dùng 8 bước job map làm khung tra — bước nào không liên quan ghi N/A, đừng bỏ trống.

| Chặng | Họ đang cố làm gì? | Hôm nay họ dùng gì? (tua video / hỏi bạn / hỏi tutor / ChatGPT riêng / bỏ qua) | Kẹt ở đâu? | Mức đau |
|---|---|---|---|---|
| Trước buổi | N/A | N/A | N/A | N/A |
| Trong buổi | Theo dõi bài giảng, nắm bắt kiến thức. | Xem slide được cung cấp, nghe giảng và hỏi đáp trong chatbot cá nhân. | Tốc độ bài giảng nhanh để kịp tiến độ, không kịp tự kiểm tra mức độ nắm rõ kiến thức. | L |
| Ngay sau buổi | Chuẩn bị cho bài thực hành LAB buổi chiều. | Đọc lướt lại slide bài giảng. | Không có công cụ đo lường mức độ hiểu bài. Chỉ tìm ra được lỗ hổng kiến thức khi gặp khó khăn trong bài thực hành. | H |
| Khi ôn lại | Tự đánh giá và củng cố mức độ hiểu sâu kiến thức lý thuyết đã học. | Đọc lại slide bài giảng, hỏi đáp với giảng viên hỗ trợ hoặc chatbot cá nhân| Thiếu hệ thống bài tập tự luyện thiết kế riêng bám sát nội dung slide lý thuyết. | H |

**Hai chỗ đau nhất trong workflow:**
* **Chỗ đau #1:** Học viên không có công cụ đo lường mức độ hiểu bài để phát hiện lỗ hổng kiến thức ngay sau buổi học thuyết trước khi thực hành bài LAB.
* **Chỗ đau #2:** Khi tự ôn tập lại, học viên thiếu các câu hỏi trắc nghiệm tự luyện bám sát nội dung slide lớp học để tự đo lường và củng cố kiến thức.

**Bằng chứng ban đầu cho 2 chỗ này** (từ chatlog/Discord/tự quan sát — sẽ đào sâu ở Bước 2):
* **Nhu cầu sinh quiz thực tế từ slide trong chatlog:**
  * Học viên trực tiếp yêu cầu tạo quiz/bài tập trắc nghiệm dựa trên nội dung slide bài học (Ví dụ tiêu biểu trong chatlog: `C0063`, `C0287`, `C0573`).
  * Trợ lý AI hiện tại chưa hỗ trợ được yêu cầu này.





## 3. Viết core JTBD *(7')*

Công thức: `[verb] + [object] + [contextual clarifier]`. Ba tiêu chí tự kiểm: ① bỏ tool đi job vẫn tồn tại · ② trong câu không có tên sản phẩm/AI/chatbot/app · ③ mô tả điều user muốn hoàn thành, không phải thứ product làm.

- Chưa tốt: `hỏi AI tutor về bài học`
- Tốt hơn: `làm rõ ngay chỗ vừa đọc không hiểu mà không phải rời trang tài liệu`
- Chưa tốt: `dùng AI ôn tập`
- Tốt hơn: `tìm lại đúng đoạn giảng viên giải thích một khái niệm trong vài phút thay vì tua cả buổi`

**Core JTBD bản nháp:** Dùng chatbot AI tạo câu hỏi trắc nghiệm ôn tập từ slide bài giảng để kiểm tra mức độ nắm bắt kiến thức lý thuyết.

**Từ solution lỡ nhét vào (gạch bỏ):** chatbot AI, tạo câu hỏi trắc nghiệm.

**Core JTBD bản chốt:** Đo lường mức độ nắm bắt kiến thức lý thuyết từ slide bài giảng để tự đánh giá và củng cố hiểu biết bài học.

## 4. Ba job stories *(7')*

Format: `When [trigger], I want to [motivation], so I can [outcome].`

| # | When | I want to | So I can | Story này cho thấy gì |
|---|---|---|---|---|
| JS1 | Đọc đến slide lý thuyết phức tạp. | Làm các câu hỏi nhanh về phần lý thuyết đó. | Xác nhận mình đã hiểu đúng bản chất khái niệm ngay tại chỗ. | Nhu cầu tự đánh giá cục bộ tại các phần kiến thức khó. |
| JS2 | Chuẩn bị làm bài thực hành LAB chiều. | Làm bộ câu hỏi kiểm tra nhanh toàn bộ slide bài giảng. | Phát hiện các lỗ hổng kiến thức để tự ôn lại trước khi code thực tế. | Nhu cầu kiểm tra tổng quát trước khi áp dụng kiến thức vào thực hành. |
| JS3 | Ôn tập chuẩn bị cho kỳ kiểm tra năng lực tuần. | Làm các câu hỏi đánh giá tổng hợp từ các slide bài học. | Xác định phần kiến thức còn yếu để tập trung ôn tập lại. | Nhu cầu định vị lỗ hổng kiến thức để tối ưu hóa thời gian ôn tập. |

Tự kiểm: mỗi story một tình huống thật (lý tưởng: lấy từ chatlog thật) · 3 story không trùng nhau.

## 5. Current alternatives *(5')*

Đối thủ = bất kỳ thứ gì user đang "thuê" để làm job: tua video, hỏi bạn cùng nhóm, hỏi tutor hiện tại, ChatGPT/Claude riêng, Google, tự bỏ qua.

| Alternative | Làm tốt gì? | Fail ở đâu? | Vì sao user chưa bỏ nó? |
|---|---|---|---|
| Copy slide hỏi ChatGPT/Claude riêng | Sinh câu hỏi nhanh, tùy biến linh hoạt theo yêu cầu. | Mất thời gian copy-paste thủ công; câu hỏi sinh ra lan man, không bám sát slide thực tế và dễ bị ảo giác. | Là công cụ AI tương tác nhanh và phổ biến nhất hiện tại để tự ôn tập. |
| Đọc đi đọc lại slide lý thuyết | Nhanh, tiện, có sẵn tài liệu ngay trước mắt. | Đánh giá hoàn toàn cảm tính, dễ bị ảo giác hiểu bài (illusion of competence). | Không tốn thời gian thao tác hay cài đặt công cụ bên ngoài. |

**Nếu sản phẩm nhóm không ra đời, user sẽ tiếp tục:** Tự ôn tập cảm tính bằng cách đọc lướt slide hoặc mất thời gian copy-paste thủ công sang ChatGPT cá nhân để nhận về những câu hỏi ôn tập lệch trọng tâm khóa học.

## 6. AI leverage point *(nộp vào CP1)*

- Đừng nhét AI vì "có AI nghe hay". Nếu chỗ đau nhất không phải chỗ AI giải tốt — ghi thẳng ra và chọn lại.
- Với hướng **tối ưu tính năng có sẵn**: leverage point = chỗ tính năng hiện tại đang fail job (kèm bằng chứng từ chatlog).

**AI nên vào bước nào của workflow, vai trò gì:** 
* **Bước:** Ngay sau khi học xong slide bài giảng.
* **Vai trò:** Trợ lý tự động trích xuất nội dung slide để sinh quiz trắc nghiệm ôn tập nhanh bám sát slide lý thuyết, kèm trích dẫn số trang slide nguồn.

**Vì sao không phải bước khác:** 
* Vì pain point lớn nhất của học viên là thiếu phương pháp tự đánh giá khách quan mức độ nắm bắt kiến thức sau khi đọc xong slide, nên cần đưa AI vào bước này để giải quyết trực tiếp nhu cầu lượng hóa mức độ hiểu bài.

**Product hypothesis** (công thức): *Nếu giúp [job executor] làm [job] tốt hơn ở [bước], bằng [AI leverage], họ sẽ chuyển từ [alternative] sang [giải pháp nhóm], vì [giá trị rõ nhất].*
> Nếu giúp học viên đã học xong đo lường mức độ nắm bắt kiến thức lý thuyết từ slide tốt hơn ở ngay sau khi học xong, bằng chatbot tự động sinh quiz trắc nghiệm bám sát bài học kèm trích dẫn số trang slide gốc, họ sẽ chuyển từ đọc nhẩm slide hoặc copy-paste thủ công vào ChatGPT sang VLearn Student Self-Quiz Generator, vì họ được cung cấp phương pháp tự đánh giá kiến thức khách quan, định lượng và tức thì bám sát slide thực tế.

**Assumption nguy hiểm nhất nếu nhóm đang sai** (sẽ kiểm bằng evidence + vòng validation CP5): Học viên thực sự không muốn tự đánh giá mức độ hiểu bài của mình hoặc không hứng thú với việc làm quiz tự luyện sau khi học xong slide.
