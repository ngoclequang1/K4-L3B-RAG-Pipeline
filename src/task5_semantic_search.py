"""
Task 5 — Semantic search.

Embed query bằng chính hàm của Task 4, query ChromaDB và đổi cosine distance
thành similarity. Output phải theo SearchResult, sort giảm dần và không quá top_k.
"""

from .task4_chunking_indexing import embed_texts, get_collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về dense SearchResult theo score giảm dần."""
    # Tạo vector embedding cho câu query
    query_vector = embed_texts([query])[0]
    
    # Truy vấn ChromaDB
    collection = get_collection()
    
    # Đảm bảo n_results không vượt quá số lượng bản ghi hiện có trong collection
    count = collection.count()
    if count == 0:
        return []
    
    actual_k = min(top_k, count)
    
    response = collection.query(
        query_embeddings=[query_vector],
        n_results=actual_k,
        include=["documents", "metadatas", "distances"],
    )
    
    results = []
    # Kiểm tra nếu response trả về kết quả hợp lệ
    if response and response.get("ids") and len(response["ids"]) > 0:
        for item_id, content, metadata, distance in zip(
            response["ids"][0],
            response["documents"][0],
            response["metadatas"][0],
            response["distances"][0],
        ):
            # Với ChromaDB space="cosine", distance = 1.0 - cosine_similarity
            # Do đó score (cosine similarity) = 1.0 - distance
            score = max(0.0, 1.0 - float(distance))
            
            results.append({
                "id": item_id,
                "content": content,
                "score": score,
                "metadata": metadata,
                "retrieval_method": "dense",
            })
            
    # Sắp xếp kết quả theo score giảm dần và lấy top_k
    return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]


if __name__ == "__main__":
    for result in semantic_search("test query", top_k=3):
        print(result)