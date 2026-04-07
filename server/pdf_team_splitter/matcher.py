from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from rapidfuzz import fuzz, process

from .pdf_parser import PageScan
from .team_roster import RosterData


@dataclass(frozen=True)
class PageMatch:
    team_name: str
    roster_name_raw: str
    roster_name_normalized: str
    pdf_page_number: int
    pdf_name_raw: str
    pdf_name_normalized: str
    match_status: str
    match_method: str
    fuzzy_score: int | None
    excel_order: int


@dataclass(frozen=True)
class ReportRow:
    team_name: str | None
    roster_name_raw: str | None
    roster_name_normalized: str | None
    match_status: str
    match_method: str | None
    pdf_page_number: int | None
    pdf_name_raw: str | None
    pdf_name_normalized: str | None
    fuzzy_score: int | None
    note: str | None


@dataclass(frozen=True)
class MatchResults:
    accepted_matches: list[PageMatch]
    report_rows: list[ReportRow]


def _excel_order_for_match(group, matched_count: int) -> int:
    if matched_count < len(group.roster_row_indices):
        return group.roster_row_indices[matched_count]
    return group.roster_row_indices[-1]


def match_pages(
    roster: RosterData,
    page_scans: list[PageScan],
    *,
    fuzzy_threshold: int = 90,
) -> MatchResults:
    accepted_matches: list[PageMatch] = []
    report_rows: list[ReportRow] = []
    matched_counts: Counter[str] = Counter()
    roster_names = list(roster.groups_by_name.keys())

    for scan in page_scans:
        if not scan.name_normalized:
            report_rows.append(
                ReportRow(
                    team_name=None,
                    roster_name_raw=None,
                    roster_name_normalized=None,
                    match_status="unresolved_page_name",
                    match_method=None,
                    pdf_page_number=scan.page_number,
                    pdf_name_raw=scan.name_raw,
                    pdf_name_normalized=scan.name_normalized,
                    fuzzy_score=None,
                    note="Could not extract a passenger name from the page text",
                )
            )
            continue

        exact_group = roster.groups_by_name.get(scan.name_normalized)
        if exact_group is not None:
            excel_order = _excel_order_for_match(
                exact_group, matched_counts[exact_group.name_normalized]
            )
            accepted_matches.append(
                PageMatch(
                    team_name=exact_group.team_name,
                    roster_name_raw=exact_group.roster_names_raw[0],
                    roster_name_normalized=exact_group.name_normalized,
                    pdf_page_number=scan.page_number,
                    pdf_name_raw=scan.name_raw or scan.name_normalized,
                    pdf_name_normalized=scan.name_normalized,
                    match_status="matched_exact",
                    match_method="exact",
                    fuzzy_score=None,
                    excel_order=excel_order,
                )
            )
            report_rows.append(
                ReportRow(
                    team_name=exact_group.team_name,
                    roster_name_raw=exact_group.roster_names_raw[0],
                    roster_name_normalized=exact_group.name_normalized,
                    match_status="matched_exact",
                    match_method="exact",
                    pdf_page_number=scan.page_number,
                    pdf_name_raw=scan.name_raw,
                    pdf_name_normalized=scan.name_normalized,
                    fuzzy_score=None,
                    note=None,
                )
            )
            matched_counts[exact_group.name_normalized] += 1
            continue

        candidates = process.extract(
            scan.name_normalized,
            roster_names,
            scorer=fuzz.ratio,
            score_cutoff=fuzzy_threshold,
            limit=2,
        )
        if len(candidates) == 1:
            candidate_name, score, _ = candidates[0]
            fuzzy_group = roster.groups_by_name[candidate_name]
            excel_order = _excel_order_for_match(
                fuzzy_group, matched_counts[fuzzy_group.name_normalized]
            )
            accepted_matches.append(
                PageMatch(
                    team_name=fuzzy_group.team_name,
                    roster_name_raw=fuzzy_group.roster_names_raw[0],
                    roster_name_normalized=fuzzy_group.name_normalized,
                    pdf_page_number=scan.page_number,
                    pdf_name_raw=scan.name_raw or scan.name_normalized,
                    pdf_name_normalized=scan.name_normalized,
                    match_status="matched_fuzzy",
                    match_method="fuzzy",
                    fuzzy_score=int(score),
                    excel_order=excel_order,
                )
            )
            report_rows.append(
                ReportRow(
                    team_name=fuzzy_group.team_name,
                    roster_name_raw=fuzzy_group.roster_names_raw[0],
                    roster_name_normalized=fuzzy_group.name_normalized,
                    match_status="matched_fuzzy",
                    match_method="fuzzy",
                    pdf_page_number=scan.page_number,
                    pdf_name_raw=scan.name_raw,
                    pdf_name_normalized=scan.name_normalized,
                    fuzzy_score=int(score),
                    note="Auto-accepted because exactly one fuzzy candidate qualified",
                )
            )
            matched_counts[fuzzy_group.name_normalized] += 1
            continue

        if len(candidates) > 1:
            report_rows.append(
                ReportRow(
                    team_name=None,
                    roster_name_raw=None,
                    roster_name_normalized=None,
                    match_status="ambiguous_fuzzy_match",
                    match_method=None,
                    pdf_page_number=scan.page_number,
                    pdf_name_raw=scan.name_raw,
                    pdf_name_normalized=scan.name_normalized,
                    fuzzy_score=None,
                    note="Multiple fuzzy candidates qualified; page was not auto-assigned",
                )
            )
            continue

        report_rows.append(
            ReportRow(
                team_name=None,
                roster_name_raw=None,
                roster_name_normalized=None,
                match_status="ignored_not_in_roster",
                match_method=None,
                pdf_page_number=scan.page_number,
                pdf_name_raw=scan.name_raw,
                pdf_name_normalized=scan.name_normalized,
                fuzzy_score=None,
                note="Passenger name not found in roster",
            )
        )

    for name_normalized, group in roster.groups_by_name.items():
        actual_count = matched_counts[name_normalized]
        if actual_count == 0:
            report_rows.append(
                ReportRow(
                    team_name=group.team_name,
                    roster_name_raw=group.roster_names_raw[0],
                    roster_name_normalized=group.name_normalized,
                    match_status="not_found_in_pdf",
                    match_method=None,
                    pdf_page_number=None,
                    pdf_name_raw=None,
                    pdf_name_normalized=None,
                    fuzzy_score=None,
                    note=f"Expected {group.expected_count}, matched 0",
                )
            )
        elif actual_count < group.expected_count:
            report_rows.append(
                ReportRow(
                    team_name=group.team_name,
                    roster_name_raw=group.roster_names_raw[0],
                    roster_name_normalized=group.name_normalized,
                    match_status="duplicate_count_short",
                    match_method=None,
                    pdf_page_number=None,
                    pdf_name_raw=None,
                    pdf_name_normalized=None,
                    fuzzy_score=None,
                    note=f"Expected {group.expected_count}, matched {actual_count}",
                )
            )
        elif actual_count > group.expected_count:
            report_rows.append(
                ReportRow(
                    team_name=group.team_name,
                    roster_name_raw=group.roster_names_raw[0],
                    roster_name_normalized=group.name_normalized,
                    match_status="duplicate_count_over",
                    match_method=None,
                    pdf_page_number=None,
                    pdf_name_raw=None,
                    pdf_name_normalized=None,
                    fuzzy_score=None,
                    note=f"Expected {group.expected_count}, matched {actual_count}",
                )
            )

    return MatchResults(accepted_matches=accepted_matches, report_rows=report_rows)
