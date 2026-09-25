# Individual contribution report

## Thông tin

- Họ và tên: **Lê Quang Ngọc**
- Mã học viên: **2A202602664**
- Nhóm: **kocoten**
- Repository/branch: `https://github.com/ngoclequang1/K4-L3B-RAG-Pipeline` / `main`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Data collection & standardization | Hoàn thiện kiểm tra 3 PDF, xử lý 5 bài viết JSON và chuyển dữ liệu sang Markdown có metadata | `src/task1_collect_legal_docs.py`, `src/task2_crawl_news.py`, `src/task3_convert_markdown.py`; commit `881cfe1` | Done |
| Index & retrieval | Hoàn thiện load/chunk/index, dense search, BM25, RRF và fallback dựa trên dense cosine score | `src/task4_chunking_indexing.py` đến `src/task9_retrieval_pipeline.py`; commits `881cfe1`, `afd1217` | Done |
| Generation & UI | Hoàn thiện generation có citation, safe refusal và giao diện Streamlit hiển thị nguồn/score | `src/task10_generation.py`, `app.py`; commits `881cfe1`, `afd1217` | Done |
| Evaluation | Tạo golden dataset 15 câu; chạy 30 generation A/B bằng OpenAI API; lưu raw results, latency và phân tích lỗi | `group_project/evaluation/golden_dataset.json`, `group_project/evaluation/api_evaluation_results.json`, `group_project/evaluation/RESULT.md` | Done |
| Integration & bug fixing | Xử lý conflict marker, kiểm tra contract và acceptance toàn pipeline | commits `881cfe1`, `afd1217` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Dùng hybrid retrieval gồm dense search và BM25, sau đó fuse đúng một lần bằng RRF.  
   **Lý do/evidence:** BM25 phù hợp với mã tài liệu, tên chương trình và thời hạn; dense retrieval hỗ trợ câu hỏi diễn đạt lại. Contract tests xác nhận RRF đúng công thức và không trả ID trùng.  
   **Trade-off:** Tốn thêm một bước retrieval và CPU so với dense-only, nhưng không phát sinh API cost và tăng khả năng tìm đúng bằng chứng.

2. **Quyết định:** Kiểm thử và đánh giá bản tích hợp thật bằng OpenAI `text-embedding-3-small` và `gpt-4o-mini`, đồng thời giữ fallback offline cho phát triển.  
   **Lý do/evidence:** API run đã index 53 chunks bằng vector 1536 chiều, tạo 30 câu trả lời A/B và lưu raw artifact. Dense-only đạt 0.7563, hybrid đạt 0.7475; smoke test tiếng Anh trả đúng “10 members” kèm citation.  
   **Trade-off:** API thật phản ánh pipeline triển khai tốt hơn nhưng phát sinh latency/quota; kết quả còn phụ thuộc model, ngôn ngữ query và chỉ là một lần chạy trên 15 câu.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: `pytest -q`; 15 golden questions cho dense-only và hybrid + RRF; smoke query tiếng Anh về số thành viên tối thiểu của câu lạc bộ.
- Kết quả: **20 tests passed**; OpenAI index thành công **53 chunks từ 8 documents**, embedding dimension **1536**; 30 API generations hoàn tất. Dense-only đạt trung bình **0.7563**, hybrid đạt **0.7475**; retrieval latency trung bình lần lượt **0.7794 s** và **0.7829 s**.
- Lỗi đã phát hiện và cách xử lý: sửa conflict Git trong Task 6–10; cấu hình Windows certificate store cho proxy TLS; phát hiện khoảng trống cross-language khi câu tiếng Việt không retrieve được evidence tiếng Anh, trong khi câu tiếng Anh tương đương trả đúng và có citation.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: evaluation mới chạy một lần trên 15 câu và có 2 safe refusals cho cùng một câu hỏi tiếng Việt.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: hiệu chỉnh `top_k` và threshold bằng tập câu hỏi in-domain/out-of-domain lớn hơn.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: **25/09/2026**
- Tên thành viên: **Lê Quang Ngọc**
