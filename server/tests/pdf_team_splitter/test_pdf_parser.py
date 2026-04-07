from pathlib import Path

from server.pdf_team_splitter.pdf_parser import extract_candidate_name, scan_pdf


class FakePage:
    def __init__(self, text: str):
        self._text = text

    def extract_text(self) -> str:
        return self._text


def test_extract_candidate_name_returns_airline_style_name():
    text = "Passenger: ZHU/XIUWU\nFlight: MU123"
    assert extract_candidate_name(text) == "ZHU/XIUWU"


def test_scan_pdf_normalizes_detected_names(monkeypatch, tmp_path: Path):
    class FakeReader:
        def __init__(self, _path: str):
            self.pages = [
                FakePage("Passenger: zhu / xiuwu"),
                FakePage("No passenger name on this page"),
            ]

    monkeypatch.setattr("server.pdf_team_splitter.pdf_parser.PdfReader", FakeReader)

    scans = scan_pdf(tmp_path / "dummy.pdf")

    assert scans[0].page_number == 1
    assert scans[0].name_raw == "ZHU / XIUWU"
    assert scans[0].name_normalized == "ZHU/XIUWU"
    assert scans[1].page_number == 2
    assert scans[1].name_raw is None
    assert scans[1].name_normalized is None
