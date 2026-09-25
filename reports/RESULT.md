# RAG evaluation results

The canonical evaluation report is maintained at
`group_project/evaluation/RESULT.md` alongside the 15-case golden dataset.

## Overall scores

The external OpenAI API run used `text-embedding-3-small` and `gpt-4o-mini`
across 15 golden questions (30 generated answers). Dense-only averaged 0.7563;
hybrid BM25 + RRF averaged 0.7475. Raw per-case results are stored in
`group_project/evaluation/api_evaluation_results.json`.

## A/B comparison

Dense-only performed better by 0.0088 overall in this run. Hybrid improved
answer relevance by 0.0030, but context precision fell by 0.0267. Retrieval
latency was 0.7794 seconds for dense and 0.7829 seconds for hybrid.

## Worst performers

The weakest case was the Vietnamese wording of the 10-member club requirement:
both configurations missed the English evidence and safely refused. The same
question in English succeeded with a valid citation. Detailed per-case analysis
is recorded in the canonical report.

## Recommendations

Test `top_k=3` to improve precision, tune BM25 before selecting hybrid as the
default, and calibrate the fallback threshold on additional in-domain and
out-of-domain questions.
