"""Task 7 - Reciprocal Rank Fusion for dense and lexical rankings."""


def rerank_rrf(
    ranked_lists: list[list[dict]],
    top_k: int = 5,
    k: int = 60,
) -> list[dict]:
    """Fuse rankings once using sum(1 / (k + rank)), rank starting at one."""
    if top_k <= 0:
        return []
    if k < 0:
        raise ValueError("k must be non-negative")
    scores: dict[str, float] = {}
    items: dict[str, dict] = {}
    first_seen: dict[str, int] = {}
    position = 0
    for ranked_list in ranked_lists:
        seen_in_list: set[str] = set()
        for rank, item in enumerate(ranked_list, 1):
            item_id = item["id"]
            if item_id in seen_in_list:
                continue
            seen_in_list.add(item_id)
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank)
            items.setdefault(item_id, item)
            first_seen.setdefault(item_id, position)
            position += 1
    ranked_ids = sorted(scores, key=lambda item_id: (-scores[item_id], first_seen[item_id]))
    results: list[dict] = []
    for item_id in ranked_ids[:top_k]:
        result = {**items[item_id]}
        result["metadata"] = dict(result["metadata"])
        result["score"] = scores[item_id]
        result["retrieval_method"] = "hybrid"
        results.append(result)
    return results


if __name__ == "__main__":
    print("RRF is ready.")
