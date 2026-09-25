"""Task 3 - standardize landing PDF/DOCX and JSON files as Markdown."""

import json
import re
from pathlib import Path


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"
LEGAL_EXTENSIONS = {".pdf", ".doc", ".docx"}
NEWS_FIELDS = {"url", "title", "date_crawled", "content_markdown"}
MIN_CONTENT_LENGTH = 200


def _write_markdown(path: Path, content: str) -> None:
    normalized = content.strip()
    if len(normalized) < MIN_CONTENT_LENGTH:
        raise ValueError(f"Output is too short ({len(normalized)} characters): {path.name}")
    path.write_text(normalized + "\n", encoding="utf-8")


def _format_legal_markdown(content: str) -> str:
    """Remove PDF control characters and restore basic heading structure."""
    formatted: list[str] = []
    found_title = False
    for line in content.replace("\f", "\n").splitlines():
        text = line.strip()
        if not text:
            formatted.append("")
        elif not found_title:
            formatted.append(f"# {text}")
            found_title = True
        elif re.match(r"^\d+\.\s+\S", text):
            formatted.append(f"## {text}")
        else:
            formatted.append(text)
    return "\n".join(formatted)


def _remove_duplicate_title(content: str, title: str) -> str:
    lines = content.strip().splitlines()
    if lines and lines[0].lstrip("# ").strip() == title:
        lines.pop(0)
        while lines and not lines[0].strip():
            lines.pop(0)
    return "\n".join(lines)


def convert_legal_docs() -> int:
    """Convert all legal PDF/DOC/DOCX inputs with MarkItDown."""
    from markitdown import MarkItDown

    input_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)
    inputs = sorted(
        path for path in input_dir.iterdir()
        if path.is_file() and path.suffix.lower() in LEGAL_EXTENSIONS
    )
    if len(inputs) < 3:
        raise ValueError(f"Expected at least 3 legal documents, found {len(inputs)}")

    converter = MarkItDown()
    for path in inputs:
        result = converter.convert(str(path))
        content = _format_legal_markdown(getattr(result, "text_content", ""))
        _write_markdown(output_dir / f"{path.stem}.md", content)
        print(f"Converted legal: {path.name}")
    return len(inputs)


def convert_news_articles() -> int:
    """Convert article JSON while retaining all required source metadata."""
    input_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)
    inputs = sorted(input_dir.glob("*.json"))
    if len(inputs) < 5:
        raise ValueError(f"Expected at least 5 news articles, found {len(inputs)}")

    for path in inputs:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"{path.name} must contain a JSON object")
        missing = NEWS_FIELDS - data.keys()
        if missing:
            raise ValueError(f"{path.name} is missing: {', '.join(sorted(missing))}")
        if any(not str(data[field]).strip() for field in NEWS_FIELDS):
            raise ValueError(f"{path.name} has empty required fields")

        title = str(data["title"]).strip()
        header = (
            f"# {title}\n\n"
            f"**Source:** {str(data['url']).strip()}\n\n"
            f"**Crawled:** {str(data['date_crawled']).strip()}\n\n---\n\n"
        )
        body = _remove_duplicate_title(str(data["content_markdown"]), title)
        _write_markdown(output_dir / f"{path.stem}.md", header + body)
        print(f"Converted news: {path.name}")
    return len(inputs)


def convert_all() -> None:
    """Convert and validate the complete landing corpus."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    legal_count = convert_legal_docs()
    news_count = convert_news_articles()
    print(f"Task 3 complete: {legal_count} legal + {news_count} news files saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
