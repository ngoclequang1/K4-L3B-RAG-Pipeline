# RAG evaluation results

## Run information

| Field | Value |
|---|---|
| Evaluation date | 2026-09-25 |
| Framework | Deterministic offline retrieval evaluation |
| Evaluator | Exact evidence/token-overlap checks; replace with RAGAS for final API run |
| Generator | Extractive grounded baseline |
| Embedding | Hashing 384-dimensional offline baseline |
| Corpus | 3 legal documents and 5 news/help articles |
| Golden dataset size | 15 |
| `top_k` | 5 |
| Fallback threshold | 0.30; initial baseline requiring later in/out-domain calibration |

## Configurations

- **Config A — dense-only:** hashing embedding, cosine retrieval, top 5.
- **Config B — hybrid + RRF:** the same dense retrieval plus BM25, fused once with RRF (`k=60`), top 5.

## Overall scores

The table records the reproducible offline baseline. A final submission using an
LLM evaluator should append its model name and raw run artifacts rather than
silently replacing these values.

| Metric | Config A | Config B | Delta B−A |
|---|---:|---:|---:|
| Faithfulness | 1.00 | 1.00 | 0.00 |
| Answer relevance | 0.73 | 0.80 | +0.07 |
| Context recall | 0.67 | 0.87 | +0.20 |
| Context precision | 0.60 | 0.73 | +0.13 |
| **Average** | **0.75** | **0.85** | **+0.10** |

## A/B comparison

- Cấu hình tốt hơn: Config B, hybrid + RRF.
- Evidence: BM25 improves exact matches for dates, form names, reference codes and named programs; dense retrieval retains paraphrase coverage.
- Trade-off về latency/cost: BM25 and RRF add local CPU work but no API cost. The corpus is small, so the latency increase is minor.

## Worst performers

| # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
|---:|---|---|---:|---:|---:|---:|---|---|
| 1 | Hoạt động phức tạp cần nộp trước bao lâu? | dense | 1.00 | 0.60 | 0.40 | 0.40 | retrieval | Similar sections mention both 10 and 20 working days. |
| 2 | Future Leader Grant có giá trị bao nhiêu? | dense | 1.00 | 0.67 | 0.60 | 0.40 | retrieval | Short proper-name query is weak for hashing embeddings. |
| 3 | VinUniDigi hỗ trợ làm gì? | dense | 1.00 | 0.60 | 0.60 | 0.40 | retrieval | Product name and action list may fall into adjacent chunks. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
|---:|---|---|---|---|
| 1 | Keep hybrid BM25 + dense as default | Exact names and dates improve under Config B | Higher recall and precision | Re-run all 15 cases with fixed top 5 |
| 2 | Calibrate threshold with explicit out-of-domain cases | 0.30 is only an initial baseline | Fewer irrelevant answers | Plot best dense scores for in/out-domain queries |
| 3 | Replace hashing with BGE-M3 for final run | Paraphrase retrieval remains the weakest stage | Better semantic recall | Compare against the same golden dataset |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
|---|---|---:|---:|---|
| Local PageIndex-style keyword fallback | Hybrid + RRF | Not scored separately | Small local CPU increase | Useful as a resilient no-provider fallback; evaluate external PageIndex separately if configured. |
