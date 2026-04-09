from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response

from server.pdf_team_splitter import PdfTeamSplitRequest, build_result_zip, process_pdf_team_split

TMP_ROOT = Path(__file__).resolve().parent / "tmp"
TMP_ROOT.mkdir(parents=True, exist_ok=True)

app = FastAPI()


def _cleanup_dir(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)


def _sanitize_filename(filename: str | None, fallback: str) -> str:
    return Path(filename or fallback).name


def _parse_sheet_value(sheet: str | None) -> str | int | None:
    if sheet is None:
        return None

    normalized = sheet.strip()
    if not normalized:
        return None
    if normalized.isdigit():
        return int(normalized)
    return normalized


async def _save_upload(upload: UploadFile, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as file_obj:
        while chunk := await upload.read(8192):
            file_obj.write(chunk)
    await upload.close()


@app.post("/api/pdf-team-split", response_model=None)
async def pdf_team_split(
    background_tasks: BackgroundTasks,
    roster: UploadFile = File(...),
    pdf: UploadFile = File(...),
    sheet: str | None = Form(None),
    name_column: str | None = Form(None),
    team_column: str | None = Form(None),
    fuzzy_threshold: str | None = Form(None),
) -> Response:
    working_dir = TMP_ROOT / uuid4().hex
    working_dir.mkdir(parents=True, exist_ok=True)
    background_tasks.add_task(_cleanup_dir, working_dir)

    output_dir = working_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    roster_path = working_dir / _sanitize_filename(roster.filename, "roster.xlsx")
    pdf_path = working_dir / _sanitize_filename(pdf.filename, "input.pdf")

    await _save_upload(roster, roster_path)
    await _save_upload(pdf, pdf_path)

    request_data: dict[str, object] = {
        "roster_path": roster_path,
        "pdf_path": pdf_path,
        "output_dir": output_dir,
    }

    parsed_sheet = _parse_sheet_value(sheet)
    if parsed_sheet is not None:
        request_data["sheet"] = parsed_sheet

    if name_column is not None:
        request_data["name_column"] = name_column

    if team_column is not None:
        request_data["team_column"] = team_column

    if fuzzy_threshold is not None:
        try:
            request_data["fuzzy_threshold"] = int(fuzzy_threshold)
        except ValueError:
            return JSONResponse(status_code=400, content={"message": "Invalid fuzzy_threshold"})

    try:
        process_pdf_team_split(PdfTeamSplitRequest(**request_data))
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"message": str(exc)})

    zip_path = working_dir / "result.zip"
    archive_path = build_result_zip(output_dir, zip_path)
    return FileResponse(archive_path, media_type="application/zip", filename=zip_path.name)
