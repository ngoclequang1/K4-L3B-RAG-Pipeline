"""Task 6 - BM25 lexical search over the same chunks used by Task 4."""

import re


CORPUS: list[dict] = []


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.casefold(), flags=re.UNICODE)


def _get_corpus() -> list[dict]:
    if CORPUS:
        return CORPUS
    from .task4_chunking_indexing import chunk_documents, load_documents

    CORPUS.extend(chunk_documents(load_documents()))
    return CORPUS


def build_bm25_index(corpus: list[dict]):
    """Build a BM25Okapi index from Task 4 chunk dictionaries."""
    from rank_bm25 import BM25Okapi

    return BM25Okapi([_tokenize(item["content"]) for item in corpus])


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Return unique BM25 SearchResults sorted by descending score."""
    if not query.strip() or top_k <= 0:
        return []
    corpus = _get_corpus()
    if not corpus:
        return []
    query_tokens = _tokenize(query)
    scores = build_bm25_index(corpus).get_scores(query_tokens)
    query_set = set(query_tokens)
    adjusted_scores = [
        float(score) + len(query_set & set(_tokenize(item["content"]))) / max(len(query_set), 1)
        for score, item in zip(scores, corpus)
    ]
    ranked_indices = sorted(range(len(corpus)), key=lambda index: (-adjusted_scores[index], index))
    results: list[dict] = []
    seen: set[str] = set()
    for index in ranked_indices:
        score = adjusted_scores[index]
        item = corpus[index]
        if score <= 0 or item["id"] in seen:
            continue
        seen.add(item["id"])
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": score,
            "metadata": dict(item["metadata"]),
            "retrieval_method": "bm25",
        })
        if len(results) >= top_k:
            break
    return results


if __name__ == "__main__":
    for result in lexical_search("student club", top_k=3):
        print(result["score"], result["metadata"]["source"])
