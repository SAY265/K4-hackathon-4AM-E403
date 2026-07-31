"""Extract PDF pages into the citation format expected by QuizRequest."""

from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path
from typing import BinaryIO


def extract_pdf(pdf_path: Path) -> str:
    with pdf_path.open("rb") as pdf_file:
        pages = extract_pages(pdf_file)
    return "\n\n".join(
        format_page(page_number, text)
        for page_number, text in pages.items()
        if text.strip()
    )


def extract_pages(pdf_file: BinaryIO) -> dict[int, str]:
    try:
        from pypdf import PdfReader
    except ImportError as error:
        raise RuntimeError(
            "pypdf is required; run: python -m pip install -r "
            "codebase/requirements.txt"
        ) from error

    reader = PdfReader(pdf_file)
    return {
        number: " ".join((page.extract_text() or "").split())
        for number, page in enumerate(reader.pages, start=1)
    }


def extract_pages_from_bytes(pdf_bytes: bytes) -> dict[int, str]:
    if not pdf_bytes:
        raise ValueError("PDF upload is empty")
    try:
        return extract_pages(BytesIO(pdf_bytes))
    except RuntimeError:
        raise
    except Exception as error:
        raise ValueError("Cannot read uploaded PDF") from error


def format_page(page_number: int, text: str) -> str:
    normalized = " ".join(text.split())
    if not normalized:
        return ""
    return f"[Slide trang {page_number}] {normalized}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    extracted = extract_pdf(arguments.pdf)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(extracted, encoding="utf-8")
    print(f"Saved {arguments.output}")


if __name__ == "__main__":
    main()
