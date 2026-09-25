"""Task 2 - crawl public VinUniversity articles into validated JSON."""

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    "https://vinuni.edu.vn/week-of-welcome-2026/",
    "https://registrar.vinuni.edu.vn/2026/06/29/announcement-launch-of-the-new-student-portal-for-summer-2026-course-registration/",
    "https://vinuni.edu.vn/student_life/student-clubs-associations/",
    "https://admissions.vinuni.edu.vn/scholarship-and-financial-aid/current-students/",
    "https://vinuni.edu.vn/advancing-interdisciplinary-solutions-at-the-vinuni-research-day-bootcamp-2026/",
]

REQUIRED_FIELDS = {"url", "title", "date_crawled", "content_markdown"}


def _markdown_text(value: Any) -> str:
    """Support both string and MarkdownGenerationResult Crawl4AI outputs."""
    if isinstance(value, str):
        return value.strip()
    for attribute in ("fit_markdown", "raw_markdown"):
        text = getattr(value, attribute, None)
        if text:
            return str(text).strip()
    return str(value or "").strip()


def _validate_article(article: object, expected_url: str | None = None) -> None:
    if not isinstance(article, dict):
        raise ValueError("Article JSON must be an object")
    missing = REQUIRED_FIELDS - article.keys()
    if missing:
        raise ValueError(f"Missing fields: {', '.join(sorted(missing))}")
    for field in REQUIRED_FIELDS:
        if not str(article[field]).strip():
            raise ValueError(f"Empty field: {field}")
    if expected_url and article["url"] != expected_url:
        raise ValueError(f"Cached URL does not match: {article['url']}")


async def crawl_article(url: str) -> dict:
    """Crawl one page and return the required landing-data schema."""
    from crawl4ai import AsyncWebCrawler

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
    if not getattr(result, "success", True):
        raise RuntimeError(getattr(result, "error_message", "Crawl failed"))

    metadata = getattr(result, "metadata", None) or {}
    article = {
        "url": url,
        "title": str(metadata.get("title") or url.rstrip("/").rsplit("/", 1)[-1]),
        "date_crawled": datetime.now(timezone.utc).astimezone().isoformat(),
        "content_markdown": _markdown_text(getattr(result, "markdown", "")),
    }
    _validate_article(article, expected_url=url)
    return article


async def crawl_all(refresh: bool = False) -> None:
    """Collect all configured sources; reuse valid JSON unless refreshing."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []

    for index, url in enumerate(ARTICLE_URLS, 1):
        output = DATA_DIR / f"article_{index:02d}.json"
        try:
            if output.exists() and not refresh:
                article = json.loads(output.read_text(encoding="utf-8"))
                _validate_article(article, expected_url=url)
                print(f"Validated cached article: {output.name}")
                continue

            article = await crawl_article(url)
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(f"Saved: {output.name}")
        except Exception as error:
            failures.append(f"{url}: {error}")

    if failures:
        raise RuntimeError("Task 2 failed:\n- " + "\n- ".join(failures))
    print(f"Task 2 complete: {len(ARTICLE_URLS)} news articles are ready.")


if __name__ == "__main__":
    refresh = os.getenv("RAG_REFRESH_CRAWL", "").lower() in {"1", "true", "yes"}
    asyncio.run(crawl_all(refresh=refresh))
