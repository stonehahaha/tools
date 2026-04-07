from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from zipfile import ZipFile, ZIP_DEFLATED

from .matcher import MatchResults, match_pages
from .pdf_parser import PageScan, scan_pdf
from .reporting import build_summary, write_report
from .team_roster import (
    DEFAULT_NAME_COLUMN,
    DEFAULT_TEAM_COLUMN,
    RosterData,
    load_roster,
)
from .writer import write_team_pdfs


@dataclass(frozen=True)
class PdfTeamSplitRequest:
    roster_path: Path | str
    pdf_path: Path | str
    output_dir: Path | str
    sheet: str | int | None = None
    name_column: str = DEFAULT_NAME_COLUMN
    team_column: str = DEFAULT_TEAM_COLUMN
    fuzzy_threshold: int = 90
    report_filename: str = "match_report.csv"


@dataclass(frozen=True)
class PdfTeamSplitResult:
    team_pdf_paths: list[Path]
    report_path: Path
    summary: dict[str, object]


def _to_path(value: Path | str) -> Path:
    return value if isinstance(value, Path) else Path(value)


def process_pdf_team_split(request: PdfTeamSplitRequest) -> PdfTeamSplitResult:
    roster = load_roster(
        request.roster_path,
        sheet=request.sheet,
        name_column=request.name_column,
        team_column=request.team_column,
    )

    page_scans = scan_pdf(request.pdf_path)
    match_results = match_pages(
        roster,
        page_scans,
        fuzzy_threshold=request.fuzzy_threshold,
    )

    written_paths = write_team_pdfs(
        request.pdf_path,
        match_results.accepted_matches,
        request.output_dir,
    )

    output_dir = _to_path(request.output_dir)
    report_path = output_dir / request.report_filename
    write_report(match_results.report_rows, report_path)

    summary = build_summary(
        roster=roster,
        page_scans=page_scans,
        match_results=match_results,
        written_files=written_paths,
        report_path=report_path,
    )

    return PdfTeamSplitResult(
        team_pdf_paths=written_paths,
        report_path=report_path,
        summary=summary,
    )


def build_result_zip(output_dir: Path | str, zip_path: Path | str) -> Path:
    output_directory = _to_path(output_dir)
    zip_file_path = _to_path(zip_path)
    zip_file_path.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(zip_file_path, "w", compression=ZIP_DEFLATED) as archive:
        for file_path in _iter_files(output_directory):
            archive.write(file_path, file_path.relative_to(output_directory))

    return zip_file_path


def _iter_files(base_dir: Path) -> Iterable[Path]:
    if not base_dir.exists():
        return []
    return (path for path in base_dir.rglob("*") if path.is_file())
