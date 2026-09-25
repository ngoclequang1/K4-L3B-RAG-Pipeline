"""Task 1 - validate the VinUniversity policy PDFs already collected."""

from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

DOCUMENTS = {
    "vinuni_student_club_operations_guidelines_2026.pdf": {
        "source_url": "https://policy.vinuni.edu.vn/all-policies/vinuni-student-club-operations-guidelines/",
    },
    "vinuni_student_social_media_guidelines_2026.pdf": {
        "source_url": "https://policy.vinuni.edu.vn/all-policies/guidelines-on-student-conduct-on-social-media-and-digital-platforms/",
    },
    "vinuni_student_event_representation_guidelines_2026.pdf": {
        "source_url": "https://policy.vinuni.edu.vn/all-policies/guidelines-for-students-representing-and-organizing-events-under-the-vinuniversity-name/",
    },
}


def setup_directory() -> None:
    """Create the directory for original legal documents."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def _validate_pdf(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Missing legal document: {path.name}")
    if path.stat().st_size <= 1024:
        raise ValueError(f"Legal document is too small: {path.name}")
    with path.open("rb") as file:
        if file.read(5) != b"%PDF-":
            raise ValueError(f"File is not a valid PDF: {path.name}")


def download_documents() -> None:
    """Validate the manually collected corpus without requiring network access."""
    setup_directory()
    missing = [filename for filename in DOCUMENTS if not (DATA_DIR / filename).is_file()]
    if missing:
        instructions = "\n".join(
            f"- {filename}: {DOCUMENTS[filename]['source_url']}"
            for filename in missing
        )
        raise FileNotFoundError(
            f"Missing {len(missing)} legal document(s) in {DATA_DIR}. "
            f"Download them from the official source pages:\n{instructions}"
        )

    for filename, details in DOCUMENTS.items():
        path = DATA_DIR / filename
        _validate_pdf(path)
        print(f"Validated: {path.name} ({path.stat().st_size:,} bytes)")
        print(f"  Source: {details['source_url']}")

    print(f"Task 1 complete: {len(DOCUMENTS)} legal documents are ready.")


if __name__ == "__main__":
    download_documents()
