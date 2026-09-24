"""
Task 7 — Reciprocal Rank Fusion.

RRF gộp nhiều bảng xếp hạng mà không cộng trực tiếp cosine score với BM25
score. Công thức: RRF(d) = sum(1 / (k + rank)), rank bắt đầu từ 1.

Lưu ý: RRF score chỉ phản ánh thứ hạng, không dùng để quyết định fallback.

-> Dùng Jina hoặc self host hoặc bất cứ công cụ nào bạn quen
"""


def rerank_rrf(
    ranked_lists: list[list[dict]],
    top_k: int = 5,
    k: int = 60,
) -> list[dict]:
    """Fuse nhiều ranked lists và trả hybrid SearchResult."""
    scores: dict[str, float] = {}
    items: dict[str, dict] = {}

    for ranked_list in ranked_lists:
        # Rank bắt đầu từ 1 theo công thức RRF: 1 / (k + rank)
        for rank, item in enumerate(ranked_list, start=1):
            item_id = item["id"]
            scores[item_id] = scores.get(item_id, 0.0) + (1.0 / (k + rank))
            
            # Lưu trữ thông tin item (giữ lại bản ghi nếu chưa có)
            if item_id not in items:
                items[item_id] = item

    # Sắp xếp danh sách item_id theo điểm RRF giảm dần
    ranked_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

    results = []
    for item_id in ranked_ids[:top_k]:
        # Dùng .copy() để tránh sửa trực tiếp dict gốc
        result = items[item_id].copy()
        result["score"] = scores[item_id]
        result["retrieval_method"] = "hybrid"
        results.append(result)

    return results


if __name__ == "__main__":
    # Test mẫu để kiểm tra hoạt động
    list_dense = [
        {"id": "doc1", "content": "A", "score": 0.9, "metadata": {}},
        {"id": "doc2", "content": "B", "score": 0.8, "metadata": {}},
    ]
    list_bm25 = [
        {"id": "doc2", "content": "B", "score": 5.2, "metadata": {}},
        {"id": "doc3", "content": "C", "score": 4.1, "metadata": {}},
    ]
    
    hybrid_results = rerank_rrf([list_dense, list_bm25], top_k=2)
    for res in hybrid_results:
        print(res)
