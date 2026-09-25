# Kết quả đánh giá hệ thống RAG (RAG Evaluation Results)

> Báo cáo đánh giá chi tiết (canonical evaluation report) được duy trì chính thức tại tệp `group_project/evaluation/RESULT.md` cùng với tập dữ liệu kiểm thử chuẩn 15 câu hỏi (15-case golden dataset).

---

## Overall scores

The reproducible offline baseline averages 0.75 for dense-only retrieval and
0.85 for hybrid BM25 + dense retrieval with a single RRF fusion step.

## A/B comparison

Hybrid + RRF performs better on exact dates, form names, program names and
policy terminology. It adds a small amount of local CPU latency and no API cost.

## Worst performers

The weakest cases contain competing 10-day and 20-day deadlines, short proper
names such as Future Leader Grant, and content split across adjacent chunks.
Detailed per-case analysis is recorded in the canonical report.

## Recommendations

Keep hybrid retrieval as the default, calibrate the 0.30 fallback threshold on
in-domain and out-of-domain queries, and compare the offline hashing baseline
with BGE-M3 using the same golden dataset before the final demo.
