# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai đoạn văn bản có độ tương tự cosine cao khi chúng nằm gần nhau về mặt ý nghĩa, tức là vector embedding của chúng hướng gần cùng một phía trong không gian biểu diễn. Nói đơn giản, nội dung của chúng càng giống nhau thì điểm cosine càng cao.

**Ví dụ có độ tương tự CAO:**
- Câu A: Tôi cần đăng ký môn học cho học kỳ tới.
- Câu B: Làm sao để đăng ký các học phần trong kỳ sau?
- Tại sao tương đồng: Cả hai câu đều hỏi về việc đăng ký môn học, chỉ khác cách diễn đạt.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Tôi cần đăng ký môn học cho học kỳ tới.
- Câu B: Thời tiết hôm nay ở Hà Nội thế nào?
- Tại sao khác: Hai câu nói về hai chủ đề hoàn toàn khác nhau, một câu về học vụ và một câu về thời tiết.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity tập trung vào hướng của vector hơn là độ lớn, nên phù hợp với embeddings khi điều quan trọng là ý nghĩa của văn bản. Euclidean distance dễ bị ảnh hưởng bởi độ dài vector, trong khi cosine thường phản ánh tốt hơn mức độ gần nhau về ngữ nghĩa.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Trình bày phép tính: số lượng chunk = làm_tròn_lên((10,000 - 50) / (500 - 50)) = làm_tròn_lên(9,950 / 450) = làm_tròn_lên(22.11)
> Đáp án: 23 chunks

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, số lượng chunk trở thành làm_tròn_lên((10,000 - 100) / (500 - 100)) = làm_tròn_lên(9,900 / 400) = 25 chunks, tức là tăng thêm 2 chunk so với trước. Tôi muốn tăng overlap để giữ lại ngữ cảnh giữa các chunk liên tiếp, giúp truy xuất tốt hơn khi thông tin nằm ở ranh giới giữa hai đoạn.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi tách văn bản thành các câu bằng regex `(?<=[.!?])\s+`, tức là cắt tại khoảng trắng ngay sau dấu kết câu. Sau đó tôi `strip()` từng câu và loại bỏ các chuỗi rỗng để tránh sinh chunk lỗi khi văn bản có nhiều khoảng trắng hoặc dấu câu liên tiếp. Cuối cùng, tôi nhóm các câu lại theo `max_sentences_per_chunk` và nối bằng khoảng trắng để giữ cho chunk đọc tự nhiên.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Tôi thử tách văn bản theo thứ tự ưu tiên của các separator như xuống dòng đôi, xuống dòng đơn, dấu chấm và khoảng trắng; nếu đoạn vẫn còn quá dài thì đệ quy sang separator tiếp theo. Trường hợp cơ sở là khi chuỗi rỗng, khi độ dài đã nhỏ hơn hoặc bằng `chunk_size`, hoặc khi đã hết separator thì tôi cắt thẳng theo kích thước cố định. Cách này giúp giữ được cấu trúc tự nhiên của văn bản càng nhiều càng tốt trước khi phải chia thô.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Tôi lưu mỗi `Document` thành một record trong bộ nhớ, gồm `content`, `metadata`, `embedding` và một `id` nội bộ; nếu metadata chưa có `doc_id` thì tự gán từ tiền tố của `Document.id`. Khi tìm kiếm, tôi nhúng câu truy vấn rồi tính điểm bằng tích vô hướng giữa vector truy vấn và vector của từng chunk, sau đó sắp xếp giảm dần theo score để lấy top-k. Cách này phù hợp với embeddings đã được chuẩn hóa và giữ phần triển khai đơn giản để chạy ổn định trong bài tập.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Với `search_with_filter`, tôi lọc trước trên metadata rồi mới chạy tìm kiếm similarity trên tập ứng viên còn lại để tránh làm nhiễu kết quả. Với `delete_document`, tôi xóa toàn bộ record có `doc_id` trùng với tài liệu cần xóa và trả về `True` nếu số lượng record giảm. Cách làm này đơn giản nhưng đủ rõ ràng để quản lý tài liệu theo từng nguồn.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Tôi gọi `store.search()` để lấy các chunk liên quan nhất, rồi ghép chúng thành phần `Context` theo thứ tự đánh số, kèm `doc_id` để dễ truy vết nguồn. Prompt được viết theo hướng yêu cầu LLM chỉ dùng context và nói rõ khi context không đủ thông tin, sau đó mới đưa `Question` và phần trả lời mong muốn. Cách này giữ đúng mẫu RAG: retrieve trước, rồi mới generate dựa trên ngữ cảnh đã truy xuất.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
# Dán kết quả (output) của: pytest tests/ -v
```

**Số lượng bài test vượt qua (pass):** __ / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | cao / thấp | | |
| 2 | | | cao / thấp | | |
| 3 | | | cao / thấp | | |
| 4 | | | cao / thấp | | |
| 5 | | | cao / thấp | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:*

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
