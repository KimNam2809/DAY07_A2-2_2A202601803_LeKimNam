# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** A2-2
**Thành viên:**
    Lê Kim Nam - 2A202601803
    Nguyễn Minh Hoàng - 2A202601609
    Nguyễn Quốc Hiệu - 2A202601627
    Nguyễn Khắc Huy - 2A202602036
    Nguyễn Duy Lâm - 2A202601073
**Ngày:** 03/08/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
Ký túc xá: quy định ở, đăng ký phòng, check-in/check-out, giờ yên tĩnh, dịch vụ hỗ trợ, bảo trì, và các câu hỏi thường gặp của sinh viên.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Residential Life Guideline | https://policy.vinuni.edu.vn/all-policies/residential-life-guideline/ | 2026-08-03 / 2025-06-20 | 717 | `audience=all`, `department=student-affairs`, `category=general-guideline`, `language=en` |
| 2 | Noise Policy, Quiet Hours and Out/In Hours | https://policy.vinuni.edu.vn/all-policies/residential-life-guideline/ | 2026-08-03 / 2025-06-20 | 502 | `audience=student`, `department=student-affairs`, `category=quiet-hours`, `language=en` |
| 3 | Guest Visit Policy | https://policy.vinuni.edu.vn/all-policies/residential-life-guideline/ | 2026-08-03 / 2025-06-20 | 753 | `audience=student`, `department=student-affairs`, `category=guest-policy`, `language=en` |
| 4 | Move In and Move Out Procedure | https://policy.vinuni.edu.vn/all-policies/residential-life-guideline/ | 2026-08-03 / 2025-06-20 | 744 | `audience=student`, `department=student-affairs`, `category=move-in-out`, `language=en` |
| 5 | Residence Hall Quiet Hour Policy | https://www.ccis.edu/policies/residence-hall-quiet-hour | 2026-08-03 / 2026-08-03 | 545 | `audience=student`, `department=residential-life`, `category=quiet-hours`, `language=en` |
| 6 | Policies and Procedures | https://www.northwestern.edu/living/current/policies/policies-and-procedures.html | 2026-08-03 / 2026-08-03 | 668 | `audience=student`, `department=residential-services`, `category=housing-policy`, `language=en` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [ ] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [ ] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | string | `student` | Giúp lọc tài liệu dành cho đúng đối tượng, đặc biệt khi benchmark có câu hỏi chỉ dành cho sinh viên. |
| `department` | string | `dormitory` | Phân biệt tài liệu theo đơn vị phụ trách nội dung. |
| `category` | string | `check-in-policy` | Cho phép lọc theo loại quy định hoặc chủ đề cụ thể. |
| `language` | string | `vi` | Giúp loại bỏ tài liệu khác ngôn ngữ khi corpus đa ngữ. |
| `source_url` | string | `https://...` | Truy vết nguồn gốc và kiểm chứng lại câu trả lời. |
| `retrieved_at` | date | `2026-08-02` | Kiểm tra độ mới của tài liệu. |
| `document_version` | string | `2026.1` | Phân biệt các phiên bản quy định theo thời gian. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Residence Hall Quiet Hour Policy | FixedSizeChunker (`fixed_size`) | 3 | 198.3 | Tốt, nhưng có thể cắt giữa ý khi chunk dài hơn mạch nội dung. |
| Residence Hall Quiet Hour Policy | SentenceChunker (`by_sentences`) | 1 | 543.0 | Rất tốt, giữ nguyên toàn bộ mạch nội dung của tài liệu ngắn. |
| Residence Hall Quiet Hour Policy | RecursiveChunker (`recursive`) | 6 | 89.2 | Tốt ở mức cấu trúc nhỏ, nhưng chunk khá vụn. |
| Policies and Procedures | FixedSizeChunker (`fixed_size`) | 3 | 239.3 | Tốt, nhưng vẫn có nguy cơ cắt cấu trúc mục. |
| Policies and Procedures | SentenceChunker (`by_sentences`) | 1 | 666.0 | Tốt nhất cho tài liệu ngắn dạng policy page. |
| Policies and Procedures | RecursiveChunker (`recursive`) | 36 | 17.5 | Quá vụn, khó đọc nếu dùng cho retrieval thực tế. |
| Guest Visit Policy | FixedSizeChunker (`fixed_size`) | 4 | 207.0 | Khá tốt, nhưng chưa tối ưu cho các rule theo bullet. |
| Guest Visit Policy | SentenceChunker (`by_sentences`) | 3 | 250.0 | Cân bằng tốt giữa ngữ cảnh và độ gọn. |
| Guest Visit Policy | RecursiveChunker (`recursive`) | 10 | 74.1 | Giữ ý nhưng quá nhiều mảnh nhỏ cho benchmark. |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Tên:** Lê Kim Nam
- **Loại chiến lược:** custom
- **Mô tả & lý do chọn cho chủ đề này:** Chọn chiến lược chia theo tiêu đề/mục của tài liệu ký túc xá vì các quy định thường được tổ chức theo section rõ ràng: check-in, nội quy, dịch vụ, xử lý vi phạm. Cách này giúp chunk giữ được ngữ cảnh hoàn chỉnh và truy xuất tốt hơn khi câu hỏi bám vào một mục cụ thể.
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — [Tên]**
- **Tên:** Nguyễn Minh Hoàng
- **Loại chiến lược:** SentenceChunker
- **Mô tả & lý do chọn:** Tài liệu dormitory thường có câu ngắn, policy rõ, nên chia theo câu giúp giữ nguyên ngữ nghĩa và tạo chunk gọn hơn fixed-size. Trên corpus này, cách này cho kết quả cân bằng nhất giữa số chunk và khả năng giữ ý, đặc biệt với các policy page có câu độc lập và ít bảng biểu.
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Tên:** Nguyễn Quốc Hiệu
- **Loại chiến lược:** RecursiveChunker
- **Mô tả & lý do chọn:** Recursive chunking thử giữ cấu trúc đoạn trước, rồi mới hạ xuống cấp nhỏ hơn nếu chunk còn dài. Chiến lược này hữu ích khi tài liệu có nhiều tiêu đề, nhưng trên corpus nhỏ và nhiều bullet thì số chunk sinh ra khá lớn; vẫn đáng thử để xem mức giữ cấu trúc so với sentence-based.
- **Code snippet (nếu custom):**

**Thành viên 4 — [Tên]**
- **Tên:** Nguyễn Khắc Huy
- **Loại chiến lược:** FixedSizeChunker
- **Mô tả & lý do chọn:** Dùng fixed-size để có baseline dễ so sánh và đảm bảo mọi tài liệu đều được chia thành các chunk đều nhau. Với corpus ký túc xá, chiến lược này phù hợp khi muốn ưu tiên tính đơn giản, ổn định và dễ kiểm soát overlap.
- **Code snippet (nếu custom):**

**Thành viên 5 — [Tên]**
- **Tên:** Nguyễn Duy Lâm
- **Loại chiến lược:** custom
- **Mô tả & lý do chọn:** Ưu tiên chiến lược tách theo bullet/list và giữ nguyên các nhóm quy định ngắn như guest policy, quiet hours, move-in checklist. Cách này thực tế với corpus Dormitory vì nhiều câu trả lời benchmark nằm đúng trong từng bullet rule, nên chunk cần ưu tiên giữ trọn từng rule thay vì cắt cơ học.
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Lê Kim Nam | custom heading/section-based | 10 | Giữ ngữ cảnh tốt nhất cho tài liệu quy định; dễ map sang câu hỏi theo mục. | Cần tiền xử lý heading và tách section chuẩn. |
| Nguyễn Minh Hoàng | SentenceChunker | 10 | Cân bằng tốt giữa coherence và số chunk; retrieval ổn định trên corpus Dormitory. | Có thể kém hơn nếu tài liệu không có dấu câu rõ ràng. |
| Nguyễn Quốc Hiệu | RecursiveChunker | 9 | Tôn trọng cấu trúc tài liệu và fallback linh hoạt. | Sinh quá nhiều chunk nhỏ, dễ làm retrieval nhiễu. |
| Nguyễn Khắc Huy | FixedSizeChunker | 8 | Đơn giản, dễ tái lập và làm baseline rõ ràng. | Cắt câu và cắt ý khi tài liệu có cấu trúc rule ngắn. |
| Nguyễn Duy Lâm | custom bullet-aware chunking | 9 | Giữ nguyên rule list và checklist khá tốt cho policy pages. | Cần viết tiền xử lý riêng, khó chuẩn hóa hơn built-in strategy. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
Với corpus Dormitory này, `SentenceChunker` là chiến lược mặc định tốt nhất vì nó cho kết quả retrieval ổn định, giữ nội dung nguyên vẹn và không tạo quá nhiều chunk vụn như recursive. Nếu tài liệu có heading rõ ràng hơn, custom heading/section-based chunking sẽ là lựa chọn mạnh nhất, nhưng trên corpus hiện tại thì sentence chunking cho cân bằng tốt nhất giữa coherence và recall.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | What are the quiet hours on weekdays and weekends at VinUni? | Sunday through Thursday: 10:00 PM to 7:00 AM; Friday through Saturday: 12:00 AM to 7:00 AM. | `vinuni-quiet-hours` |
| 2 | How many guests may each resident have at the same time? | No more than three guests at the same time. | `vinuni-guest-visit-policy` |
| 3 | When must daytime guests leave the residence? | Daytime guests should stay no later than 10:00 PM. | `vinuni-guest-visit-policy` |
| 4 | What steps are required during move-in and move-out? | Complete check-in paperwork, sign handover forms, inspect the room within one day, then schedule inspection, clean up, and return keys on move-out. | `vinuni-move-in-out` |
| 5 | What are the quiet hours at Columbia College residence halls? | Sunday through Thursday: 10:00 PM to 10:00 AM; Friday through Saturday: 12:00 AM to 12:00 PM. | `columbia-residence-hall-quiet-hours` |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | What are the quiet hours on weekdays and weekends at VinUni? | SentenceChunker | Yes | Top-1 là Columbia policy, nhưng VinUni chunk đứng trong top-3; đây là câu hỏi semantic gần nhau. |
| 2 | How many guests may each resident have at the same time? | SentenceChunker | Yes | VinUni guest policy xuất hiện ngay top-1 và lặp lại trong top-3. |
| 3 | When must daytime guests leave the residence? | SentenceChunker | Yes | Câu hỏi bám sát guest-policy section nên retrieval rất ổn định. |
| 4 | What steps are required during move-in and move-out? | SentenceChunker | Yes | Đặt `metadata_filter={"audience": "student"}` giúp loại bớt tài liệu general guideline. |
| 5 | What are the quiet hours at Columbia College residence halls? | SentenceChunker | Yes | Top-1 đúng tài liệu Columbia, score cao nhất trong 5 câu. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
Lọc metadata rất đáng giá khi câu hỏi nhắm vào một đối tượng cụ thể, đặc biệt là `audience=student`. Với bộ tài liệu ký túc xá, filter giúp loại các chunk mang tính tổng quát hơn như guideline gốc, từ đó giảm nhiễu trong top-3 và tăng khả năng truy xuất đúng mục, nhất là ở câu hỏi move-in/move-out.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
* Cùng một bộ tài liệu ký túc xá nhưng chunking khác nhau sẽ tạo ra mức giữ ngữ cảnh khác nhau, dẫn đến độ mịn của retrieval khác nhau.
* Metadata lọc có thể tăng precision rõ rệt cho các câu hỏi theo đối tượng.
* Với corpus này, sentence chunking là điểm cân bằng tốt nhất giữa coherence và số lượng chunk.

**Bài học rút ra khi so sánh trong nhóm:**
Khi cùng một corpus ký túc xá, chiến lược chia nhỏ quyết định chunk có “giữ được ý” hay bị cắt vụn. Trên corpus này, sentence chunking cho kết quả ổn định nhất, còn recursive tạo quá nhiều mảnh nhỏ nên khó đọc hơn dù vẫn retrieve đúng. Strategy bám cấu trúc tài liệu sẽ còn mạnh hơn nếu nhóm tiền xử lý heading tốt hơn trước khi ingest.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
Nhóm nên chuẩn hóa thêm heading/section trước khi ingest để chunking theo cấu trúc dễ hơn. Ngoài ra, nên gắn thêm metadata theo loại câu hỏi thực tế của benchmark để metadata filtering hữu ích hơn thay vì chỉ lọc theo nguồn. Nếu có thêm tài liệu handbook dài hơn, custom heading-based chunking sẽ đáng thử hơn sentence chunking.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
