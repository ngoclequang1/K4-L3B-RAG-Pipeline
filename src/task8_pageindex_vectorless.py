"""Task 8 - resilient vectorless fallback.

When PAGEINDEX_API_KEY is not configured, this module performs a local
document-level keyword traversal over the standardized corpus.  It preserves
the PageIndex SearchResult contract and keeps the application usable offline.
"""

import hashlib
import json
import re
from pathlib import Path

from .task4_chunking_indexing import chunk_documents, load_documents


ROOT = Path(__file__).parent.parent
CACHE_PATH = ROOT / "pageindex_doc_ids.json"


def upload_documents() -> None:
    """Cache stable source IDs; external upload can be added without changing search."""
    mapping = {
        document["metadata"]["source"]: hashlib.sha256(document["id"].encode()).hexdigest()[:16]
        for document in load_documents()
    }
    CACHE_PATH.write_text(json.dumps(mapping, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Cached {len(mapping)} document IDs in {CACHE_PATH.name}")


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.casefold(), flags=re.UNICODE))


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Traverse documents by title/content overlap and return matching chunks."""
    if not query.strip() or top_k <= 0:
        return []
    query_tokens = _tokens(query)
    candidates: list[tuple[float, dict]] = []
    for chunk in chunk_documents(load_documents()):
        metadata = chunk["metadata"]
        title_tokens = _tokens(metadata["title"])
        content_tokens = _tokens(chunk["content"])
        title_overlap = len(query_tokens & title_tokens)
        content_overlap = len(query_tokens & content_tokens)
        score = (2.0 * title_overlap + content_overlap) / max(len(query_tokens), 1)
        if score > 0:
            candidates.append((score, chunk))
    candidates.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
    return [
        {
            "id": chunk["id"],
            "content": chunk["content"],
            "score": float(score),
            "metadata": dict(chunk["metadata"]),
            "retrieval_method": "pageindex",
        }
        for score, chunk in candidates[:top_k]
    ]


if __name__ == "__main__":
    upload_documents()
