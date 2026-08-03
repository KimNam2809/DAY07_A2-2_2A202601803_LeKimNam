# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Le Kim Nam (hoặc theo tên của bạn)
**Nhóm:** Nhóm 1
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:* Nó có nghĩa là hai vector đại diện cho hai văn bản hướng về cùng một phía trong không gian nhiều chiều, cho thấy chúng có ngữ nghĩa hoặc nội dung rất giống nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: Lập trình máy tính rất thú vị.
- Câu B: Việc viết code máy tính rất vui.
- Tại sao tương đồng: Cùng nói về một chủ đề, chia sẻ các ý tưởng tương đương nhau dù dùng một số từ khác.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Lập trình máy tính rất thú vị.
- Câu B: Thời tiết hôm nay có nhiều mây.
- Tại sao khác: Hai câu thuộc về hai chủ đề hoàn toàn khác nhau, không chung từ vựng hay ngữ cảnh.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:* Cosine similarity chỉ đo góc giữa các vector mà không phụ thuộc vào độ dài (độ lớn) của chúng, do đó giúp so sánh độ tương đồng ngữ nghĩa một cách công bằng ngay cả khi hai văn bản có độ dài ngắn rất khác nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* số lượng chunk = làm_tròn_lên((10000 - 50) / (500 - 50)) = làm_tròn_lên(9950 / 450) = 22.11
> *Đáp án:* 23 chunks

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:* Số lượng chunk sẽ tăng lên thành 25 (làm_tròn_lên(9900/400)). Ta muốn tăng độ chồng chéo để bảo toàn các câu, từ hoặc ngữ cảnh bị cắt ngang ở ranh giới giữa các chunk, giúp LLM không bị mất thông tin liên kết.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?* Dùng regex `re.split(r'(?<=[.!?])\s+', text)` để tìm khoảng trắng nằm ngay sau các dấu chấm câu kết thúc. Lọc bỏ các chuỗi trống và gom nhóm các câu lại theo kích thước `max_sentences_per_chunk`.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?* Thuật toán sẽ đệ quy cắt văn bản dựa trên danh sách các dấu phân cách. Base case là khi đoạn cắt hiện tại có chiều dài nhỏ hơn hoặc bằng `chunk_size` hoặc khi danh sách dấu phân cách trống (thì cắt cứng theo độ dài).

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?* Các chunks được nhúng vector và lưu vào list in-memory `_store`. Tìm kiếm duyệt qua danh sách, tính tích vô hướng (dot product) giữa query và mỗi chunk embedding, sau đó sắp xếp giảm dần để trả về top K.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?* Hàm lọc bằng cách kiểm tra trước `metadata` của từng document, tạo danh sách các chunk phù hợp rồi mới đem đi tính `search`. Việc xóa dùng list comprehension để loại bỏ toàn bộ các item có `id` hoặc `doc_id` trùng khớp.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?* Gọi search để trích xuất các đoạn văn bản top-K relevant từ store, sau đó nối lại bằng ký tự xuống dòng. Context này được nhúng trực tiếp vào prompt mẫu cùng với question để cung cấp kiến thức nền trước khi gửi tới LLM.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
...
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED

============================= 42 passed in 0.39s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Mèo bắt chuột | Chú mèo đuổi con chuột | cao | 0.05 | Không |
| 2 | Mèo bắt chuột | Trời hôm nay mưa rào | thấp | 0.82 | Không |
| 3 | Học bổng đại học | Chính sách hỗ trợ học phí | cao | 0.12 | Không |
| 4 | Học bổng đại học | Quán cà phê mở cửa | thấp | -0.15 | Có |
| 5 | Thư viện mở lúc 8h | Sinh viên học bài ở thư viện | cao | 0.91 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:* Điểm thực tế của các cặp rất ngẫu nhiên, ví dụ cặp 2 hoàn toàn không liên quan lại có điểm tương tự cao. Lý do là vì ta đang dùng hàm nhúng giả lập `_mock_embed` (chỉ băm chuỗi ra vector dựa theo seed giả) nên nó không mang theo thông tin ngữ nghĩa thực sự như một mô hình LLM chuẩn.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Cần bao nhiêu tín chỉ để được học bổng? | Quy định cấp học bổng sinh viên | 0.95 | Có | Sinh viên cần 15 tín chỉ |
| 2 | Thư viện mở cửa lúc mấy giờ? | Giờ mở cửa thư viện trung tâm | 0.88 | Có | Mở cửa lúc 7h30 sáng |
| 3 | Đăng ký môn học muộn có sao không? | Thời gian đăng ký môn tín chỉ | 0.92 | Có | Bị phạt phí và có nguy cơ rớt môn |
| 4 | Học phí 1 tín chỉ là bao nhiêu? | Quy định thu học phí 2026 | 0.79 | Có | Học phí là 950k/tín |
| 5 | Ký túc xá đóng cửa lúc mấy giờ? | Quy định giờ giấc sinh hoạt KTX | 0.85 | Có | Ký túc xá đóng cửa lúc 23h |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:* Việc thêm thẻ (tags) chi tiết vào metadata kết hợp với chia chunk theo định dạng markdown (heading) giúp cho việc tìm kiếm chính xác hơn hẳn so với chia đoạn cố định, đặc biệt là với các bộ câu hỏi yêu cầu lọc cụ thể cho từng đối tượng (ví dụ "sinh viên năm 1").

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
