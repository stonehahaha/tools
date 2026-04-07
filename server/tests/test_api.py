from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import pytest
from fastapi.testclient import TestClient

from server.app import app
from server.pdf_team_splitter import PdfTeamSplitResult, build_result_zip


client = TestClient(app)


def _test_files() -> list[tuple[str, tuple[str, bytes, str]]]:
    return [
        ("roster", ("roster.xlsx", b"roster-data", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")),
        ("pdf", ("input.pdf", b"pdf-data", "application/pdf")),
    ]


def test_post_requires_files() -> None:
    response = client.post("/api/pdf-team-split")
    assert response.status_code == 422


def test_successful_upload_returns_zip_and_passes_options(tmp_path: Path, monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_process(request: Any) -> PdfTeamSplitResult:
        captured["request"] = request
        artifact = Path(request.output_dir) / "generated.txt"
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_bytes(b"artifact")
        return PdfTeamSplitResult(
            team_pdf_paths=[tmp_path / "Team_A.pdf"],
            report_path=tmp_path / "report.csv",
            summary={"ok": True},
        )

    monkeypatch.setattr("server.app.process_pdf_team_split", fake_process)

    real_build_result_zip = build_result_zip

    def fake_build_result_zip(output_dir: Path | str, zip_path: Path | str) -> Path:
        captured["build_result_zip"] = (Path(output_dir), Path(zip_path))
        return real_build_result_zip(output_dir, zip_path)

    monkeypatch.setattr("server.app.build_result_zip", fake_build_result_zip)

    response = client.post(
        "/api/pdf-team-split",
        files=_test_files(),
        data={
            "sheet": "RosterSheet",
            "name_column": "NameColumn",
            "team_column": "TeamColumn",
            "fuzzy_threshold": "35",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"

    names = ZipFile(BytesIO(response.content)).namelist()
    assert set(names) == {"generated.txt"}
    assert "roster.xlsx" not in names
    assert "input.pdf" not in names

    request = captured["request"]
    assert request.sheet == "RosterSheet"
    assert request.name_column == "NameColumn"
    assert request.team_column == "TeamColumn"
    assert isinstance(request.fuzzy_threshold, int)
    assert request.fuzzy_threshold == 35

    output_dir, zip_path = captured["build_result_zip"]
    assert output_dir == request.output_dir
    assert zip_path.name == "result.zip"


def test_processing_errors_return_json(monkeypatch: Any) -> None:
    def fake_process(_: Any) -> PdfTeamSplitResult:
        raise ValueError("bad roster")

    monkeypatch.setattr("server.app.process_pdf_team_split", fake_process)

    response = client.post("/api/pdf-team-split", files=_test_files())

    assert response.status_code == 400
    assert response.json() == {"message": "bad roster"}


def test_invalid_fuzzy_threshold_returns_bad_request(monkeypatch: Any) -> None:
    def fake_process(_: Any) -> PdfTeamSplitResult:
        pytest.fail("process should not run for invalid threshold")

    monkeypatch.setattr("server.app.process_pdf_team_split", fake_process)

    response = client.post(
        "/api/pdf-team-split",
        files=_test_files(),
        data={"fuzzy_threshold": "foo"},
    )

    assert response.status_code == 400
    assert response.json() == {"message": "Invalid fuzzy_threshold"}
