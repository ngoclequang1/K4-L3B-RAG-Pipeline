# RAG evaluation results

## Run information

| Field | Value |
|---|---|
| Evaluation date | 2026-09-25 |
| Framework | Custom API-backed A/B evaluation with raw per-case artifact |
| Generator | OpenAI `gpt-4o-mini` |
| Embedding/evaluator | OpenAI `text-embedding-3-small` (1536 dimensions) |
| Corpus | 3 legal documents + 5 news/help articles; 53 chunks |
| Golden dataset size | 15 questions; 30 generated answers across two configurations |
| `top_k` | 5 |
| Raw artifact | `group_project/evaluation/api_evaluation_results.json` |

The run used the external OpenAI API key from `.env`. It was not the offline
hashing/extractive baseline. Faithfulness and answer relevance are embedding
similarity proxies; context recall and precision are evidence-token coverage
metrics. These numbers are reproducible run results, but should not be presented
as native RAGAS scores.

## Configurations

- **Config A — dense-only:** OpenAI embedding, cosine retrieval, top 5.
- **Config B — hybrid + RRF:** the same dense results plus BM25, fused once with RRF (`k=60`), top 5.
- Both configurations used the same corpus, questions, generator, prompt and `top_k`.

## Overall scores

| Metric | Config A | Config B | Delta B−A |
|---|---:|---:|---:|
| Faithfulness | 0.7432 | 0.7368 | -0.0064 |
| Answer relevance | 0.7887 | 0.7917 | +0.0030 |
| Context recall | 0.9068 | 0.9017 | -0.0051 |
| Context precision | 0.5867 | 0.5600 | -0.0267 |
| **Average** | **0.7563** | **0.7475** | **-0.0088** |

Average retrieval latency was **0.7794 s** for dense-only and **0.7829 s** for
hybrid. Average generation latency was **2.9710 s** and **2.8952 s** respectively.

## A/B comparison

- Cấu hình tốt hơn trong lần chạy này: **Config A — dense-only**, hơn 0.0088 điểm trung bình.
- Hybrid tăng nhẹ answer relevance (+0.0030) nhưng giảm context precision (-0.0267); BM25 đưa thêm các chunk có từ khóa liên quan nhưng không trực tiếp chứa evidence mong đợi.
- Chênh lệch retrieval latency chỉ khoảng 0.0035 giây trên corpus nhỏ, nên lựa chọn cấu hình chủ yếu phụ thuộc chất lượng thay vì chi phí/latency.
- Kết luận chỉ áp dụng cho corpus 8 tài liệu và 15 câu hiện tại; cần chạy lặp lại trước khi khẳng định ưu thế tổng quát.

## Worst performers

| # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
|---:|---|---|---:|---:|---:|---:|---|---|
| 1 | Một câu lạc bộ VinUni cần tối thiểu bao nhiêu thành viên hoạt động? | dense | 0.5266 | 0.6578 | 0.0000 | 0.0000 | retrieval | Vietnamese query did not retrieve the English evidence; generator correctly refused. |
| 2 | Một câu lạc bộ VinUni cần tối thiểu bao nhiêu thành viên hoạt động? | hybrid | 0.5292 | 0.6578 | 0.0000 | 0.0000 | retrieval | BM25 could not bridge the Vietnamese/English vocabulary gap; generator correctly refused. |
| 3 | Câu lạc bộ mới phải trải qua thời gian thử thách bao lâu? | dense | 0.6399 | 0.7104 | 1.0000 | 0.2000 | retrieval | Evidence was found, but only one of five chunks was directly relevant. |

Across 30 generations there were **2 safe refusals**, both for the first
Vietnamese question. All non-refusal answers contained `[Document N]` citations.
An English smoke-test version of the first question retrieved the correct rule
and produced the answer “10 members” with a valid citation.

## Recommendations

| Priority | Action | Evidence from API run | Expected impact | How to verify |
|---:|---|---|---|---|
| 1 | Tune `top_k` from 5 to 3 and/or add a relevance filter | Several cases had recall 1.0 but precision 0.2 | Improve context precision and reduce noise | Compare precision and faithfulness on all 15 cases |
| 2 | Tune BM25 tokenization/weighting before keeping hybrid as default | Hybrid lost 0.0267 context precision and 0.0088 overall | Preserve keyword gains without adding weak chunks | Re-run the same 15-case A/B evaluation |
| 3 | Calibrate the fallback threshold with more in-domain/out-of-domain queries | The current threshold remains an initial setting | Reduce irrelevant retrieval and unnecessary fallback | Plot dense scores and select a validated cutoff |

## Reproduction

The raw JSON contains every generated answer, source ID, per-case metrics and
latencies. API keys are not written to the artifact. Automated repository tests
were also run separately and completed with **20 passed**.
