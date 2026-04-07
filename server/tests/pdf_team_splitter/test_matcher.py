from pathlib import Path

from server.pdf_team_splitter.pdf_parser import PageScan
from server.pdf_team_splitter.team_roster import DEFAULT_NAME_COLUMN, DEFAULT_TEAM_COLUMN, load_roster

from server.pdf_team_splitter.matcher import match_pages


def _write_roster(tmp_path: Path, rows: list[tuple[str, str]]):
    roster_path = tmp_path / "roster.csv"
    csv_lines = [f"{DEFAULT_NAME_COLUMN},{DEFAULT_TEAM_COLUMN}"]
    csv_lines.extend(f"{name},{team}" for name, team in rows)
    roster_path.write_text("\n".join(csv_lines), encoding="utf-8-sig")
    return load_roster(roster_path)


def test_match_pages_records_exact_fuzzy_and_ignored_rows(tmp_path: Path):
    roster = _write_roster(
        tmp_path,
        [("ZHU/XIUWU", "A队"), ("LI/LEI", "B队")],
    )
    scans = [
        PageScan(1, "Passenger: ZHU/XIUWU", "ZHU/XIUWU", "ZHU/XIUWU"),
        PageScan(2, "Passenger: LI/LEEI", "LI/LEEI", "LI/LEEI"),
        PageScan(3, "Passenger: CHEN/JIE", "CHEN/JIE", "CHEN/JIE"),
    ]

    results = match_pages(roster, scans, fuzzy_threshold=85)

    assert [match.match_status for match in results.accepted_matches] == [
        "matched_exact",
        "matched_fuzzy",
    ]
    assert any(row.match_status == "ignored_not_in_roster" for row in results.report_rows)


def test_match_pages_marks_missing_roster_names(tmp_path: Path):
    roster = _write_roster(
        tmp_path,
        [("ZHU/XIUWU", "A队"), ("WANG/WEI", "A队")],
    )
    scans = [PageScan(1, "Passenger: ZHU/XIUWU", "ZHU/XIUWU", "ZHU/XIUWU")]

    results = match_pages(roster, scans, fuzzy_threshold=90)

    missing_rows = [
        row for row in results.report_rows if row.match_status == "not_found_in_pdf"
    ]
    assert len(missing_rows) == 1
    assert missing_rows[0].roster_name_normalized == "WANG/WEI"


def test_match_pages_marks_duplicate_count_short(tmp_path: Path):
    roster = _write_roster(
        tmp_path,
        [("ZHU/XIUWU", "A队"), ("ZHU/XIUWU", "A队")],
    )
    scans = [PageScan(1, "Passenger: ZHU/XIUWU", "ZHU/XIUWU", "ZHU/XIUWU")]

    results = match_pages(roster, scans, fuzzy_threshold=90)

    assert any(
        row.match_status == "duplicate_count_short" for row in results.report_rows
    )


def test_match_pages_marks_pages_without_detected_name_as_unresolved(tmp_path: Path):
    roster = _write_roster(
        tmp_path,
        [("ZHU/XIUWU", "A队")],
    )
    scans = [PageScan(1, "No passenger name on this page", None, None)]

    results = match_pages(roster, scans, fuzzy_threshold=90)

    unresolved_rows = [
        row for row in results.report_rows if row.match_status == "unresolved_page_name"
    ]
    assert results.accepted_matches == []
    assert len(unresolved_rows) == 1
    assert unresolved_rows[0].pdf_page_number == 1
    assert unresolved_rows[0].note == "Could not extract a passenger name from the page text"


def test_match_pages_marks_ambiguous_fuzzy_candidates_explicitly(tmp_path: Path):
    roster = _write_roster(
        tmp_path,
        [("LI/LEI", "A队"), ("LI/LEE", "B队")],
    )
    scans = [PageScan(1, "Passenger: LI/LEEI", "LI/LEEI", "LI/LEEI")]

    results = match_pages(roster, scans, fuzzy_threshold=90)

    unresolved_rows = [
        row for row in results.report_rows if row.match_status == "ambiguous_fuzzy_match"
    ]
    assert results.accepted_matches == []
    assert len(unresolved_rows) == 1
    assert unresolved_rows[0].pdf_name_normalized == "LI/LEEI"


def test_match_pages_marks_duplicate_count_over(tmp_path: Path):
    roster = _write_roster(
        tmp_path,
        [("ZHU/XIUWU", "A队")],
    )
    scans = [
        PageScan(1, "Passenger: ZHU/XIUWU", "ZHU/XIUWU", "ZHU/XIUWU"),
        PageScan(2, "Passenger: ZHU/XIUWU", "ZHU/XIUWU", "ZHU/XIUWU"),
    ]

    results = match_pages(roster, scans, fuzzy_threshold=90)

    over_rows = [
        row for row in results.report_rows if row.match_status == "duplicate_count_over"
    ]
    assert len(results.accepted_matches) == 2
    assert len(over_rows) == 1
    assert over_rows[0].note == "Expected 1, matched 2"


def test_match_pages_prefers_exact_match_over_fuzzy_candidates(tmp_path: Path):
    roster = _write_roster(
        tmp_path,
        [("ZHU/XIUWU", "A队"), ("ZHU/XIUWEN", "B队")],
    )
    scans = [PageScan(1, "Passenger: ZHU/XIUWU", "ZHU/XIUWU", "ZHU/XIUWU")]

    results = match_pages(roster, scans, fuzzy_threshold=80)

    assert len(results.accepted_matches) == 1
    assert results.accepted_matches[0].match_status == "matched_exact"
    assert results.accepted_matches[0].match_method == "exact"
    assert results.accepted_matches[0].fuzzy_score is None


def test_match_pages_assigns_distinct_excel_order_for_duplicate_names(tmp_path: Path):
    roster = _write_roster(
        tmp_path,
        [("ZHU/XIUWU", "A队"), ("LI/LEI", "A队"), ("ZHU/XIUWU", "A队")],
    )
    scans = [
        PageScan(1, "Passenger: ZHU/XIUWU", "ZHU/XIUWU", "ZHU/XIUWU"),
        PageScan(2, "Passenger: LI/LEI", "LI/LEI", "LI/LEI"),
        PageScan(3, "Passenger: ZHU/XIUWU", "ZHU/XIUWU", "ZHU/XIUWU"),
    ]

    results = match_pages(roster, scans, fuzzy_threshold=90)

    assert [
        (match.pdf_page_number, match.excel_order) for match in results.accepted_matches
    ] == [(1, 0), (2, 1), (3, 2)]


def test_match_pages_sorts_duplicate_names_by_excel_row_order(tmp_path: Path):
    roster = _write_roster(
        tmp_path,
        [("ZHU/XIUWU", "A队"), ("LI/LEI", "A队"), ("ZHU/XIUWU", "A队")],
    )
    scans = [
        PageScan(1, "Passenger: ZHU/XIUWU", "ZHU/XIUWU", "ZHU/XIUWU"),
        PageScan(2, "Passenger: LI/LEI", "LI/LEI", "LI/LEI"),
        PageScan(3, "Passenger: ZHU/XIUWU", "ZHU/XIUWU", "ZHU/XIUWU"),
    ]

    results = match_pages(roster, scans, fuzzy_threshold=90)
    sorted_matches = sorted(results.accepted_matches, key=lambda match: match.excel_order)

    assert [
        (match.roster_name_normalized, match.pdf_page_number) for match in sorted_matches
    ] == [("ZHU/XIUWU", 1), ("LI/LEI", 2), ("ZHU/XIUWU", 3)]
