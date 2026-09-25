"""Task 4 - load, chunk, embed, and index the standardized corpus."""

import hashlib
import math
import os
import re
from pathlib import Path

from dotenv import load_dotenv

from .contracts import validate_document


load_dotenv()

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_DIM = 384
COLLECTION_NAME = "rag_documents"

_MODEL = None


def _hash_embedding(text: str) -> list[float]:
    """Deterministic offline embedding used when no model provider is selected."""
    vector = [0.0] * EMBEDDING_DIM
    tokens = re.findall(r"\w+", text.casefold(), flags=re.UNICODE)
    features = tokens + [f"{a}_{b}" for a, b in zip(tokens, tokens[1:])]
    for feature in features:
        digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
        value = int.from_bytes(digest, "big")
        vector[value % EMBEDDING_DIM] += 1.0 if value & 1 else -1.0
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed texts with the provider shared by indexing and semantic search."""
    if not texts:
        return []
    provider = os.getenv("EMBEDDING_PROVIDER", "hashing").casefold()
    if provider in {"hashing", "local", "offline"}:
        return [_hash_embedding(text) for text in texts]
    if provider == "sentence_transformers":
        global _MODEL
        if _MODEL is None:
            from sentence_transformers import SentenceTransformer

            _MODEL = SentenceTransformer(EMBEDDING_MODEL)
        return _MODEL.encode(texts, normalize_embeddings=True).tolist()
    if provider == "openai":
        from openai import OpenAI

        model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        response = OpenAI().embeddings.create(model=model, input=texts)
        return [item.embedding for item in sorted(response.data, key=lambda item: item.index)]
    if provider == "gemini":
        from google import genai

        model = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
        response = genai.Client().models.embed_content(model=model, contents=texts)
        return [list(item.values) for item in response.embeddings]
    raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {provider}")


def get_collection():
    """Open the persistent Chroma collection configured for cosine distance."""
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def _extract_metadata(path: Path, content: str) -> dict:
    title_match = re.search(r"^#\s+(.+)$", content, flags=re.MULTILINE)
    source_match = re.search(
        r"^(?:\*\*)?(?:Source|Source URL)(?:\*\*)?:\s*(https?://\S+)",
        content,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    relative = path.relative_to(STANDARDIZED_DIR)
    return {
        "source": relative.as_posix(),
        "title": title_match.group(1).strip() if title_match else path.stem.replace("_", " "),
        "doc_type": "legal" if relative.parts[0] == "legal" else "news",
        "url": source_match.group(1).rstrip(")") if source_match else None,
    }


def load_documents() -> list[dict]:
    """Load every non-empty Markdown file as a contract-compliant Document."""
    documents: list[dict] = []
    if not STANDARDIZED_DIR.is_dir():
        raise FileNotFoundError(f"Missing standardized corpus: {STANDARDIZED_DIR}")
    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        relative = path.relative_to(STANDARDIZED_DIR).as_posix()
        document = {
            "id": relative,
            "content": content,
            "metadata": _extract_metadata(path, content),
        }
        validate_document(document)
        documents.append(document)
    if not documents:
        raise ValueError("No standardized Markdown documents were found")
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Recursively split documents while preserving stable IDs and metadata."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks: list[dict] = []
    for document in documents:
        validate_document(document)
        for index, text in enumerate(splitter.split_text(document["content"])):
            if not text.strip():
                continue
            chunk = {
                "id": f"{document['id']}::chunk-{index}",
                "content": text.strip(),
                "metadata": {**document["metadata"], "chunk_index": index},
            }
            validate_document(chunk, require_chunk=True)
            chunks.append(chunk)
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Return new chunk dictionaries containing matching embedding vectors."""
    vectors = embed_texts([chunk["content"] for chunk in chunks])
    if len(vectors) != len(chunks):
        raise ValueError("Embedding provider returned an unexpected vector count")
    return [{**chunk, "embedding": vector} for chunk, vector in zip(chunks, vectors)]


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert the complete corpus and remove stale IDs from earlier runs."""
    if not chunks:
        raise ValueError("Cannot index an empty chunk list")
    collection = get_collection()
    current_ids = {chunk["id"] for chunk in chunks}
    stored_ids = set(collection.get(include=[]).get("ids", []))
    stale_ids = sorted(stored_ids - current_ids)
    if stale_ids:
        collection.delete(ids=stale_ids)
    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["content"] for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        metadatas=[
            {key: ("" if value is None else value) for key, value in chunk["metadata"].items()}
            for chunk in chunks
        ],
    )


def run_pipeline() -> None:
    documents = load_documents()
    chunks = chunk_documents(documents)
    index_to_vectorstore(embed_chunks(chunks))
    print(f"Indexed {len(chunks)} chunks from {len(documents)} documents")


if __name__ == "__main__":
    run_pipeline()
