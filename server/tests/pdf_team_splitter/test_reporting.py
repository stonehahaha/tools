from pathlib import Path

from server.pdf_team_splitter.matcher import MatchResults, PageMatch, ReportRow
from server.pdf_team_splitter.pdf_parser import PageScan
from server.pdf_team_splitter.reporting import build_summary, print_summary, write_report
from server.pdf_team_splitter.team_roster import RosterData, RosterEntry, RosterGroup, load_roster


def _load_roster(tmp_path: Path):
    roster_path = tmp_path / "roster.csv"
    roster_path.write_text(
        "姓名,团队\n"
        "ZHU/XIUWU,A团\n"
        "LI/LEI,B团\n",
        encoding="utf-8-sig",
    )
    return load_roster(roster_path)


def test_write_report_creates_csv_with_expected_headers(tmp_path: Path):
    report_path = tmp_path / "match_report.csv"
    rows = [
        ReportRow(
            team_name="A团",
            roster_name_raw="ZHU/XIUWU",
            roster_name_normalized="ZHU/XIUWU",
            match_status="matched_exact",
            match_method="exact",
            pdf_page_number=1,
            pdf_name_raw="ZHU/XIUWU",
            pdf_name_normalized="ZHU/XIUWU",
            fuzzy_score=None,
            note=None,
        )
    ]

    write_report(rows, report_path)

    content = report_path.read_text(encoding="utf-8-sig")
    assert "team_name,roster_name_raw,roster_name_normalized,match_status" in content
    assert "matched_exact" in content
    assert "A团,ZHU/XIUWU,ZHU/XIUWU,matched_exact,exact,1,ZHU/XIUWU,ZHU/XIUWU,," in content


def test_build_summary_and_print_summary(tmp_path: Path, capsys):
    roster = _load_roster(tmp_path)
    scans = [
        PageScan(1, "Passenger: ZHU/XIUWU", "ZHU/XIUWU", "ZHU/XIUWU"),
        PageScan(2, "Passenger: CHEN/JIE", "CHEN/JIE", "CHEN/JIE"),
    ]
    results = MatchResults(
        accepted_matches=[
            PageMatch(
                team_name="A团",
                roster_name_raw="ZHU/XIUWU",
                roster_name_normalized="ZHU/XIUWU",
                pdf_page_number=1,
                pdf_name_raw="ZHU/XIUWU",
                pdf_name_normalized="ZHU/XIUWU",
                match_status="matched_exact",
                match_method="exact",
                fuzzy_score=None,
                excel_order=0,
            )
        ],
        report_rows=[
            ReportRow(
                team_name="A团",
                roster_name_raw="ZHU/XIUWU",
                roster_name_normalized="ZHU/XIUWU",
                match_status="matched_exact",
                match_method="exact",
                pdf_page_number=1,
                pdf_name_raw="ZHU/XIUWU",
                pdf_name_normalized="ZHU/XIUWU",
                fuzzy_score=None,
                note=None,
            ),
            ReportRow(
                team_name=None,
                roster_name_raw=None,
                roster_name_normalized=None,
                match_status="ignored_not_in_roster",
                match_method=None,
                pdf_page_number=2,
                pdf_name_raw="CHEN/JIE",
                pdf_name_normalized="CHEN/JIE",
                fuzzy_score=None,
                note="Passenger name not found in roster",
            ),
            ReportRow(
                team_name="B团",
                roster_name_raw="LI/LEI",
                roster_name_normalized="LI/LEI",
                match_status="not_found_in_pdf",
                match_method=None,
                pdf_page_number=None,
                pdf_name_raw=None,
                pdf_name_normalized=None,
                fuzzy_score=None,
                note="Expected 1, matched 0",
            ),
        ],
    )

    summary = build_summary(
        roster=roster,
        page_scans=scans,
        match_results=results,
        written_files=[tmp_path / "A团_行程单.pdf"],
        report_path=tmp_path / "match_report.csv",
    )

    assert summary["roster_row_count"] == 2
    assert summary["pdf_page_count"] == 2
    assert summary["matched_page_count"] == 1
    assert summary["ignored_non_roster_page_count"] == 1
    assert summary["roster_not_found_count"] == 1

    print_summary(summary)
    output = capsys.readouterr().out
    assert "Matched pages: 1" in output
    assert "Ignored non-roster pages: 1" in output


def test_build_summary_counts_duplicate_shortage_as_missing_roster_entry(tmp_path: Path):
    roster = RosterData(
        entries=[
            RosterEntry(
                row_index=0,
                team_name="A团",
                name_raw="ZHU/XIUWU",
                name_normalized="ZHU/XIUWU",
            ),
            RosterEntry(
                row_index=1,
                team_name="A团",
                name_raw="ZHU/XIUWU",
                name_normalized="ZHU/XIUWU",
            ),
        ],
        groups_by_name={
            "ZHU/XIUWU": RosterGroup(
                team_name="A团",
                name_normalized="ZHU/XIUWU",
                roster_names_raw=("ZHU/XIUWU", "ZHU/XIUWU"),
                expected_count=2,
                first_row_index=0,
            )
        },
        team_names=["A团"],
    )
    results = MatchResults(
        accepted_matches=[
            PageMatch(
                team_name="A团",
                roster_name_raw="ZHU/XIUWU",
                roster_name_normalized="ZHU/XIUWU",
                pdf_page_number=1,
                pdf_name_raw="ZHU/XIUWU",
                pdf_name_normalized="ZHU/XIUWU",
                match_status="matched_exact",
                match_method="exact",
                fuzzy_score=None,
                excel_order=0,
            )
        ],
        report_rows=[
            ReportRow(
                team_name="A团",
                roster_name_raw="ZHU/XIUWU",
                roster_name_normalized="ZHU/XIUWU",
                match_status="matched_exact",
                match_method="exact",
                pdf_page_number=1,
                pdf_name_raw="ZHU/XIUWU",
                pdf_name_normalized="ZHU/XIUWU",
                fuzzy_score=None,
                note=None,
            ),
            ReportRow(
                team_name="A团",
                roster_name_raw="ZHU/XIUWU",
                roster_name_normalized="ZHU/XIUWU",
                match_status="duplicate_count_short",
                match_method=None,
                pdf_page_number=None,
                pdf_name_raw=None,
                pdf_name_normalized=None,
                fuzzy_score=None,
                note="Expected 2, matched 1",
            ),
        ],
    )

    summary = build_summary(
        roster=roster,
        page_scans=[PageScan(1, "Passenger: ZHU/XIUWU", "ZHU/XIUWU", "ZHU/XIUWU")],
        match_results=results,
        written_files=[tmp_path / "A团_行程单.pdf"],
        report_path=tmp_path / "match_report.csv",
    )

    assert summary["roster_not_found_count"] == 1
