from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from .matcher import MatchResults, ReportRow
from .pdf_parser import PageScan
from .team_roster import RosterData

REPORT_FIELDNAMES = [
    "team_name",
    "roster_name_raw",
    "roster_name_normalized",
    "match_status",
    "match_method",
    "pdf_page_number",
    "pdf_name_raw",
    "pdf_name_normalized",
    "fuzzy_score",
    "note",
]


def write_report(rows: list[ReportRow], report_path: str | Path) -> None:
    output_path = Path(report_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=REPORT_FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "team_name": row.team_name,
                    "roster_name_raw": row.roster_name_raw,
                    "roster_name_normalized": row.roster_name_normalized,
                    "match_status": row.match_status,
                    "match_method": row.match_method,
                    "pdf_page_number": row.pdf_page_number,
                    "pdf_name_raw": row.pdf_name_raw,
                    "pdf_name_normalized": row.pdf_name_normalized,
                    "fuzzy_score": row.fuzzy_score,
                    "note": row.note,
                }
            )


def build_summary(
    *,
    roster: RosterData,
    page_scans: list[PageScan],
    match_results: MatchResults,
    written_files: list[Path],
    report_path: Path,
) -> dict[str, object]:
    status_counts: dict[str, int] = {}
    for row in match_results.report_rows:
        status_counts[row.match_status] = status_counts.get(row.match_status, 0) + 1

    matched_counts = Counter(
        match.roster_name_normalized for match in match_results.accepted_matches
    )
    roster_not_found_count = sum(
        max(group.expected_count - matched_counts.get(name_normalized, 0), 0)
        for name_normalized, group in roster.groups_by_name.items()
    )

    return {
        "roster_row_count": len(roster.entries),
        "unique_roster_passenger_count": len(roster.groups_by_name),
        "pdf_page_count": len(page_scans),
        "matched_page_count": len(match_results.accepted_matches),
        "exact_match_count": status_counts.get("matched_exact", 0),
        "fuzzy_match_count": status_counts.get("matched_fuzzy", 0),
        "roster_not_found_count": roster_not_found_count,
        "ignored_non_roster_page_count": status_counts.get("ignored_not_in_roster", 0),
        "generated_team_pdf_count": len(written_files),
        "report_path": str(report_path),
    }


def print_summary(summary: dict[str, object]) -> None:
    print(f"Roster rows: {summary['roster_row_count']}")
    print(f"Unique roster passengers: {summary['unique_roster_passenger_count']}")
    print(f"PDF pages: {summary['pdf_page_count']}")
    print(f"Matched pages: {summary['matched_page_count']}")
    print(f"Exact matches: {summary['exact_match_count']}")
    print(f"Fuzzy matches: {summary['fuzzy_match_count']}")
    print(f"Roster passengers not found: {summary['roster_not_found_count']}")
    print(f"Ignored non-roster pages: {summary['ignored_non_roster_page_count']}")
    print(f"Generated team PDFs: {summary['generated_team_pdf_count']}")
    print(f"Report: {summary['report_path']}")
