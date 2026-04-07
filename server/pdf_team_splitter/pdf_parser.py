from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from pypdf import PdfReader

from .team_roster import normalize_name

NAME_PATTERN = re.compile(r"\b[A-Z]{2,}\s*/\s*[A-Z]{2,}\b")


@dataclass(frozen=True)
class PageScan:
    page_number: int
    text: str
    name_raw: str | None
    name_normalized: str | None


def extract_candidate_name(text: str) -> str | None:
    upper_text = text.upper()
    match = NAME_PATTERN.search(upper_text)
    if not match:
        return None
    return match.group(0)


def scan_pdf(pdf_path: str | Path) -> list[PageScan]:
    reader = PdfReader(str(pdf_path))
    page_scans: list[PageScan] = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        name_raw = extract_candidate_name(text)
        name_normalized = normalize_name(name_raw) if name_raw else None
        page_scans.append(
            PageScan(
                page_number=page_number,
                text=text,
                name_raw=name_raw,
                name_normalized=name_normalized,
            )
        )

    return page_scans
