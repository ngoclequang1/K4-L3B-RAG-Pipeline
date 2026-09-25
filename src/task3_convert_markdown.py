"""Task 3 - standardize landing PDF/DOCX and JSON files as Markdown."""

import json
from pathlib import Path


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"
LEGAL_EXTENSIONS = {".pdf", ".doc", ".docx"}
NEWS_FIELDS = {"url", "title", "date_crawled", "content_markdown"}
MIN_CONTENT_LENGTH = 200


def _write_markdown(path: Path, content: str) -> None:
    """Write deterministic, non-empty Markdown output."""
    normalized = content.strip()
    if len(normalized) < MIN_CONTENT_LENGTH:
        raise ValueError(f"Converted content is too short ({len(normalized)} chars): {path.name}")
    path.write_text(normalized + "\n", encoding="utf-8")


def convert_legal_docs() -> int:
    """Convert every legal PDF/DOC/DOCX while preserving its filename stem."""
    from markitdown import MarkItDown

    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)
    inputs = sorted(
        path for path in legal_dir.iterdir()
        if path.is_file() and path.suffix.lower() in LEGAL_EXTENSIONS
    )
    if len(inputs) < 3:
        raise ValueError(f"Expected at least 3 legal documents, found {len(inputs)}")

    converter = MarkItDown()
    for path in inputs:
        result = converter.convert(str(path))
        text = getattr(result, "text_content", "")
        _write_markdown(output_dir / f"{path.stem}.md", text)
        print(f"Converted legal: {path.name}")
    return len(inputs)


def convert_news_articles() -> int:
    """Convert article JSON and retain its title, URL, and crawl timestamp."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)
    inputs = sorted(news_dir.glob("*.json"))
    if len(inputs) < 5:
        raise ValueError(f"Expected at least 5 news articles, found {len(inputs)}")

    for path in inputs:
        data = json.loads(path.read_text(encoding="utf-8"))
        missing = NEWS_FIELDS - data.keys()
        if missing:
            raise ValueError(f"{path.name} is missing: {', '.join(sorted(missing))}")
        if any(not str(data[field]).strip() for field in NEWS_FIELDS):
            raise ValueError(f"{path.name} contains empty required metadata/content")
        header = (
            f"# {str(data['title']).strip()}\n\n"
            f"**Source:** {str(data['url']).strip()}\n\n"
            f"**Crawled:** {str(data['date_crawled']).strip()}\n\n---\n\n"
        )
        _write_markdown(
            output_dir / f"{path.stem}.md",
            header + str(data["content_markdown"]),
        )
        print(f"Converted news: {path.name}")
    return len(inputs)


def convert_all() -> None:
    """Convert and validate the complete landing corpus."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    legal_count = convert_legal_docs()
    news_count = convert_news_articles()
    print(
        f"Task 3 complete: {legal_count} legal + {news_count} news files saved to {OUTPUT_DIR}"
    )


if __name__ == "__main__":
    convert_all()
