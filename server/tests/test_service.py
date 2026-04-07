from __future__ import annotations

import zipfile
from pathlib import Path

from server.pdf_team_splitter import service
from server.pdf_team_splitter.matcher import MatchResults, PageMatch, ReportRow
from server.pdf_team_splitter.pdf_parser import PageScan
from server.pdf_team_splitter.team_roster import RosterData


def test_build_result_zip_includes_generated_pdfs_and_report(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    pdf_file = output_dir / "Team_A_行程单.pdf"
    pdf_file.write_bytes(b"PDF")

    report_file = output_dir / "match_report.csv"
    report_file.write_text("header, value\n", encoding="utf-8-sig")

    zip_path = tmp_path / "result.zip"

    result = service.build_result_zip(output_dir, zip_path)

    assert result == zip_path

    with zipfile.ZipFile(zip_path) as archive:
        contents = set(archive.namelist())

    assert "Team_A_行程单.pdf" in contents
    assert "match_report.csv" in contents


def test_process_pdf_team_split_passes_request_options(tmp_path: Path, monkeypatch) -> None:
    captured: dict[str, tuple] = {}

    def fake_load_roster(path: Path, *, sheet: str | int | None, name_column: str, team_column: str) -> RosterData:
        captured["load_roster"] = (path, sheet, name_column, team_column)
        return RosterData(entries=[], groups_by_name={}, team_names=[])

    monkeypatch.setattr(service, "load_roster", fake_load_roster)

    sample_scan = PageScan(
        page_number=1,
        text="TEXT",
        name_raw="AA/BB",
        name_normalized="AABB",
    )

    def fake_scan_pdf(path: Path) -> list[PageScan]:
        captured["scan_pdf"] = (path,)
        return [sample_scan]

    monkeypatch.setattr(service, "scan_pdf", fake_scan_pdf)

    sample_match = PageMatch(
        team_name="Team A",
        roster_name_raw="NAME",
        roster_name_normalized="NAME",
        pdf_page_number=1,
        pdf_name_raw="AA/BB",
        pdf_name_normalized="AABB",
        match_status="matched_exact",
        match_method="exact",
        fuzzy_score=None,
        excel_order=0,
    )
    sample_row = ReportRow(
        team_name="Team A",
        roster_name_raw="NAME",
        roster_name_normalized="NAME",
        match_status="matched_exact",
        match_method="exact",
        pdf_page_number=1,
        pdf_name_raw="AA/BB",
        pdf_name_normalized="AABB",
        fuzzy_score=None,
        note=None,
    )
    match_results = MatchResults(accepted_matches=[sample_match], report_rows=[sample_row])

    def fake_match_pages(roster: RosterData, page_scans: list[PageScan], *, fuzzy_threshold: int) -> MatchResults:
        captured["match_pages"] = (roster, page_scans, fuzzy_threshold)
        return match_results

    monkeypatch.setattr(service, "match_pages", fake_match_pages)

    written_path = tmp_path / "Team A_行程单.pdf"

    def fake_write_team_pdfs(pdf_path: Path, matches: list[PageMatch], outdir: Path) -> list[Path]:
        captured["write_team_pdfs"] = (pdf_path, matches, outdir)
        return [written_path]

    monkeypatch.setattr(service, "write_team_pdfs", fake_write_team_pdfs)

    def fake_write_report(rows: list[ReportRow], report_path: Path) -> None:
        captured["write_report"] = (rows, report_path)

    monkeypatch.setattr(service, "write_report", fake_write_report)

    def fake_build_summary(
        *,
        roster: RosterData,
        page_scans: list[PageScan],
        match_results: MatchResults,
        written_files: list[Path],
        report_path: Path,
    ) -> dict[str, object]:
        captured["build_summary"] = (roster, page_scans, match_results, written_files, report_path)
        return {"summary": True}

    monkeypatch.setattr(service, "build_summary", fake_build_summary)

    request = service.PdfTeamSplitRequest(
        roster_path="roster.xlsx",
        pdf_path="input.pdf",
        output_dir=tmp_path,
        sheet="RosterSheet",
        name_column="NameCol",
        team_column="TeamCol",
        fuzzy_threshold=42,
        report_filename="match_report.csv",
    )

    result = service.process_pdf_team_split(request)

    assert result.report_path.name == "match_report.csv"
    assert result.team_pdf_paths == [written_path]
    assert result.summary == {"summary": True}

    load_roster_args = captured["load_roster"]
    assert load_roster_args[1:] == ("RosterSheet", "NameCol", "TeamCol")

    match_pages_args = captured["match_pages"]
    assert match_pages_args[2] == 42

    write_report_args = captured["write_report"]
    assert write_report_args[0] == match_results.report_rows
    assert write_report_args[1].name == "match_report.csv"


def test_build_result_zip_skips_zip_inside_output(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    (output_dir / "data.txt").write_text("data")
    zip_path = output_dir / "archive.zip"

    service.build_result_zip(output_dir, zip_path)

    with zipfile.ZipFile(zip_path) as archive:
        contents = set(archive.namelist())

    assert "archive.zip" not in contents
