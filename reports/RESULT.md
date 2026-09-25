# Kết quả đánh giá hệ thống RAG (RAG Evaluation Results)

> Báo cáo đánh giá chi tiết (canonical evaluation report) được duy trì chính thức tại tệp `group_project/evaluation/RESULT.md` cùng với tập dữ liệu kiểm thử chuẩn 15 câu hỏi (15-case golden dataset).

---

## 1. Kết quả điểm số tổng quan (Overall Scores)

Thử nghiệm đánh giá offline baseline (có tính lặp lại) đạt kết quả trung bình **0.75** đối với cấu hình chỉ dùng Semantic/Dense Retrieval, và tăng lên **0.85** khi sử dụng Hybrid Retrieval (BM25 + Dense) kết hợp thuật toán xếp hạng Reciprocal Rank Fusion (RRF, $k=60$).

| Chỉ số đánh giá (Metric) | Config A (Dense-Only) | Config B (Hybrid + RRF) | Mức chênh lệch (Delta B−A) |
| :--- | :---: | :---: | :---: |
| **Faithfulness** | 1.00 | 1.00 | 0.00 |
| **Answer Relevance** | 0.73 | 0.80 | +0.07 |
| **Context Recall** | 0.67 | 0.87 | +0.20 |
| **Context Precision** | 0.60 | 0.73 | +0.13 |
| **ĐIỂM TRUNG BÌNH (Average)** | **0.75** | **0.85** | **+0.10** |

---

## 2. So sánh A/B (A/B Comparison)

- **Cấu hình vượt trội:** Cấu hình **Hybrid + RRF (Config B)** đem lại hiệu năng truy xuất vượt trội hơn hẳn.
- **Ưu điểm chính:** Khả năng truy xuất chính xác cao đối với các câu hỏi chứa mốc thời gian/ngày tháng, tên biểu mẫu, mã tài liệu tham chiếu, tên chương trình và thuật ngữ chính sách chuyên biệt nhờ sự hỗ trợ của BM25. Trong khi đó, Dense Search giữ vai trò phủ ngữ nghĩa và xử lý diễn đạt lại (paraphrase).
- **Chi phí & Độ trễ (Cost & Latency):** Phương pháp Hybrid chỉ làm tăng thêm một lượng nhỏ tài nguyên tính toán trên CPU nội bộ (local) và **hoàn toàn không làm phát sinh thêm chi phí API**.

---

## 3. Phân tích các trường hợp kém nhất (Worst Performers)

Các trường hợp có chỉ số thấp nhất tập trung vào 3 nhóm nguyên nhân chính:
1. **Nhiễu thông tin song song:** Các đoạn văn bản có cấu trúc tương tự nhau cùng đề cập đến các mốc thời gian khác nhau (ví dụ: mốc 10 ngày làm việc vs 20 ngày làm việc).
2. **Từ khóa tên riêng ngắn:** Truy vấn chứa tên riêng ngắn (ví dụ: *"Future Leader Grant"*) khó biểu diễn chính xác qua vector embedding dạng thô/hashing.
3. **Hiện tượng đứt gãy Context:** Thông tin về tên dịch vụ/sản phẩm và danh sách tính năng chi tiết bị phân tách nằm ở 2 đoạn chunks liền kề.

*(Chi tiết phân tích nguyên nhân gốc rễ cho từng trường hợp được ghi nhận tại báo cáo chuẩn `RESULT.md`).*

---

## 4. Khuyến nghị phát triển (Recommendations)

1. **Duy trì Hybrid Retrieval làm mặc định:** Đặt mô hình Hybrid (BM25 + Dense Search + RRF) làm phương thức truy xuất mặc định cho toàn bộ Pipeline Production.
2. **Căn chỉnh ngưỡng Fallback (Threshold Calibration):** Thực hiện căn chỉnh lại ngưỡng fallback $0.30$ dựa trên tập câu hỏi mở rộng gồm cả truy vấn trong miền (in-domain) và ngoài miền (out-of-domain) để tối ưu việc chuyển giao sang PageIndex Vectorless Fallback.
3. **Nâng cấp mô hình Embedding:** So sánh và chuyển đổi từ baseline hashing offline sang mô hình embedding chính thức `BAAI/bge-m3` trên cùng tập dữ liệu Golden Dataset trước buổi Live Demo để tối đa hóa chỉ số Semantic Recall.