# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Lê Kim Nam
**Nhóm:** A2-2
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
Khi hai câu có độ tương tự cosine cao, nghĩa là các vector embedding của chúng đang trỏ gần cùng một hướng, nên nội dung và ý nghĩa của chúng gần nhau. Nói đơn giản, hai câu có thể dùng từ khác nhau nhưng nói về cùng một chủ đề hoặc cùng một thông tin.

**Ví dụ có độ tương tự CAO:**
- Câu A: Thư viện mở cửa đến 9 giờ tối.
- Câu B: Thư viện đóng cửa lúc 9 giờ tối.
- Tại sao tương đồng: Hai câu cùng nói về thời gian hoạt động của thư viện, khác cách diễn đạt nhưng cùng ngữ cảnh.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Sinh viên phải nộp bài lab trước hạn chót.
- Câu B: Ký túc xá có quy định giờ tắt đèn lúc 11 giờ.
- Tại sao khác: Hai câu nói về hai chủ đề khác nhau, một câu về bài tập, một câu về nội quy ký túc xá.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
Cosine similarity thường phù hợp hơn cho text embeddings vì nó đo độ giống nhau về hướng của vector, tức là giống nhau về ý nghĩa, thay vì bị ảnh hưởng nhiều bởi độ lớn của vector. Với văn bản, độ lớn embedding có thể thay đổi do độ dài câu hoặc đặc trưng của mô hình, nên cosine ổn định và trực quan hơn Euclidean distance.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
Theo công thức: `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11...) = 23` chunks.

Đáp án: 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
Khi overlap tăng lên 100, số chunks tăng lên vì bước nhảy giữa các chunk nhỏ hơn. Với `chunk_size=500`, ta có `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25` chunks. Overlap lớn hơn giúp giữ ngữ cảnh liên tục giữa các chunk, đặc biệt hữu ích khi một ý nghĩa bị cắt qua ranh giới chunk.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
Tôi dùng regex để tách câu theo dấu câu kết thúc như `.`, `!`, `?`, rồi nhóm các câu lại theo `max_sentences_per_chunk`. Trường hợp văn bản không có dấu câu rõ ràng hoặc chỉ có whitespace được xử lý bằng cách trả về toàn bộ đoạn đã `strip()` thay vì làm rỗng dữ liệu. Cách này đủ ổn cho tài liệu học thuật/nghị định có văn phong tương đối chuẩn.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
Thuật toán thử lần lượt các separator theo thứ tự ưu tiên, từ cấu trúc lớn đến nhỏ: đoạn, dòng, câu, khoảng trắng, rồi mới đến cắt theo ký tự nếu cần. Base case là khi đoạn văn đã nhỏ hơn `chunk_size`, khi không còn separator nào, hoặc khi separator hiện tại không xuất hiện trong văn bản. Cách làm này giữ được cấu trúc ngữ nghĩa tốt hơn so với cắt cứng ngay từ đầu.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
Tôi lưu từng `Document` dưới dạng record chuẩn hóa gồm `id`, `content`, `metadata`, và embedding đã được chuẩn hóa độ dài. Khi tìm kiếm, tôi embed câu truy vấn, tính dot product với toàn bộ embedding đã lưu, rồi sắp xếp giảm dần theo score để lấy top-k. Việc chuẩn hóa vector giúp dot product tương đương cosine similarity trong thực tế.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
Tôi lọc theo metadata trước rồi mới tính score, để tránh so sánh trên các chunk không liên quan đến bộ lọc. Hàm xóa hỗ trợ cả trường hợp document gốc và chunked document bằng cách xóa theo `record.id` hoặc `metadata['doc_id']`. Cách này phù hợp với cả dữ liệu thô trong test và dữ liệu đã ingest từ pipeline.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
Tôi xây prompt theo cấu trúc: hướng dẫn trả lời dựa trên context, câu hỏi, rồi danh sách context đã truy xuất. Mỗi chunk được đưa vào prompt kèm nguồn tham chiếu ngắn để dễ trace nguồn khi đọc lại kết quả. Nếu context nghèo hoặc không đủ, prompt yêu cầu mô hình nói rõ là chưa đủ thông tin thay vì tự bịa.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0 -- D:\CodeLabs_VinUni\Day7\DAY07_2A202601803_LeKimNam\env\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\CodeLabs_VinUni\Day7\DAY07_2A202601803_LeKimNam
plugins: anyio-4.14.2
collected 42 items                                                             

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.11s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Quiet hours in the residence hall are from 10 PM to 7 AM. | Residents must keep noise to a minimum between 10 PM and 7 AM. | cao | 0.59 | Đúng |
| 2 | Each resident may have no more than three guests at the same time. | Guests must always be accompanied by the host. | thấp | 0.3185 | Đúng |
| 3 | Students must return access keys on move-out day. | Residents should return borrowed items when leaving the room. | cao | 0.4379 | Đúng |
| 4 | How do I report a broken light in my room? | What time does the library open on weekdays? | thấp | 0.0857 | Đúng |
| 5 | The Residential Office handles room changes case by case. | The Residential Office may help resolve roommate disputes and adjust room arrangements. | cao | 0.772 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
Kết quả bất ngờ nhất là cặp về room changes và roommate disputes có score cao nhất, dù hai câu không lặp từ y hệt nhau. Điều đó cho thấy embeddings đang mã hóa quan hệ ngữ nghĩa và bối cảnh, không chỉ là sự trùng lặp từ vựng. Ngược lại, những câu có cùng chủ đề nhưng khác mục đích rõ rệt vẫn có score thấp, nên retrieval vẫn cần chunking và metadata tốt.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | When are quiet hours on weekdays and weekends at VinUni? | Columbia quiet hour policy chunk, then VinUni quiet hours chunk | 0.7026 | Yes | VinUni quiet hours: Sunday-Thursday 10:00 PM-7:00 AM; Friday-Saturday 12:00 AM-7:00 AM. |
| 2 | How many guests may each resident have at the same time? | VinUni guest visit policy chunk | 0.7529 | Yes | Each resident may have no more than three guests at the same time. |
| 3 | When must daytime guests leave the residence? | VinUni guest visit policy chunk | 0.7135 | Yes | Daytime guests should stay no later than 10:00 PM. |
| 4 | What steps are required during move-in and move-out? | VinUni move in/out procedure chunk | 0.6394 | Yes | Complete paperwork, inspect the room within one day, schedule checkout, clean the room, and return keys. |
| 5 | What are the quiet hours at Columbia College residence halls? | Columbia quiet hour policy chunk | 0.8789 | Yes | Sunday-Thursday 10:00 PM-10:00 AM; Friday-Saturday 12:00 AM-12:00 PM. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
Trên corpus Dormitory này, cùng một query có thể kéo về nhiều policy page gần nghĩa, nên chỉ nhìn top-1 là chưa đủ. Tôi học được rằng metadata filtering và cách chia chunk quyết định liệu context cuối cùng có sạch và đúng mục tiêu hay không, nhất là khi query hỏi theo chính sách chứ không theo đúng tên tài liệu.

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
