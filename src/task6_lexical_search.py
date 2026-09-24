"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

import numpy as np
from rank_bm25 import BM25Okapi
from .task4_chunking_indexing import load_documents, chunk_documents

CORPUS: list[dict] = []


def _ensure_corpus_loaded():
    """Tự động load và chunk tài liệu nếu CORPUS đang rỗng."""
    global CORPUS
    if not CORPUS:
        documents = load_documents()
        CORPUS = chunk_documents(documents)


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    if not corpus:
        return None
    # Tokenize đơn giản bằng cách viết thường và split theo khoảng trắng
    tokenized = [item["content"].lower().split() for item in corpus]
    return BM25Okapi(tokenized)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    _ensure_corpus_loaded()
    
    if not CORPUS:
        return []

    bm25 = build_bm25_index(CORPUS)
    if bm25 is None:
        return []

    # Tokenize query
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)
    
    # Sắp xếp chỉ số theo điểm từ cao xuống thấp
    indices = np.argsort(scores)[::-1][:top_k]
    
    results = []
    for index in indices:
        score = float(scores[index])
        # Lọc bỏ các tài liệu có score <= 0 (không chứa từ khóa nào)
        if score <= 0:
            continue
            
        item = CORPUS[index]
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": score,
            "metadata": item["metadata"],
            "retrieval_method": "bm25",
        })
        
    return results


if __name__ == "__main__":
    for result in lexical_search("test query", top_k=3):
        print(result)
