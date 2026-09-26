# Group Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin bài nộp

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Khóa/Lớp         | K4              |
| Tên nhóm         | Arrogant Idiota     |
| Repository         | https://github.com/xuantungtran64-ai/K4-L3B-DAY10-ArrogantIdiota-DataPipelineDataObservability |
| Ngày hoàn thành | 2026-09-26               |

### Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò chính | Module/deliverable sở hữu |
| --: | --- | --- | --- | --- |
| 1 | Trần Xuân Tùng | 2A202602787 | Fullstack AI Engineer | Toàn bộ dự án (`core/`, `ingestion/`, `pipelines/`, `retrieval/`, `observability/`, `evaluation/`) |

## 2. Tóm tắt kết quả

**Tóm tắt của nhóm:**
Nhóm đã hoàn thành toàn bộ các yêu cầu của bài Lab, bao gồm xây dựng hoàn chỉnh Data Ingestion (từ Crossref API), Data Observability (với Great Expectations 1.x) và Evaluation cho mô hình RAG. 
Baseline pipeline đã tạo ra thành công các bộ dữ liệu thô (raw), sạch (clean), CSDL vector (ChromaDB), bộ testset tự động (15 câu hỏi ngẫu nhiên) và bảng báo cáo phase 1.
Trong kịch bản lỗi, corruption làm nhiễu loạn văn bản (summary noise) và cắt xén tiêu đề (title truncation) ảnh hưởng mạnh nhất đến agent (Retrieval Hit Rate giảm từ 1.0 xuống 0.6, Judge Accuracy giảm từ 33.3% xuống 20%). Ngoài ra việc thay đổi ngày tháng thành 1999 lập tức làm hệ thống Freshness báo lỗi 4 dòng Stale.
Sau khi kích hoạt cơ chế Repair (lấy lại dữ liệu từ raw), tất cả chỉ số Agent Metric và Data Quality đều được phục hồi 100% về mức Baseline ban đầu.

## 3. Kiến trúc và luồng dữ liệu

### Luồng end-to-end
```text
Crossref API (hoặc Local Snapshot)
    -> raw response/raw records
    -> cleaning và data modeling
    -> embedding + ChromaDB index
    -> testset generation -> evaluation baseline
    -> quality/freshness reports
    -> corruption
    -> re-index và re-evaluate
    -> repair từ dữ liệu nguồn gốc (raw)
    -> comparison report
```

### Trách nhiệm của từng khối

| Khối             | Input          | Xử lý chính             | Output/artifact          | Owner          |
| ----------------- | -------------- | -------------------------- | ------------------------ | -------------- |
| Ingestion         | Crossref API/JSON | Fetch, parse payload, normalize | `data/raw/` | Trần Xuân Tùng |
| Cleaning          | Raw Records | Xóa khoảng trắng, gộp mảng, parse dates | `data/clean/papers_clean.csv` | Trần Xuân Tùng |
| Embedding/index   | Cleaned Data | Tạo LocalEmbeddingIndex, lưu ChromaDB | `data/chroma/`, `data/embeddings/` | Trần Xuân Tùng |
| Evaluation        | Cleaned Data | Xây Testset, chạy Answer, chấm điểm | `data/eval/`, `data/results/` | Trần Xuân Tùng |
| Observability     | Cleaned Data | Great Expectations Validator, đếm Stale | `data/quality/` | Trần Xuân Tùng |
| Corruption/repair | Cleaned / Raw | Giả lập noise, khôi phục từ raw | Artifacts corrupted/repaired | Trần Xuân Tùng |
| Orchestration     | Toàn bộ config | Gọi các module theo đúng pipeline | Các Markdown Reports | Trần Xuân Tùng |

## 4. Cách tái hiện kết quả

### Cấu hình không chứa secret

| Biến/cấu hình             | Giá trị sử dụng |
| ---------------------------- | ------------------- |
| `LLM_PROVIDER`             | gemini         |
| `LLM_MODEL`                | gemini-2.5-flash |
| Embedding model              | sentence-transformers/all-MiniLM-L6-v2 |
| Số lượng Crossref records | 24 |
| Retrieval `top_k`           | 4 |
| Freshness threshold          | 180 |

### Lệnh chạy
Baseline:
```bash
python script/run_phase1.py
```
Corruption flow:
```bash
python script/run_corruption_flow.py
```

### Kết quả tái hiện

| Lệnh             | Trạng thái                                    | Bằng chứng                         |
| ----------------- | ----------------------------------------------- | ------------------------------------ |
| Baseline pipeline | Thành công | `data/reports/phase1_report.md` |
| Corruption flow   | Thành công | `data/reports/corruption_report.md` |

## 5. Ingestion, cleaning và data contract

### Nguồn dữ liệu

| Thuộc tính                | Giá trị                             |
| --------------------------- | ------------------------------------- |
| Source                      | Crossref REST API / Offline Snapshot |
| Query/filter                | `agentic retrieval augmented generation...` / `has-abstract:true` |
| Số record nhận được    | 24 |
| Cơ chế retry/backoff      | Exponential backoff (sleep $2^{attempt}$) cho HTTP 429/50x |

### Quy tắc cleaning

| Quy tắc                                 | Quality dimension liên quan | Số record bị tác động |
| ---------------------------------------- | ---------------------------- | -------------------------: |
| Loại bỏ Title trống | Completeness | Phụ thuộc đầu vào |
| Loại bỏ Summary < 10 ký tự | Validity | Phụ thuộc đầu vào |
| Chuẩn hóa ngày tháng, tính age_days | Timeliness | Toàn bộ bản ghi |

## 6. Evaluation setup

| Thành phần                             | Cấu hình thực tế          |
| ---------------------------------------- | ----------------------------- |
| Số câu hỏi                            | 15 (từ 5 documents x 3 loại) |
| Các`question_type`                    | summary, authors, date |
| Ground-truth document ID                 | Sử dụng `paper_id` |
| Embedding model                          | all-MiniLM-L6-v2 |
| Vector store/collection                  | ChromaDB (`papers-baseline`) |
| Retrieval`top_k`                       | 4 |
| Test set dùng chung cho ba trạng thái | `data/eval/test_set.json` |

Giải thích vì sao test set được giữ nguyên:
Giữ nguyên test set giúp loại bỏ yếu tố biến thiên của câu hỏi, từ đó so sánh khách quan và chính xác tác động của việc hỏng/nhiễu dữ liệu lên hệ thống truy xuất (hit rate, accuracy).

## 7. Kết quả baseline

### Baseline metrics

| Metric                 |       Giá trị | Diễn giải                             |
| ---------------------- | --------------: | --------------------------------------- |
| `retrieval_hit_rate` |     1.0 | 100% trả về được document liên quan  |
| `mean_token_f1`      |     0.215 | Mức độ trùng lặp từ vựng giữa câu trả lời LLM và ground truth |
| `judge_accuracy`     |     0.333 | Tỷ lệ câu trả lời được Heuristic LLM đánh giá là hoàn toàn chính xác |
| Ragas        | N/A | Không chạy vì không cấu hình `RUN_RAGAS=1` |

## 8. Data quality và freshness

### Quality checks

| Check        | Quality dimension | Ngưỡng/kỳ vọng | Kết quả baseline      |
| ------------ | ----------------- | ------------------ | ----------------------- |
| ID Not Null / Unique | Uniqueness/Completeness | 100% pass | Pass |
| age_days <= 180 | Timeliness | Max 180 | Fail (có 1 record trễ hạn) |

### Freshness

| Thuộc tính               | Giá trị                           |
| -------------------------- | ----------------------------------- |
| Trạng thái baseline      | Stale |
| Lý do                     | Có 1 dòng dữ liệu xuất bản quá 180 ngày (2026-03-28) |

## 9. Corruption scenarios và repair

| Corruption         | Cách tạo | Quality signal kỳ vọng | Tác động thực tế | Cách repair   |
| ------------------ | ---------- | ------------------------ | --------------------- | -------------- |
| Blank Summary | Xóa summary rỗng | GE check Length Fail | F1 & Hit Rate giảm | Build lại từ RAW |
| Noise injection | Nối thêm chuỗi vô nghĩa | Chất lượng embedding giảm | Hit Rate giảm | Build lại từ RAW |
| Truncated Title | Cắt Title còn 10 ký tự | Mất ngữ nghĩa | Giảm Hit Rate | Build lại từ RAW |
| Fake old date (1999) | Sửa published date | Freshness Fail | Stale Rows = 4 | Build lại từ RAW |

Giải thích cách repair:
Hệ thống repair tuân thủ nguyên tắc "Idempotent" (thực thi lại từ đầu). Thay vì tìm cách vá víu (patch) dữ liệu lỗi, pipeline tự động chạy lại module cleaning dựa trên Single Source of Truth là file RAW snapshot ban đầu.

## 10. So sánh baseline, corrupted và repaired

| Metric/signal            | Baseline | Corrupted | Repaired | Thay đổi do corruption | Mức phục hồi |
| ------------------------ | -------: | --------: | -------: | -----------------------: | --------------: |
| `retrieval_hit_rate`   |      1.0 |       0.6 |      1.0 | Giảm mạnh | Khôi phục 100% |
| `mean_token_f1`        |      0.215 |       0.161 |      0.215 | Giảm | Khôi phục 100% |
| `judge_accuracy`       |      0.333 |       0.2 |      0.333 | Giảm | Khôi phục 100% |
| Freshness status         |  1 Stale |   4 Stale |  1 Stale | Tăng số lỗi | Khôi phục 100% |

Nhân quả được hỗ trợ bởi artifacts:
1. Sửa ngày tháng thành 1999 (Corruption) → Quality báo Freshness Fail (4 dòng Stale).
2. Xóa/làm nhiễu summary & title (Corruption) → Vector mất ngữ nghĩa → LLM không tìm thấy tài liệu gốc (Hit rate giảm từ 1.0 xuống 0.6).
3. Đọc lại từ Raw (Repair action) → Tái tạo Clean data chuẩn → Agent metric recovery 100% về 1.0.

## 11. Vấn đề tích hợp quan trọng
- **Triệu chứng:** Pipeline báo cáo Heuristics metric thiếu trên báo cáo Markdown dù đã chạy thành công.
- **Nguyên nhân:** File `reporting.py` chỉ lấy key bên trong dict của module `ragas` bị skip.
- **Cách xử lý:** Bổ sung phương thức `.get()` trực tiếp từ `metrics` ở root level để hiển thị Heuristics.

## 12. Giới hạn và hướng cải thiện

| Giới hạn hiện tại | Ảnh hưởng   | Hướng cải thiện có thể kiểm chứng |
| --------------------- | -------------- | ----------------------------------------- |
| Ragas chạy quá lâu | Chi phí token cao, dễ nghẽn API | Chạy Ragas bằng mô hình nhỏ nhẹ hơn (ví dụ Ollama/Llama3). |
| Mock data ít (24 bản ghi) | VectorDB chưa bộc lộ nhược điểm truy xuất chậm | Tăng Max Results lên 1000 bản ghi để test HNSW index. |

## 13. Checklist trước khi nộp
- [x] Thông tin nhóm và repository chính xác.
- [x] Phân công khớp với module, artifact và kết quả thực tế.
- [x] Lệnh tái hiện đã được chạy lại trên phiên bản dùng để nộp.
- [x] Baseline, corrupted và repaired dùng cùng evaluation set.
- [x] Bảng metrics khớp với các file trong `data/results/`.
- [x] Quality/freshness conclusions khớp với `data/quality/`.
- [x] Không có `.env`, API key, token hoặc secret trong source, report.
