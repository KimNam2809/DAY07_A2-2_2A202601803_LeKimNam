# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Duy Lâm

**Nhóm:** A2-2

**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung trong `REPORT_NHOM.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) — Bài tập 1.1

**Độ tương tự cosine cao nghĩa là gì?**

Độ tương tự cosine cao cho biết hai vector embedding có hướng gần giống nhau. Trong bài toán văn bản, điều này thường có nghĩa hai câu hoặc hai đoạn đang biểu đạt nội dung, chủ đề hay ý nghĩa tương tự, ngay cả khi chúng không dùng chính xác cùng từ ngữ.

**Ví dụ có độ tương tự CAO:**

- Câu A: “Sinh viên đăng ký học phần qua cổng học vụ.”
- Câu B: “Việc đăng ký môn học được thực hiện trên hệ thống học vụ.”
- Tại sao tương đồng: Hai câu đều nói về cùng đối tượng là sinh viên, cùng hành động đăng ký môn/học phần và cùng kênh thực hiện là cổng/hệ thống học vụ.

**Ví dụ có độ tương tự THẤP:**

- Câu A: “Sinh viên cần kiểm tra học phần tiên quyết.”
- Câu B: “Hôm nay thời tiết có mưa lớn.”
- Tại sao khác: Một câu thuộc chủ đề quy định học vụ, còn câu kia mô tả thời tiết; hai câu gần như không chia sẻ ý nghĩa hay ngữ cảnh.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**

Cosine similarity tập trung vào hướng của vector nên ít bị ảnh hưởng bởi độ lớn tuyệt đối của embedding. Euclidean distance phụ thuộc nhiều vào độ lớn và tỷ lệ vector, trong khi với văn bản, hướng biểu diễn ngữ nghĩa thường quan trọng hơn độ dài của vector.

### Bài toán tính toán Chunking — Bài tập 1.2

**Tài liệu 10.000 ký tự, `chunk_size=500`, `overlap=50`. Bao nhiêu chunk?**

Khoảng dịch chuyển của cửa sổ là:

```text
step = chunk_size - overlap = 500 - 50 = 450
```

Theo công thức của đề:

```text
số chunk = ceil((10.000 - 50) / (500 - 50))
          = ceil(9.950 / 450)
          = ceil(22,111...)
          = 23
```

**Đáp án:** 23 chunk.

**Nếu overlap tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**

```text
số chunk = ceil((10.000 - 100) / (500 - 100))
          = ceil(9.900 / 400)
          = ceil(24,75)
          = 25
```

Số chunk tăng từ 23 lên 25 vì mỗi cửa sổ chỉ tiến 400 ký tự thay vì 450 ký tự. Overlap lớn hơn giúp giữ lại ngữ cảnh ở ranh giới giữa hai chunk và giảm nguy cơ cắt mất một ý quan trọng, nhưng đổi lại làm tăng dữ liệu trùng lặp, chi phí embedding và chi phí tìm kiếm.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk` — hướng tiếp cận:**

Tôi loại bỏ khoảng trắng thừa, trả danh sách rỗng khi đầu vào không có nội dung, sau đó dùng regex `(?<=[.!?])(?:[ \t]+|\n+)` để tách sau dấu `.`, `!` hoặc `?` khi gặp khoảng trắng/xuống dòng. Các câu được gom theo từng nhóm có tối đa `max_sentences_per_chunk`; dấu câu vẫn được giữ lại để chunk dễ đọc và giữ ý nghĩa tốt hơn.

**`RecursiveChunker.chunk` / `_split` — hướng tiếp cận:**

Tôi thử lần lượt các separator theo mức độ từ thô đến chi tiết: đoạn văn, dòng, câu, từ và cuối cùng là ký tự. Base case là văn bản rỗng hoặc đoạn đã ngắn hơn `chunk_size`; nếu separator hiện tại không tồn tại thì chuyển sang separator tiếp theo, còn đoạn vẫn quá dài sẽ được đưa lại vào `_split()` với danh sách separator còn lại. Khi không còn separator, hàm cắt cứng theo số ký tự để bảo đảm luôn có kết quả và tránh đệ quy vô hạn.

### Chiến lược cá nhân ở Giai đoạn 2

**`BulletAwareChunker` — hướng tiếp cận:**

Theo phân công của nhóm, tôi xây dựng chiến lược custom ưu tiên các bullet/list trong tài liệu ký túc xá. Chunker nhận diện heading Markdown, bullet `-`, `*`, `+` và danh sách đánh số; mỗi rule được xem là một đơn vị nguyên vẹn, tối đa ba bullet được ghép trong một chunk và tổng độ dài không vượt 300 ký tự khi có thể. Heading được lặp lại trong các chunk con để giữ chủ đề, còn prose hoặc rule quá dài được chuyển cho `RecursiveChunker` làm fallback.

### Lớp `EmbeddingStore`

**`add_documents` + `search` — hướng tiếp cận:**

Tôi chọn kho in-memory cho phần bắt buộc của lab. Mỗi `Document` được chuẩn hóa thành record gồm ID duy nhất, nội dung, bản sao metadata và embedding; `doc_id` được bổ sung nếu chưa có. Khi tìm kiếm, truy vấn được embedding một lần, điểm của từng record được tính bằng tích vô hướng với vector truy vấn, sau đó kết quả được sắp xếp giảm dần và cắt lấy `top_k`.

**`search_with_filter` + `delete_document` — hướng tiếp cận:**

Tôi lọc metadata trước rồi mới tính similarity để chỉ xếp hạng các record thỏa mãn toàn bộ điều kiện lọc. `delete_document` tạo lại danh sách `_store`, giữ những record có `metadata["doc_id"]` khác ID cần xóa; hàm trả về `True` nếu kích thước kho giảm và `False` nếu không tìm thấy tài liệu.

### Tác tử `KnowledgeBaseAgent`

**`answer` — hướng tiếp cận:**

Agent gọi `EmbeddingStore.search()` để lấy top-k chunk, sau đó ghép nội dung, nguồn và score của từng chunk thành phần `Context`. Prompt yêu cầu LLM chỉ trả lời từ context và phải thừa nhận khi thiếu thông tin; câu hỏi được đặt sau context và toàn bộ prompt được chuyển cho `llm_fn`. Việc đưa `source_url`, `source` hoặc `doc_id` vào prompt giúp truy vết tài liệu được sử dụng.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

### Kết quả kiểm thử

Lệnh đã chạy:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```

Kết quả tóm tắt:

```text
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0
rootdir: E:\DAY07_2A202601803_LeKimNam
collected 42 items

tests/test_solution.py .......................................... [100%]

============================= 42 passed in 0.05s =============================
```

**Số lượng bài test vượt qua:** 42 / 42.

Demo tích hợp cũng chạy hết bằng:

```powershell
.\.venv\Scripts\python.exe -X utf8 main.py
```

Tùy chọn `-X utf8` được dùng vì terminal Windows hiện tại dùng `cp1258` và không in được một số ký tự tiếng Việt nếu chạy trực tiếp `python main.py`. Demo đã nạp 3 chunk, thực hiện tìm kiếm và gọi `KnowledgeBaseAgent` thành công.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Tôi dự đoán trước theo ý nghĩa của câu, sau đó gọi `compute_similarity()` trên vector 384 chiều do `LocalEmbedder` tạo với mô hình `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-------|-------|---------|---------------|-------|
| 1 | Sinh viên đăng ký học phần qua cổng học vụ. | Việc đăng ký môn học được thực hiện trên hệ thống học vụ. | Cao | 0,551201 | Có |
| 2 | Thư viện cung cấp dịch vụ mượn tài liệu. | Sinh viên có thể mượn sách tại thư viện. | Cao | 0,803110 | Có |
| 3 | Sinh viên cần kiểm tra học phần tiên quyết. | Hôm nay thời tiết có mưa lớn. | Thấp | -0,099956 | Có |
| 4 | Người dùng phải mang thẻ định danh khi mượn tài liệu. | Sinh viên cần thẻ hợp lệ để sử dụng dịch vụ mượn. | Cao | 0,607515 | Có |
| 5 | Điều chỉnh lớp học phần trước thời hạn. | Thư viện có không gian học tập. | Thấp | 0,352067 | Có, tương đối |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

Cặp 5 bất ngờ nhất vì hai câu khác chủ đề cụ thể nhưng vẫn đạt 0,352067. Điều này cho thấy semantic embedding có thể nhận ra ngữ cảnh chung về dịch vụ/học tập trong trường đại học, nên “thấp” không nhất thiết gần bằng 0 tuyệt đối. Các cặp diễn đạt lại cùng ý đạt từ 0,55 đến 0,80, trong khi cặp học vụ–thời tiết nhận điểm âm, phù hợp với dự đoán ban đầu.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

### Cấu hình thử nghiệm

- Corpus chung của nhóm: 6 tài liệu trong `data/dormitory/`.
- Chiến lược cá nhân: `BulletAwareChunker(chunk_size=300, max_bullets_per_chunk=3)`.
- Tổng số chunk: 19.
- Embedding backend: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- `top_k`: 3.
- Câu 4 dùng `metadata_filter={"audience": "student"}` theo benchmark chung.

Lệnh benchmark có thể tái chạy:

```powershell
python -X utf8 scripts/evaluate_dormitory.py --provider local --offline
```

| # | Câu hỏi (Query) | Top-1 chunk truy xuất được (tóm tắt) | Score | Có liên quan không? | Câu trả lời dựa trên context Top-3 |
|---|-----------------|--------------------------------------|-------|----------------------|------------------------------------|
| 1 | What are the quiet hours on weekdays and weekends at VinUni? | `vinuni-quiet-hours`, nội dung giới thiệu và bảng giờ yên tĩnh | 0,722003 | Có | Chủ nhật–thứ Năm: 10:00 PM–7:00 AM; thứ Sáu–thứ Bảy: 12:00 AM–7:00 AM. |
| 2 | How many guests may each resident have at the same time? | `vinuni-guest-visit-policy`, phần giới thiệu guest rules; bullet đáp án ở Top-2 | 0,605108 | Có, đáp án trực tiếp ở Top-2 | Mỗi cư dân được có tối đa ba khách tại cùng một thời điểm. |
| 3 | When must daytime guests leave the residence? | `vinuni-guest-visit-policy`, chunk giữ nguyên ba bullet liên quan đến khách | 0,744228 | Có | Khách ban ngày không nên ở lại sau 10:00 PM. |
| 4 | What steps are required during move-in and move-out? *(lọc `audience=student`)* | `vinuni-move-in-out`, chunk về kiểm tra và trả phòng | 0,638626 | Có | Hoàn tất giấy tờ check-in, ký bàn giao, kiểm tra phòng trong một ngày; khi check-out phải hẹn kiểm tra, dọn phòng và trả chìa khóa/vật dụng mượn. |
| 5 | What are the quiet hours at Columbia College residence halls? | `columbia-residence-hall-quiet-hours`; bullet giờ cụ thể ở Top-2 | 0,731455 | Có, đáp án trực tiếp ở Top-2 | Chủ nhật–thứ Năm: 10:00 PM–10:00 AM; thứ Sáu–thứ Bảy: 12:00 AM–12:00 PM. |

Các câu trả lời tóm tắt được kiểm chứng trực tiếp từ context Top-3 và gold answer chung của nhóm. `demo_llm` trong `main.py` chỉ trả phần xem trước của prompt, nên phần đánh giá này tập trung vào khả năng truy xuất và chất lượng context cung cấp cho agent.

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5.

Đúng tài liệu đứng Top-1 ở cả 5 câu; các chunk chứa chính xác bullet gold answer nằm trong Top-3 ở cả 5 câu. Theo bảng so sánh chung, chiến lược cá nhân được ghi nhận 9/10 vì một số câu hỏi rộng đưa chunk giới thiệu lên trước chunk chứa rule trực tiếp, dù context Top-3 vẫn đủ để trả lời.

**Điều hay nhất tôi học được từ việc so sánh chiến lược và chuẩn bị demo nhóm:**

Bullet-aware chunking đặc biệt hữu ích với guest policy và quiet-hours vì nó không cắt giữa một rule. Tuy nhiên, lặp heading và phần giới thiệu có thể khiến chunk tổng quát được xếp cao hơn bullet đáp án ở câu hỏi rộng. Vì vậy chiến lược này nên được so sánh bằng cả độ chính xác Top-3 và vị trí của chunk chứa gold answer, không chỉ dựa vào score lớn nhất.

---

## Tự đánh giá (Phần cá nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 9 / 10 |
| **Tổng phần cá nhân** | **59 / 60** |

Mức tự đánh giá phần truy xuất là 9/10, thống nhất với bảng so sánh nhóm. Local embedding đưa đúng tài liệu lên Top-1 cho cả năm câu, nhưng ở câu 2 và câu 5, bullet chứa gold answer đứng sau chunk giới thiệu cùng tài liệu; đây là điểm cần tiếp tục tối ưu khi điều chỉnh cách ghép bullet và phần prose.
