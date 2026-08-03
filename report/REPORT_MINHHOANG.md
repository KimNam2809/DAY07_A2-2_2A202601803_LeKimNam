# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Minh Hoàng-2A202601609
**Nhóm:** A2-2
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Khi hai đoạn văn bản có độ tương tự cosine cao, vector biểu diễn của chúng hướng gần giống nhau, nên chúng có ý nghĩa và ngữ cảnh tương đồng.

**Ví dụ có độ tương tự CAO:**
- Câu A: "The cat sat on the mat."
- Câu B: "The cat sat on the mat."
- Tại sao tương đồng: Đây là cùng một câu, nên vector biểu diễn gần như trùng nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "The cat sat on the mat."
- Câu B: "The weather today is sunny and warm."
- Tại sao khác: Hai câu nói về hai chủ đề hoàn toàn khác nhau.

**Tại sao độ tương tự cosine được ưu tiên hơn khoảng cách Euclid cho text embeddings?**
> Cosine similarity tập trung vào hướng của vector, phù hợp hơn với ý nghĩa ngữ cảnh, trong khi khoảng cách Euclid nhạy hơn với độ lớn tổng thể của vector.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Công thức: $\lceil (10000 - 50) / (500 - 50) \rceil = \lceil 9950 / 450 \rceil = 23$
>
> **Đáp án:** 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Với overlap = 100, số chunk là $\lceil (10000 - 100) / (500 - 100) \rceil = \lceil 9900 / 400 \rceil = 25$.
> Tăng độ chồng chéo làm các chunk có nhiều nội dung chung, giúp giữ ngữ cảnh liên tiếp tốt hơn nhưng cũng làm tăng số chunk và giảm độ cô đọng.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng cách chia văn bản theo các câu bằng regex dựa trên dấu kết thúc câu `.`, `!`, `?`, rồi gom nhóm theo số câu tối đa mỗi chunk. Nếu đầu vào rỗng hoặc không có dấu câu, hàm vẫn trả về một chunk hợp lệ để tránh lỗi.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán sẽ thử chia theo từng separator theo thứ tự ưu tiên như dòng mới, dấu chấm câu và khoảng trắng. Khi một đoạn vẫn quá dài, hàm đệ quy tiếp tục chia cho đến khi mỗi phần nhỏ hơn kích thước chunk hoặc không còn separator nào để dùng.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi tài liệu được chuyển thành một record chuẩn gồm nội dung, embedding và metadata; sau đó được lưu vào bộ nhớ. Khi tìm kiếm, query cũng được nhúng rồi so sánh bằng tích vô hướng (dot product) để xếp hạng các chunk phù hợp nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Tôi thực hiện lọc metadata trước khi tính toán độ tương tự để giảm số lượng candidate và giữ kết quả đúng nhóm dữ liệu. Với xóa tài liệu, tôi loại bỏ tất cả các chunk có cùng `doc_id` khỏi store.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent lấy top-k chunk từ store, nối các chunk đó làm ngữ cảnh, rồi xây dựng prompt ngắn gọn để LLM trả lời dựa trên context. Cách này giúp phản hồi có nền tảng rõ ràng hơn so với việc chỉ hỏi trực tiếp.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```bash
pytest tests/ -v
```

```text
============================= 42 passed in 0.12s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | The cat sat on the mat. | The cat sat on the mat. | cao | 1.0000 | Có |
| 2 | The cat sat on the mat. | A cat is sitting on the rug. | cao | 0.0928 | Không |
| 3 | The cat sat on the mat. | The weather today is sunny and warm. | thấp | -0.0266 | Có |
| 4 | Machine learning uses algorithms to learn from data. | Algorithms learn patterns from data using machine learning. | cao | 0.0672 | Không |
| 5 | Python is a programming language. | The sky is blue in the afternoon. | thấp | 0.0960 | Không (về mặt ngữ nghĩa thì thấp nhưng điểm số thực tế vẫn gần 0) |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Điều bất ngờ nhất là các cặp có ngữ nghĩa gần nhau vẫn có thể nhận điểm thấp khi dùng embedding giả lập/mock. Điều này cho thấy embedding thực sự phụ thuộc vào chất lượng mô hình và cách biểu diễn, không phải chỉ là phép toán similarity đơn thuần.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | What is Python? | A university library offers study rooms and online catalog access. | 0.0713 | Không | Trả lời mang tính chung chung và không dựa trên ngữ cảnh đúng.
| 2 | How does machine learning work? | Machine learning uses algorithms to learn from data. | 0.0626 | Có | Trả lời có nền tảng đúng trên chunk được truy xuất.
| 3 | What is a vector database? | Python is a high-level programming language. | 0.1490 | Không | Không phản ánh đúng chủ đề vector database.
| 4 | Where can I find study rooms? | Vector databases store embeddings for similarity search. | 0.1444 | Không | Không liên quan đến câu hỏi về thư viện/nhà học.
| 5 | What is a programming language? | Machine learning uses algorithms to learn from data. | 0.0645 | Không | Trả lời không đúng trọng tâm của câu hỏi.

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 1 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Tôi học được rằng chất lượng retrieval không chỉ phụ thuộc vào chunking mà còn phụ thuộc rất lớn vào embedding và metadata. Khi metadata phù hợp và chunk có ngữ cảnh rõ ràng, kết quả truy xuất sẽ tốt hơn nhiều.

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
