# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| --- | --- |
| Họ và tên | Trần Xuân Tùng |
| MSSV | 2A202602787 |
| Khóa/Lớp | K4 |
| Tên nhóm | Arrogant Idiota |
| Vai trò chính | làm tất cả các việc do là thành viên duy nhất |
| Repository | https://github.com/xuantungtran64-ai/K4-L3B-DAY10-ArrogantIdiota-DataPipelineDataObservability |
| Ngày hoàn thành | 2026-09-26 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| lấy và làm sạch dữ liệu | `crossref.py`, `cleaning.py` | file json từ api | `papers_clean.csv` | hoàn thành |
| theo dõi chất lượng | `quality.py`, `reporting.py` | `papers_clean.csv` | `quality_report.json` | hoàn thành |
| chạy luồng dữ liệu | `phase1.py`, `corruption.py` | toàn bộ mã nguồn | báo cáo markdown | hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| --- | --- | --- |
| không có do làm một mình | không | không |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --- | --- | --- | --- |
| cài đặt luật kiểm tra dữ liệu | `quality.py` | file báo cáo chất lượng | chạy `run_phase1.py` ra `baseline_quality.json` |
| xây dựng luồng tự sửa lỗi | `corruption_flow.py` | dữ liệu sạch và các chỉ số | chạy `run_corruption_flow.py` ra `corruption_report.md` |

Hệ thống xuất ra báo cáo chất lượng dữ liệu để biết file nào đang bị lỗi

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Bài toán yêu cầu làm một đường ống tự động lấy bài báo khoa học về làm sạch và phát hiện lỗi dữ liệu trước khi đưa cho AI

### Cách triển khai

sử dùng pandas để xử lý dữ liệu để tăng tốc độ thay vì lặp từng dòng
với phần kiểm tra thì dùng thư viện great expectations bản mới để viết luật trực tiếp trong code luôn không cần file cấu hình nặng
lúc dữ liệu bị hỏng thì hệ thống sẽ tự lấy lại từ bản gốc thay vì cố sửa file lỗi

### Input, output và contract

| Thành phần | Mô tả |
| --- | --- |
| Input | dữ liệu thô tải từ api |
| Output | file csv đã được làm sạch |
| Module phụ thuộc | luồng tải dữ liệu |
| Module sử dụng output | luồng nhúng dữ liệu vào vector |
| Điều kiện lỗi cần xử lý | file bị thiếu thông tin hoặc sai ngày tháng |

### Cách xác minh

```bash
python scripts/run_phase1.py
```

- **Kết quả mong đợi:** dữ liệu được xử lý và lưu lại
- **Kết quả thực tế:** code chạy ổn như dự tính
- **Artifact/log:** `data/reports/baseline_quality.json`

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** cần tìm cách kiểm tra dữ liệu xem có đạt chuẩn không
- **Các phương án đã cân nhắc:** tự viết code để check hoặc dùng thư viện ngoài
- **Phương án đã chọn:** dùng great expectations
- **Lý do:** thư viện này in ra báo cáo rõ ràng và dễ nâng cấp về sau
- **Bằng chứng quyết định phù hợp:** file json trả về báo đúng chỗ bị lỗi đọc phát hiểu luôn

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** máy bị đơ lúc cài thư viện do ragas và langchain cắn nhau
- **Lệnh hoặc bước tái hiện:** gõ lệnh pip install requirements
- **Nguyên nhân gốc:** mấy thư viện này đòi hỏi phiên bản phụ thuộc chồng chéo
- **Cách xử lý:** chuyển sang dùng uv để tải gói
- **Cách xác minh sau khi sửa:** gõ uv sync thấy cài vèo vèo xong luôn
- **Điều học được:** chốt phiên bản thư viện tử tế rất quan trọng để không bị lỗi môi trường

## 7. Hiểu biết về luồng end-to-end

**Câu trả lời:**

Dữ liệu tải từ api sẽ được dọn dẹp sạch sẽ rồi gộp lại thành câu chữ sau đó đưa qua mô hình minilm biến thành vector và tống vào chroma
câu trả lời chuẩn dùng để so xem hệ thống lôi bài báo lên có đúng với đáp án không
kiểm tra chất lượng là xem dữ liệu có bị rỗng hay sai cấu trúc không còn kiểm tra độ mới là xem bài báo có bị cũ quá không
phải dùng chung bộ test để chắc chắn điểm bị tụt là do dữ liệu hỏng chứ không phải tại câu hỏi khó
sửa lỗi thành công là lúc điểm số của mô hình quay lại bằng mức lúc đầu

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| --- | --- | --- | --- | --- |
| `retrieval_hit_rate` | 1.0 | 0.6 | 1.0 | dữ liệu hỏng làm điểm tụt hẳn |
| `mean_token_f1` | trống | trống | trống | tôi chưa tính cái này |
| `judge_accuracy` | trống | trống | trống | chưa làm phần này |
| `mean_judge_score` | trống | trống | trống | tương tự ở trên |
| Quality checks | pass | fail | pass | báo cáo bắt được đúng lỗi |
| Freshness status | pass | fail | pass | phát hiện được bài báo cũ rích |

### Kết luận từ số liệu

1. dữ liệu bị hỏng -> báo lỗi -> điểm số ai giảm thê thảm
2. chạy luồng sửa lỗi -> báo cáo hết lỗi -> điểm số quay về như cũ

việc phá hỏng chữ trong bài làm vector bị sai hướng nhiều nhất vì hệ thống này tìm kiếm bằng chữ

lúc đầu tôi nghĩ nó sẽ tự đoán chữ để sửa lỗi nhưng hóa ra vứt đi tải lại từ bản gốc vừa dễ vừa an toàn hơn

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. dữ liệu rác vào thì kết quả rác ra
2. code chạy mượt chưa chắc đã đúng nên phải có cổng kiểm tra
3. dữ liệu hỏng làm tìm kiếm sai nên câu trả lời cũng sai nốt

### Nếu có thêm thời gian

Tôi tính đưa hệ thống này lên airflow để nó tự chạy định kỳ thay vì phải gõ lệnh bằng tay

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác

**Họ và tên:** Trần Xuân Tùng
**Ngày xác nhận:** 2026-09-26
