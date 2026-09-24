"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Hướng dẫn:
    1. Chọn chủ đề của nhóm.
    2. Tìm tối thiểu 3 tài liệu PDF/DOCX từ nguồn công khai.
    3. Lưu file gốc vào data/landing/legal/.
    4. Đặt tên không dấu và thể hiện đúng nội dung.

Ví dụ tài liệu: học phí, học bổng, ký túc xá, quy trình đăng ký.
Nếu website chặn crawler, hãy chọn nguồn công khai khác; không vượt WAF.
"""

from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents() -> None:
    """Tải ít nhất 3 PDF/DOCX từ nguồn công khai."""
    # TODO: Có thể tải thủ công hoặc dùng requests.
    #
    # from markitdown import MarkItDown
    # legal_dir = LANDING_DIR / "legal"
    # output_dir = OUTPUT_DIR / "legal"
    # output_dir.mkdir(parents=True, exist_ok=True)
    # converter = MarkItDown()
    # for path in legal_dir.iterdir():
    #     if path.suffix.lower() in {".pdf", ".doc", ".docx"}:
    #         result = converter.convert(str(path))
    #         (output_dir / f"{path.stem}.md").write_text(
    #             result.text_content, encoding="utf-8"
    #         )
    import requests

    sources = {
        "vinuni_student_club_operations_guidelines_2026.pdf": (
            "https://policy.vinuni.edu.vn/wp-content/uploads/2026/09/"
            "GDL-SAM-012-V1.0_VinUni-Student-Club-Operations-Guideline_10092026-Eng.pdf"
        ),
        "vinuni_student_social_media_guidelines_2026.pdf": (
            "https://policy.vinuni.edu.vn/wp-content/uploads/2026/08/"
            "GDL-SAM-011-V1.0_Guidelines-on-student-conduct-on-social-media-and-digital-platforms_07082026.pdf"
        ),
        "vinuni_student_event_representation_guidelines_2026.pdf": (
            "https://policy.vinuni.edu.vn/wp-content/uploads/2026/09/"
            "GDL-SAM-013-V1.0_Guidelines_Students-Representing-and-Organizing-Events-under-the-VinUniversity-Name.pdf"
        ),
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; K4-L3B-RAG-Pipeline/1.0)"
    }

    for filename, url in sources.items():
        filepath = DATA_DIR / filename
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        if not response.content:
            raise RuntimeError(f"Downloaded empty file: {filename}")

        filepath.write_bytes(response.content)
        print(f"✓ Đã tải: {filepath}")


if __name__ == "__main__":
    setup_directory()
    download_documents()
