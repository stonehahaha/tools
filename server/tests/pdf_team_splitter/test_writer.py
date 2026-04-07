from pathlib import Path

import pytest

from server.pdf_team_splitter.matcher import PageMatch
from server.pdf_team_splitter.writer import order_matches_for_team, write_team_pdfs


TEAM_A = "A\u56e2"
TEAM_B = "B\u56e2"
ITINERARY_SUFFIX = "_\u884c\u7a0b\u5355.pdf"


def _match(
    *,
    page_number: int,
    name: str,
    team: str = TEAM_A,
    excel_order: int = 0,
) -> PageMatch:
    return PageMatch(
        team_name=team,
        roster_name_raw=name,
        roster_name_normalized=name,
        pdf_page_number=page_number,
        pdf_name_raw=name,
        pdf_name_normalized=name,
        match_status="matched_exact",
        match_method="exact",
        fuzzy_score=None,
        excel_order=excel_order,
    )


def test_order_matches_for_team_respects_requested_sort_mode():
    matches = [
        _match(page_number=5, name="WANG/WEI", excel_order=1),
        _match(page_number=2, name="ZHU/XIUWU", excel_order=0),
        _match(page_number=7, name="ZHU/XIUWU", excel_order=1),
    ]

    assert [m.pdf_page_number for m in order_matches_for_team(matches)] == [2, 5, 7]


def test_write_team_pdfs_writes_one_file_per_team(monkeypatch, tmp_path: Path):
    written_bytes: list[bytes] = []

    class FakeReader:
        def __init__(self, _path: str):
            self.pages = ["page-1", "page-2", "page-3"]

    class FakeWriter:
        def __init__(self):
            self.pages = []

        def add_page(self, page):
            self.pages.append(page)

        def write(self, stream):
            written_bytes.append(b"|".join(page.encode("utf-8") for page in self.pages))
            stream.write(b"%PDF-FAKE%")

    monkeypatch.setattr("server.pdf_team_splitter.writer.PdfReader", FakeReader)
    monkeypatch.setattr("server.pdf_team_splitter.writer.PdfWriter", FakeWriter)

    outdir = tmp_path / "out"
    written_files = write_team_pdfs(
        pdf_path=tmp_path / "source.pdf",
        matches=[
            _match(page_number=2, name="ZHU/XIUWU", team=TEAM_A, excel_order=1),
            _match(page_number=1, name="LI/LEI", team=TEAM_A, excel_order=0),
            _match(page_number=3, name="WANG/WEI", team=TEAM_B, excel_order=0),
        ],
        outdir=outdir,
    )

    assert [path.name for path in written_files] == [
        f"{TEAM_A}{ITINERARY_SUFFIX}",
        f"{TEAM_B}{ITINERARY_SUFFIX}",
    ]
    assert written_bytes == [b"page-1|page-2", b"page-3"]


def test_write_team_pdfs_preserves_same_team_roster_order(monkeypatch, tmp_path: Path):
    written_bytes: list[bytes] = []

    class FakeReader:
        def __init__(self, _path: str):
            self.pages = ["page-1", "page-2", "page-3"]

    class FakeWriter:
        def __init__(self):
            self.pages = []

        def add_page(self, page):
            self.pages.append(page)

        def write(self, stream):
            written_bytes.append(b"|".join(page.encode("utf-8") for page in self.pages))
            stream.write(b"%PDF-FAKE%")

    monkeypatch.setattr("server.pdf_team_splitter.writer.PdfReader", FakeReader)
    monkeypatch.setattr("server.pdf_team_splitter.writer.PdfWriter", FakeWriter)

    write_team_pdfs(
        pdf_path=tmp_path / "source.pdf",
        matches=[
            _match(page_number=3, name="ZHU/XIUWU", team=TEAM_A, excel_order=1),
            _match(page_number=1, name="WANG/WEI", team=TEAM_A, excel_order=0),
        ],
        outdir=tmp_path / "out",
    )

    assert written_bytes == [b"page-1|page-3"]


def test_write_team_pdfs_rejects_unsafe_team_name(monkeypatch, tmp_path: Path):
    class FakeReader:
        def __init__(self, _path: str):
            self.pages = ["page-1"]

    class FakeWriter:
        def add_page(self, _page):
            raise AssertionError("writer should not be used for unsafe team names")

        def write(self, _stream):
            raise AssertionError("writer should not be used for unsafe team names")

    monkeypatch.setattr("server.pdf_team_splitter.writer.PdfReader", FakeReader)
    monkeypatch.setattr("server.pdf_team_splitter.writer.PdfWriter", FakeWriter)

    with pytest.raises(ValueError, match="Unsafe team name"):
        write_team_pdfs(
            pdf_path=tmp_path / "source.pdf",
            matches=[_match(page_number=1, name="ESCAPE", team="../escape")],
            outdir=tmp_path / "out",
        )


def test_write_team_pdfs_prevalidates_all_teams_before_writing(monkeypatch, tmp_path: Path):
    write_calls = 0

    class FakeReader:
        def __init__(self, _path: str):
            self.pages = ["page-1", "page-2"]

    class FakeWriter:
        def __init__(self):
            self.pages = []

        def add_page(self, page):
            self.pages.append(page)

        def write(self, _stream):
            nonlocal write_calls
            write_calls += 1
            raise AssertionError("no files should be written before validation succeeds")

    monkeypatch.setattr("server.pdf_team_splitter.writer.PdfReader", FakeReader)
    monkeypatch.setattr("server.pdf_team_splitter.writer.PdfWriter", FakeWriter)

    outdir = tmp_path / "out"
    with pytest.raises(ValueError, match="Unsafe team name"):
        write_team_pdfs(
            pdf_path=tmp_path / "source.pdf",
            matches=[
                _match(page_number=1, name="SAFE", team="A"),
                _match(page_number=2, name="UNSAFE", team="B?B"),
            ],
            outdir=outdir,
        )

    assert write_calls == 0
    assert not outdir.exists()


def test_write_team_pdfs_rejects_windows_invalid_filename_characters(
    monkeypatch, tmp_path: Path
):
    class FakeReader:
        def __init__(self, _path: str):
            self.pages = ["page-1"]

    class FakeWriter:
        def add_page(self, _page):
            raise AssertionError("writer should not be used for unsafe team names")

        def write(self, _stream):
            raise AssertionError("writer should not be used for unsafe team names")

    monkeypatch.setattr("server.pdf_team_splitter.writer.PdfReader", FakeReader)
    monkeypatch.setattr("server.pdf_team_splitter.writer.PdfWriter", FakeWriter)

    with pytest.raises(ValueError, match="Unsafe team name"):
        write_team_pdfs(
            pdf_path=tmp_path / "source.pdf",
            matches=[_match(page_number=1, name="INVALID", team="A?B")],
            outdir=tmp_path / "out",
        )


def test_write_team_pdfs_rejects_control_characters_before_any_write(
    monkeypatch, tmp_path: Path
):
    write_calls = 0

    class FakeReader:
        def __init__(self, _path: str):
            self.pages = ["page-1", "page-2"]

    class FakeWriter:
        def __init__(self):
            self.pages = []

        def add_page(self, page):
            self.pages.append(page)

        def write(self, _stream):
            nonlocal write_calls
            write_calls += 1
            raise AssertionError("no files should be written before validation succeeds")

    monkeypatch.setattr("server.pdf_team_splitter.writer.PdfReader", FakeReader)
    monkeypatch.setattr("server.pdf_team_splitter.writer.PdfWriter", FakeWriter)

    outdir = tmp_path / "out"
    with pytest.raises(ValueError, match="Unsafe team name"):
        write_team_pdfs(
            pdf_path=tmp_path / "source.pdf",
            matches=[
                _match(page_number=1, name="SAFE", team="A"),
                _match(page_number=2, name="UNSAFE", team="B\nB"),
            ],
            outdir=outdir,
        )

    assert write_calls == 0
    assert not outdir.exists()


def test_write_team_pdfs_preserves_pdf_order_when_excel_order_ties(
    monkeypatch, tmp_path: Path
):
    written_bytes: list[bytes] = []

    class FakeReader:
        def __init__(self, _path: str):
            self.pages = ["page-1", "page-2", "page-3"]

    class FakeWriter:
        def __init__(self):
            self.pages = []

        def add_page(self, page):
            self.pages.append(page)

        def write(self, stream):
            written_bytes.append(b"|".join(page.encode("utf-8") for page in self.pages))
            stream.write(b"%PDF-FAKE%")

    monkeypatch.setattr("server.pdf_team_splitter.writer.PdfReader", FakeReader)
    monkeypatch.setattr("server.pdf_team_splitter.writer.PdfWriter", FakeWriter)

    write_team_pdfs(
        pdf_path=tmp_path / "source.pdf",
        matches=[
            _match(page_number=3, name="ZHU/XIUWU", team=TEAM_A, excel_order=1),
            _match(page_number=2, name="ZHU/XIUWU", team=TEAM_A, excel_order=1),
            _match(page_number=1, name="WANG/WEI", team=TEAM_A, excel_order=0),
        ],
        outdir=tmp_path / "out",
    )

    assert written_bytes == [b"page-1|page-2|page-3"]
