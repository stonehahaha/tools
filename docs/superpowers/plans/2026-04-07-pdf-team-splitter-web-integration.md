# PDF Team Splitter Web Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new web tool to the existing Vue application that uploads a roster file and a PDF, sends them to a local Python API, and downloads a zip bundle containing per-team PDFs and `match_report.csv`.

**Architecture:** Keep the existing Vue app as a static frontend and add a small Python API under `server/` inside the same repository. Reuse the validated Python PDF-processing modules from `E:\code\pdftool` by copying them into a package-local `server/pdf_team_splitter/` directory, then add a thin orchestration layer that zips outputs and exposes one `POST /api/pdf-team-split` endpoint. Use same-origin `/api` requests in production and a Vite dev proxy locally.

**Tech Stack:** Vue 3, Vite, Vue Router, Element Plus, Vitest, Vue Test Utils, Python 3.12, FastAPI, Uvicorn, pandas, pypdf, rapidfuzz, openpyxl, xlrd, pytest

---

## Planned File Layout

- `.gitignore`
  Add Python cache, local virtualenv, and temporary output ignores for the new backend.
- `vite.config.ts`
  Add a local `/api` proxy to the Python service during development.
- `README.md`
  Update product description and local run instructions for the new frontend + backend split.
- `docs/deployment/1panel-pdf-team-splitter.md`
  Record the concrete 1Panel / Nginx deployment steps and reverse-proxy rules.
- `server/__init__.py`
  Mark `server` as a Python package.
- `server/requirements.txt`
  Python runtime and test dependencies for the API service.
- `server/app.py`
  FastAPI application and the `POST /api/pdf-team-split` route.
- `server/pdf_team_splitter/__init__.py`
  Export the orchestration helpers for the API layer.
- `server/pdf_team_splitter/team_roster.py`
  Ported roster loader from `E:\code\pdftool`.
- `server/pdf_team_splitter/pdf_parser.py`
  Ported PDF scanner from `E:\code\pdftool`.
- `server/pdf_team_splitter/matcher.py`
  Ported match logic from `E:\code\pdftool`.
- `server/pdf_team_splitter/reporting.py`
  Ported CSV reporting helpers from `E:\code\pdftool`.
- `server/pdf_team_splitter/writer.py`
  Ported PDF output writer from `E:\code\pdftool`.
- `server/pdf_team_splitter/service.py`
  Request object, orchestration, zip creation, and cleanup helpers.
- `server/tests/pdf_team_splitter/test_team_roster.py`
  Copied and adapted regression tests for roster loading.
- `server/tests/pdf_team_splitter/test_pdf_parser.py`
  Copied and adapted regression tests for PDF parsing.
- `server/tests/pdf_team_splitter/test_matcher.py`
  Copied and adapted regression tests for matching.
- `server/tests/pdf_team_splitter/test_reporting.py`
  Copied and adapted regression tests for reporting.
- `server/tests/pdf_team_splitter/test_writer.py`
  Copied and adapted regression tests for PDF writing.
- `server/tests/test_service.py`
  New orchestration and zip-bundle tests.
- `server/tests/test_api.py`
  New FastAPI upload / response tests.
- `src/api/pdfTeamSplit.ts`
  Frontend request and download helpers for the PDF splitter page.
- `src/router/index.ts`
  Add the new tool route and make sure navigation metadata is present.
- `src/router/__tests__/index.test.ts`
  Update route expectations to include the new tool.
- `src/layout/index.vue`
  Add a second sidebar entry for the PDF splitter page.
- `src/views/pdf-team-splitter/index.vue`
  New upload-and-download page.
- `src/views/pdf-team-splitter/__tests__/index.test.ts`
  UI tests for required files, loading state, success download, and error feedback.

## Preflight

- Use the local Python launcher from PowerShell:

```powershell
py -3.12 --version
```

Expected: output starting with `Python 3.12`

- Install Node dependencies if needed:

```powershell
npm install
```

Expected: install completes without `ERR!`

### Task 1: Bootstrap The Python Backend Workspace

**Files:**
- Modify: `.gitignore`
- Modify: `vite.config.ts`
- Create: `server/__init__.py`
- Create: `server/requirements.txt`

- [ ] **Step 1: Add backend dependency manifest**

Create `server/requirements.txt` with:

```text
fastapi>=0.116,<1.0
uvicorn[standard]>=0.35,<1.0
python-multipart>=0.0.20,<1.0
pandas>=2.2,<3.0
pypdf>=5.0,<6.0
rapidfuzz>=3.9,<4.0
openpyxl>=3.1,<4.0
xlrd>=2.0,<3.0
pytest>=8.2,<9.0
httpx>=0.28,<1.0
```

- [ ] **Step 2: Ignore backend caches and temp files**

Append these lines to `.gitignore`:

```gitignore
__pycache__/
*.pyc
server/.venv/
server/.pytest_cache/
server/tmp/
```

- [ ] **Step 3: Mark the backend directory as a Python package**

Create `server/__init__.py` with:

```python
"""Backend package for the internal tools site."""
```

- [ ] **Step 4: Add a local `/api` proxy to Vite**

Update `vite.config.ts` so the exported config includes:

```ts
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8001',
      changeOrigin: true,
    },
  },
},
```

- [ ] **Step 5: Install Python dependencies**

Run:

```powershell
py -3.12 -m pip install -r server/requirements.txt
```

Expected: output includes `Successfully installed` or `Requirement already satisfied`

- [ ] **Step 6: Commit the bootstrap**

```powershell
git add .gitignore vite.config.ts server/__init__.py server/requirements.txt
git commit -m "chore: bootstrap pdf splitter backend workspace"
```

### Task 2: Port The Validated PDF Processor Package

**Files:**
- Create: `server/pdf_team_splitter/__init__.py`
- Create: `server/pdf_team_splitter/team_roster.py`
- Create: `server/pdf_team_splitter/pdf_parser.py`
- Create: `server/pdf_team_splitter/matcher.py`
- Create: `server/pdf_team_splitter/reporting.py`
- Create: `server/pdf_team_splitter/writer.py`
- Create: `server/tests/pdf_team_splitter/test_team_roster.py`
- Create: `server/tests/pdf_team_splitter/test_pdf_parser.py`
- Create: `server/tests/pdf_team_splitter/test_matcher.py`
- Create: `server/tests/pdf_team_splitter/test_reporting.py`
- Create: `server/tests/pdf_team_splitter/test_writer.py`

- [ ] **Step 1: Copy the validated regression tests from `pdftool` first**

Run:

```powershell
New-Item -ItemType Directory -Force server\tests\pdf_team_splitter | Out-Null
Copy-Item E:\code\pdftool\tests\test_team_roster.py server\tests\pdf_team_splitter\test_team_roster.py
Copy-Item E:\code\pdftool\tests\test_pdf_parser.py server\tests\pdf_team_splitter\test_pdf_parser.py
Copy-Item E:\code\pdftool\tests\test_matcher.py server\tests\pdf_team_splitter\test_matcher.py
Copy-Item E:\code\pdftool\tests\test_reporting.py server\tests\pdf_team_splitter\test_reporting.py
Copy-Item E:\code\pdftool\tests\test_writer.py server\tests\pdf_team_splitter\test_writer.py
```

- [ ] **Step 2: Rewrite the copied test imports to target the new package**

Replace the top-level imports so they read like this:

```python
from server.pdf_team_splitter.pdf_parser import PageScan
from server.pdf_team_splitter.team_roster import load_roster
from server.pdf_team_splitter.matcher import MatchResults, PageMatch, ReportRow, match_pages
from server.pdf_team_splitter.reporting import build_summary, print_summary, write_report
from server.pdf_team_splitter.writer import order_matches_for_team, write_team_pdfs
```

- [ ] **Step 3: Run the copied tests and confirm they fail because the package does not exist yet**

Run:

```powershell
py -3.12 -m pytest server/tests/pdf_team_splitter -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'server.pdf_team_splitter'`

- [ ] **Step 4: Copy the validated processor modules from `pdftool`**

Run:

```powershell
New-Item -ItemType Directory -Force server\pdf_team_splitter | Out-Null
Copy-Item E:\code\pdftool\team_roster.py server\pdf_team_splitter\team_roster.py
Copy-Item E:\code\pdftool\pdf_parser.py server\pdf_team_splitter\pdf_parser.py
Copy-Item E:\code\pdftool\matcher.py server\pdf_team_splitter\matcher.py
Copy-Item E:\code\pdftool\reporting.py server\pdf_team_splitter\reporting.py
Copy-Item E:\code\pdftool\writer.py server\pdf_team_splitter\writer.py
```

- [ ] **Step 5: Fix the copied modules to use package-relative imports**

Apply these import changes:

```python
# server/pdf_team_splitter/pdf_parser.py
from .team_roster import normalize_name

# server/pdf_team_splitter/matcher.py
from .pdf_parser import PageScan
from .team_roster import RosterData

# server/pdf_team_splitter/reporting.py
from .matcher import MatchResults, ReportRow
from .pdf_parser import PageScan
from .team_roster import RosterData

# server/pdf_team_splitter/writer.py
from .matcher import PageMatch
```

- [ ] **Step 6: Run the copied processor tests and confirm they pass**

Run:

```powershell
py -3.12 -m pytest server/tests/pdf_team_splitter -v
```

Expected: all copied processor tests pass

- [ ] **Step 7: Commit the ported processor package**

```powershell
git add server/pdf_team_splitter server/tests/pdf_team_splitter
git commit -m "feat: port pdf team splitter processor package"
```

### Task 3: Add Orchestration And Zip Packaging

**Files:**
- Create: `server/pdf_team_splitter/service.py`
- Create: `server/tests/test_service.py`

- [ ] **Step 1: Write failing orchestration tests**

Create `server/tests/test_service.py` with:

```python
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile

from server.pdf_team_splitter.service import (
    PdfTeamSplitRequest,
    build_result_zip,
    process_pdf_team_split,
)


def test_build_result_zip_includes_generated_pdfs_and_report(tmp_path: Path):
    output_dir = tmp_path / 'output'
    output_dir.mkdir()
    (output_dir / 'A团_行程单.pdf').write_bytes(b'%PDF-A%')
    (output_dir / 'B团_行程单.pdf').write_bytes(b'%PDF-B%')
    (output_dir / 'match_report.csv').write_text(
        'team_name,match_status\nA团,matched_exact\n',
        encoding='utf-8-sig',
    )

    zip_path = build_result_zip(output_dir, tmp_path / 'result.zip')

    with ZipFile(zip_path) as archive:
        assert sorted(archive.namelist()) == [
            'A团_行程单.pdf',
            'B团_行程单.pdf',
            'match_report.csv',
        ]


def test_process_pdf_team_split_passes_request_options_to_pipeline(
    monkeypatch,
    tmp_path: Path,
):
    captured: dict[str, object] = {}
    roster = SimpleNamespace(entries=[object()], groups_by_name={'A': object()})
    page_scans = [object()]
    match_results = SimpleNamespace(accepted_matches=[], report_rows=[])
    written_files = [tmp_path / 'output' / 'A团_行程单.pdf']

    def fake_load_roster(path, **kwargs):
        captured['load_roster'] = {'path': Path(path), **kwargs}
        return roster

    def fake_scan_pdf(path):
        captured['scan_pdf'] = Path(path)
        return page_scans

    def fake_match_pages(*_args, **kwargs):
        captured['match_pages'] = kwargs
        return match_results

    def fake_write_team_pdfs(**kwargs):
        captured['write_team_pdfs'] = kwargs
        return written_files

    monkeypatch.setattr('server.pdf_team_splitter.service.load_roster', fake_load_roster)
    monkeypatch.setattr('server.pdf_team_splitter.service.scan_pdf', fake_scan_pdf)
    monkeypatch.setattr('server.pdf_team_splitter.service.match_pages', fake_match_pages)
    monkeypatch.setattr('server.pdf_team_splitter.service.write_team_pdfs', fake_write_team_pdfs)
    monkeypatch.setattr(
        'server.pdf_team_splitter.service.write_report',
        lambda rows, report_path: Path(report_path).write_text(
            'team_name,match_status\nA团,matched_exact\n',
            encoding='utf-8-sig',
        ),
    )
    monkeypatch.setattr(
        'server.pdf_team_splitter.service.build_summary',
        lambda **_kwargs: {'generated_team_pdf_count': 1},
    )

    request = PdfTeamSplitRequest(
        roster_path=tmp_path / 'roster.xlsx',
        pdf_path=tmp_path / 'input.pdf',
        output_dir=tmp_path / 'output',
        sheet='旅客名单',
        name_column='旅客姓名',
        team_column='团名',
        fuzzy_threshold=88,
    )

    result = process_pdf_team_split(request)

    assert result.report_path.name == 'match_report.csv'
    assert captured['load_roster']['sheet'] == '旅客名单'
    assert captured['load_roster']['name_column'] == '旅客姓名'
    assert captured['load_roster']['team_column'] == '团名'
    assert captured['match_pages']['fuzzy_threshold'] == 88
```

- [ ] **Step 2: Run the service tests and confirm they fail**

Run:

```powershell
py -3.12 -m pytest server/tests/test_service.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'server.pdf_team_splitter.service'`

- [ ] **Step 3: Implement the service layer**

Create `server/pdf_team_splitter/service.py` with:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from .matcher import MatchResults, match_pages
from .pdf_parser import PageScan, scan_pdf
from .reporting import build_summary, write_report
from .team_roster import DEFAULT_NAME_COLUMN, DEFAULT_TEAM_COLUMN, RosterData, load_roster
from .writer import write_team_pdfs


@dataclass(frozen=True)
class PdfTeamSplitRequest:
    roster_path: Path
    pdf_path: Path
    output_dir: Path
    sheet: str | int | None = None
    name_column: str = DEFAULT_NAME_COLUMN
    team_column: str = DEFAULT_TEAM_COLUMN
    fuzzy_threshold: int = 90


@dataclass(frozen=True)
class PdfTeamSplitResult:
    written_files: list[Path]
    report_path: Path
    summary: dict[str, object]


def process_pdf_team_split(request: PdfTeamSplitRequest) -> PdfTeamSplitResult:
    request.output_dir.mkdir(parents=True, exist_ok=True)

    roster: RosterData = load_roster(
        request.roster_path,
        sheet=request.sheet,
        name_column=request.name_column,
        team_column=request.team_column,
    )
    page_scans: list[PageScan] = scan_pdf(request.pdf_path)
    match_results: MatchResults = match_pages(
        roster,
        page_scans,
        fuzzy_threshold=request.fuzzy_threshold,
    )
    report_path = request.output_dir / 'match_report.csv'
    written_files = write_team_pdfs(
        pdf_path=request.pdf_path,
        matches=match_results.accepted_matches,
        outdir=request.output_dir,
    )
    write_report(match_results.report_rows, report_path)
    summary = build_summary(
        roster=roster,
        page_scans=page_scans,
        match_results=match_results,
        written_files=written_files,
        report_path=report_path,
    )

    return PdfTeamSplitResult(
        written_files=written_files,
        report_path=report_path,
        summary=summary,
    )


def build_result_zip(output_dir: Path, zip_path: Path) -> Path:
    with ZipFile(zip_path, 'w', compression=ZIP_DEFLATED) as archive:
        for path in sorted(output_dir.iterdir(), key=lambda item: item.name):
            if path.is_file():
                archive.write(path, arcname=path.name)
    return zip_path
```

- [ ] **Step 4: Run the service tests and confirm they pass**

Run:

```powershell
py -3.12 -m pytest server/tests/test_service.py -v
```

Expected: `2 passed`

- [ ] **Step 5: Commit the service layer**

```powershell
git add server/pdf_team_splitter/service.py server/tests/test_service.py
git commit -m "feat: add pdf splitter orchestration service"
```

### Task 4: Add The FastAPI Upload Endpoint

**Files:**
- Create: `server/app.py`
- Modify: `server/pdf_team_splitter/__init__.py`
- Create: `server/tests/test_api.py`

- [ ] **Step 1: Write failing API tests**

Create `server/tests/test_api.py` with:

```python
from pathlib import Path
from zipfile import ZipFile

from fastapi.testclient import TestClient

from server.app import app


def test_post_pdf_team_split_requires_files():
    client = TestClient(app)

    response = client.post('/api/pdf-team-split')

    assert response.status_code == 422


def test_post_pdf_team_split_returns_zip_response(monkeypatch, tmp_path: Path):
    client = TestClient(app)
    output_dir = tmp_path / 'output'
    output_dir.mkdir()
    report_path = output_dir / 'match_report.csv'
    report_path.write_text('team_name,match_status\nA团,matched_exact\n', encoding='utf-8-sig')
    zip_path = tmp_path / 'result.zip'
    with ZipFile(zip_path, 'w') as archive:
        archive.write(report_path, arcname='match_report.csv')

    captured: dict[str, object] = {}

    def fake_process(request):
        captured['sheet'] = request.sheet
        captured['name_column'] = request.name_column
        captured['team_column'] = request.team_column
        captured['fuzzy_threshold'] = request.fuzzy_threshold
        return type(
            'Result',
            (),
            {
                'written_files': [],
                'report_path': report_path,
                'summary': {'generated_team_pdf_count': 0},
            },
        )()

    monkeypatch.setattr('server.app.process_pdf_team_split', fake_process)
    monkeypatch.setattr('server.app.build_result_zip', lambda _output_dir, _zip_path: zip_path)

    response = client.post(
        '/api/pdf-team-split',
        files={
            'roster': (
                'roster.csv',
                '姓名,团队\nZHU/XIUWU,A团\n'.encode('utf-8-sig'),
                'text/csv',
            ),
            'pdf': ('input.pdf', b'%PDF-1.4\n', 'application/pdf'),
        },
        data={
            'sheet': 'Sheet1',
            'name_column': '姓名',
            'team_column': '团队',
            'fuzzy_threshold': '87',
        },
    )

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/zip'
    assert 'attachment;' in response.headers['content-disposition']
    assert captured == {
        'sheet': 'Sheet1',
        'name_column': '姓名',
        'team_column': '团队',
        'fuzzy_threshold': 87,
    }


def test_post_pdf_team_split_returns_json_on_processing_error(monkeypatch):
    client = TestClient(app)

    monkeypatch.setattr(
        'server.app.process_pdf_team_split',
        lambda _request: (_ for _ in ()).throw(ValueError('bad input')),
    )

    response = client.post(
        '/api/pdf-team-split',
        files={
            'roster': ('roster.csv', '姓名,团队\nZHU/XIUWU,A团\n'.encode('utf-8-sig'), 'text/csv'),
            'pdf': ('input.pdf', b'%PDF-1.4\n', 'application/pdf'),
        },
    )

    assert response.status_code == 400
    assert response.json()['message'] == 'bad input'
```

- [ ] **Step 2: Run the API tests and confirm they fail**

Run:

```powershell
py -3.12 -m pytest server/tests/test_api.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'server.app'`

- [ ] **Step 3: Implement the FastAPI app**

Create `server/app.py` with:

```python
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from tempfile import mkdtemp

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from .pdf_team_splitter import (
    PdfTeamSplitRequest,
    build_result_zip,
    process_pdf_team_split,
)

app = FastAPI(title='PDF Team Splitter API')


def _cleanup_tree(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)


def _save_upload(upload: UploadFile, target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open('wb') as stream:
        upload.file.seek(0)
        shutil.copyfileobj(upload.file, stream)


@app.post('/api/pdf-team-split')
async def pdf_team_split(
    roster: UploadFile = File(...),
    pdf: UploadFile = File(...),
    sheet: str | None = Form(None),
    name_column: str = Form('姓名'),
    team_column: str = Form('团队'),
    fuzzy_threshold: int = Form(90),
):
    work_dir = Path(mkdtemp(prefix='pdf-team-split-', dir='server/tmp'))
    upload_dir = work_dir / 'uploads'
    output_dir = work_dir / 'output'

    try:
        roster_path = upload_dir / roster.filename
        pdf_path = upload_dir / pdf.filename
        _save_upload(roster, roster_path)
        _save_upload(pdf, pdf_path)

        result = process_pdf_team_split(
            PdfTeamSplitRequest(
                roster_path=roster_path,
                pdf_path=pdf_path,
                output_dir=output_dir,
                sheet=sheet,
                name_column=name_column,
                team_column=team_column,
                fuzzy_threshold=fuzzy_threshold,
            )
        )

        zip_name = f"pdf-team-split-{datetime.now().strftime('%Y%m%d-%H%M%S')}.zip"
        zip_path = build_result_zip(result.report_path.parent, work_dir / zip_name)
        response = FileResponse(
            zip_path,
            media_type='application/zip',
            filename=zip_name,
        )
        response.call_on_close(lambda: _cleanup_tree(work_dir))
        return response
    except ValueError as exc:
        _cleanup_tree(work_dir)
        return JSONResponse(status_code=400, content={'message': str(exc)})
    except Exception as exc:
        _cleanup_tree(work_dir)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
```

- [ ] **Step 4: Export the service layer from the package**

Create `server/pdf_team_splitter/__init__.py` with:

```python
from .service import PdfTeamSplitRequest, PdfTeamSplitResult, build_result_zip, process_pdf_team_split

__all__ = [
    'PdfTeamSplitRequest',
    'PdfTeamSplitResult',
    'build_result_zip',
    'process_pdf_team_split',
]
```

- [ ] **Step 5: Run the API tests and confirm they pass**

Run:

```powershell
py -3.12 -m pytest server/tests/test_api.py -v
```

Expected: `3 passed`

- [ ] **Step 6: Commit the API service**

```powershell
git add server/app.py server/pdf_team_splitter/__init__.py server/tests/test_api.py
git commit -m "feat: add pdf splitter upload api"
```

### Task 5: Add The Frontend Route, Page, And Download Flow

**Files:**
- Create: `src/api/pdfTeamSplit.ts`
- Create: `src/views/pdf-team-splitter/index.vue`
- Create: `src/views/pdf-team-splitter/__tests__/index.test.ts`
- Modify: `src/router/index.ts`
- Modify: `src/router/__tests__/index.test.ts`
- Modify: `src/layout/index.vue`

- [ ] **Step 1: Write failing route and page tests**

Create `src/views/pdf-team-splitter/__tests__/index.test.ts` with:

```ts
import { flushPromises, mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import { describe, expect, it, vi } from 'vitest'

import PdfTeamSplitterView from '../index.vue'

vi.mock('@/api/pdfTeamSplit', () => ({
  requestPdfTeamSplit: vi.fn(),
  downloadPdfTeamSplitResult: vi.fn(),
}))

vi.mock('element-plus', async () => {
  const actual = await vi.importActual<typeof import('element-plus')>('element-plus')

  return {
    ...actual,
    ElMessage: {
      success: vi.fn(),
      warning: vi.fn(),
      error: vi.fn(),
    },
  }
})

describe('pdf team splitter view', () => {
  it('requires both files before submission', async () => {
    const wrapper = mount(PdfTeamSplitterView, {
      global: { plugins: [ElementPlus] },
    })

    expect(wrapper.text()).toContain('PDF 行程整理')
    expect(wrapper.find('button.el-button--primary').attributes('disabled')).toBeDefined()
  })

  it('submits files and downloads the returned zip', async () => {
    const { requestPdfTeamSplit, downloadPdfTeamSplitResult } = await import('@/api/pdfTeamSplit')
    vi.mocked(requestPdfTeamSplit).mockResolvedValue(new Blob(['zip'], { type: 'application/zip' }))

    const wrapper = mount(PdfTeamSplitterView, {
      global: { plugins: [ElementPlus] },
    })

    const [rosterInput, pdfInput] = wrapper.findAll('input[type="file"]')
    const rosterFile = new File(['姓名,团队\nZHU/XIUWU,A团\n'], 'roster.csv', { type: 'text/csv' })
    const pdfFile = new File(['%PDF-1.4\n'], 'input.pdf', { type: 'application/pdf' })

    await rosterInput!.setValue([rosterFile])
    await pdfInput!.setValue([pdfFile])
    await wrapper.find('button.el-button--primary').trigger('click')
    await flushPromises()

    expect(requestPdfTeamSplit).toHaveBeenCalledOnce()
    expect(downloadPdfTeamSplitResult).toHaveBeenCalledOnce()
  })
})
```

Update `src/router/__tests__/index.test.ts` to:

```ts
import { describe, expect, it } from 'vitest'

import { constantRoutes } from '../index'

describe('router config', () => {
  it('exposes the text formatter and pdf team splitter tools', () => {
    const rootRoute = constantRoutes.find((route) => route.path === '/')

    expect(rootRoute?.redirect).toBe('/text-formatter')
    expect(rootRoute?.children).toHaveLength(2)
    expect(rootRoute?.children?.map((route) => route.path)).toEqual([
      'text-formatter',
      'pdf-team-splitter',
    ])
  })
})
```

- [ ] **Step 2: Run the frontend tests and confirm they fail**

Run:

```powershell
npm run test -- src/router/__tests__/index.test.ts src/views/pdf-team-splitter/__tests__/index.test.ts
```

Expected: FAIL because the route, page, or API helper does not exist yet

- [ ] **Step 3: Add the frontend request helper**

Create `src/api/pdfTeamSplit.ts` with:

```ts
export interface PdfTeamSplitPayload {
  roster: File
  pdf: File
  sheet?: string
  nameColumn?: string
  teamColumn?: string
  fuzzyThreshold?: number
}

export async function requestPdfTeamSplit(payload: PdfTeamSplitPayload): Promise<Blob> {
  const body = new FormData()
  body.set('roster', payload.roster)
  body.set('pdf', payload.pdf)
  if (payload.sheet) body.set('sheet', payload.sheet)
  if (payload.nameColumn) body.set('name_column', payload.nameColumn)
  if (payload.teamColumn) body.set('team_column', payload.teamColumn)
  if (payload.fuzzyThreshold !== undefined) {
    body.set('fuzzy_threshold', String(payload.fuzzyThreshold))
  }

  const response = await fetch('/api/pdf-team-split', {
    method: 'POST',
    body,
  })

  if (!response.ok) {
    const data = (await response.json().catch(() => ({ message: '处理失败' }))) as {
      message?: string
      detail?: string
    }
    throw new Error(data.message ?? data.detail ?? '处理失败')
  }

  return response.blob()
}

export function downloadPdfTeamSplitResult(blob: Blob, filename = 'pdf-team-split-result.zip') {
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  anchor.click()
  URL.revokeObjectURL(url)
}
```

- [ ] **Step 4: Add the new page, route, and navigation item**

Create `src/views/pdf-team-splitter/index.vue` with:

```vue
<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { Files, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

import { downloadPdfTeamSplitResult, requestPdfTeamSplit } from '@/api/pdfTeamSplit'

const rosterFile = ref<File | null>(null)
const pdfFile = ref<File | null>(null)
const loading = ref(false)
const form = reactive({
  sheet: '',
  nameColumn: '姓名',
  teamColumn: '团队',
  fuzzyThreshold: 90,
})

const canSubmit = computed(() => Boolean(rosterFile.value && pdfFile.value && !loading.value))

const onRosterChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  rosterFile.value = input.files?.[0] ?? null
}

const onPdfChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  pdfFile.value = input.files?.[0] ?? null
}

const submit = async () => {
  if (!rosterFile.value || !pdfFile.value) {
    ElMessage.warning('请先选择人员表和 PDF 文件')
    return
  }

  loading.value = true
  try {
    const blob = await requestPdfTeamSplit({
      roster: rosterFile.value,
      pdf: pdfFile.value,
      sheet: form.sheet || undefined,
      nameColumn: form.nameColumn || undefined,
      teamColumn: form.teamColumn || undefined,
      fuzzyThreshold: form.fuzzyThreshold,
    })
    downloadPdfTeamSplitResult(blob)
    ElMessage.success('处理完成，开始下载结果')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '处理失败')
  } finally {
    loading.value = false
  }
}
</script>
```

and the matching template structure:

```vue
<template>
  <div class="tool-view">
    <div class="tool-header">
      <h2>PDF 行程整理</h2>
      <p class="tool-desc">上传人员表和行程单 PDF，按团队拆分并下载 zip 结果包。</p>
    </div>

    <div class="tool-layout">
      <div class="tool-main">
        <label class="upload-card">
          <span class="upload-title">人员表</span>
          <input type="file" accept=".xlsx,.xls,.csv" @change="onRosterChange" />
          <span>{{ rosterFile?.name ?? '选择 Excel/CSV 文件' }}</span>
        </label>

        <label class="upload-card">
          <span class="upload-title">PDF</span>
          <input type="file" accept=".pdf" @change="onPdfChange" />
          <span>{{ pdfFile?.name ?? '选择 PDF 文件' }}</span>
        </label>

        <el-input v-model="form.sheet" placeholder="Sheet 名称或序号（可选）" />
        <el-input v-model="form.nameColumn" placeholder="姓名列名" />
        <el-input v-model="form.teamColumn" placeholder="团队列名" />
        <el-input-number v-model="form.fuzzyThreshold" :min="0" :max="100" />

        <div class="actions-section">
          <el-button type="primary" size="large" :icon="Download" :loading="loading" :disabled="!canSubmit" @click="submit">
            开始整理并下载
          </el-button>
        </div>
      </div>

      <div class="tool-guide">
        <div class="guide-card">
          <h3>使用说明</h3>
          <ul class="guide-list">
            <li>人员表支持 xlsx、xls、csv</li>
            <li>PDF 需为可提取文本的行程单</li>
            <li>下载结果为 zip，包含团队 PDF 和 match_report.csv</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
```

Update `src/router/index.ts` so the root route children include:

```ts
{
  path: 'pdf-team-splitter',
  component: () => import('@/views/pdf-team-splitter/index.vue'),
  name: 'PdfTeamSplitter',
  meta: {
    title: 'PDF 行程整理',
    icon: 'Files',
  },
},
```

Update `src/layout/index.vue` menu items to include:

```ts
{
  path: '/pdf-team-splitter',
  name: 'PdfTeamSplitter',
  title: 'PDF 行程整理',
  icon: Files,
},
```

- [ ] **Step 5: Run the frontend tests and confirm they pass**

Run:

```powershell
npm run test -- src/router/__tests__/index.test.ts src/views/pdf-team-splitter/__tests__/index.test.ts
```

Expected: tests pass

- [ ] **Step 6: Commit the frontend integration**

```powershell
git add src/api/pdfTeamSplit.ts src/router/index.ts src/router/__tests__/index.test.ts src/layout/index.vue src/views/pdf-team-splitter
git commit -m "feat: add pdf team splitter frontend"
```

### Task 6: Document Deployment And Run Full Verification

**Files:**
- Modify: `README.md`
- Create: `docs/deployment/1panel-pdf-team-splitter.md`

- [ ] **Step 1: Update the root README**

Rewrite the relevant sections so `README.md` includes:

```text
## 工具列表

- 文本整理：浏览器本地提取旅客信息
- PDF 行程整理：上传人员表和 PDF，由本机 Python 服务处理后返回 zip

## 本地开发

### 前端

npm run dev

### 后端

py -3.12 -m uvicorn server.app:app --host 127.0.0.1 --port 8001
```

- [ ] **Step 2: Add the 1Panel deployment guide**

Create `docs/deployment/1panel-pdf-team-splitter.md` with:

```text
# 1Panel Deployment Notes

## Frontend

- Build:
  - `npm run build`
- Deploy `dist/` as the static site root

## Backend

- Install deps:
  - `py -3.12 -m pip install -r server/requirements.txt`
- Run:
  - `py -3.12 -m uvicorn server.app:app --host 127.0.0.1 --port 8001`

## Nginx

location / {
  try_files $uri $uri/ /index.html;
}

location /api/ {
  proxy_pass http://127.0.0.1:8001;
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

## Access Protection

- Enable Basic Auth or the equivalent 1Panel access password for the whole site.
```

- [ ] **Step 3: Run backend tests**

Run:

```powershell
py -3.12 -m pytest server/tests -v
```

Expected: backend tests all pass

- [ ] **Step 4: Run frontend tests**

Run:

```powershell
npm run test
```

Expected: frontend tests all pass

- [ ] **Step 5: Run type-check and build**

Run:

```powershell
npm run type-check
npm run build
```

Expected:

- `type-check` exits with code `0`
- `build` ends with Vite build success output

- [ ] **Step 6: Commit docs and final verification**

```powershell
git add README.md docs/deployment/1panel-pdf-team-splitter.md
git commit -m "docs: add pdf splitter deployment guide"
```

## Spec Coverage Check

- New standalone tool route and page: covered by Task 5 route, layout, and page files.
- Upload roster and PDF from the frontend: covered by Task 5 page component.
- Optional `sheet`, `name_column`, `team_column`, `fuzzy_threshold`: covered by Tasks 3, 4, and 5.
- Python API under `/api/pdf-team-split`: covered by Task 4.
- Reuse existing PDF logic from `pdftool`: covered by Task 2 package port.
- Return a single zip containing team PDFs and `match_report.csv`: covered by Task 3 zip helper and Task 4 API response.
- Public password protection via Nginx / 1Panel: documented in Task 6 deployment guide.
- Same-origin `/api` plus local development proxy: covered by Task 1 and Task 5.
- Synchronous processing flow: covered by Tasks 3, 4, and 5.
- Error JSON responses: covered by Task 4 API tests and implementation.

## Execution Notes

- Execute tasks in order.
- Do not skip the failing-test steps; they are the guardrail for the integration work.
- Keep the backend self-contained under `server/`; do not make the deployed app depend on `E:\code\pdftool` at runtime.
- If copied `pdftool` modules require further fixes after import changes, apply them in the processor package and rerun the copied regression tests before moving on.
