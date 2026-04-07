A plan that follows the writing-plans skill while staying inside the server tree.

# PDF Team Splitter Porting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to run this plan inline.

**Goal:** Move the validated PDF team splitter modules and their regression suite from the pdftool prototype into `server.pdf_team_splitter`, keeping the same behavior while exposing them as a proper package.

**Architecture:** Treat each module (roster, PDF scanning, matcher, reporting, writer) as a standalone unit, copy it into the backend package, and then switch all intra-package imports to relative references so the package is self-contained. The regression suite lives alongside the ported modules so backend developers can continue to validate functionality via pytest.

**Tech Stack:** Python 3.12, pandas, pypdf, rapidfuzz, pytest.

---

### Task 1: Populate the `server.pdf_team_splitter` package with the validated modules

**Files:**
- Create: `server/pdf_team_splitter/__init__.py`
- Create: `server/pdf_team_splitter/team_roster.py`
- Create: `server/pdf_team_splitter/pdf_parser.py`
- Create: `server/pdf_team_splitter/matcher.py`
- Create: `server/pdf_team_splitter/reporting.py`
- Create: `server/pdf_team_splitter/writer.py`

- [ ] Step 1: Re-run the directory creation command.
  ```powershell
  New-Item -ItemType Directory -Path server\pdf_team_splitter -Force
  ```

- [ ] Step 2: Create `__init__.py` with a simple module-level docstring.
  ```python
  """Team splitter backend utilities ported from pdftool."""
  ```

- [ ] Step 3: Copy `team_roster.py`.
  ```powershell
  Copy-Item -LiteralPath E:\code\pdftool\team_roster.py -Destination server\pdf_team_splitter\team_roster.py -Force
  ```

- [ ] Step 4: Copy `pdf_parser.py`.
  ```powershell
  Copy-Item -LiteralPath E:\code\pdftool\pdf_parser.py -Destination server\pdf_team_splitter\pdf_parser.py -Force
  ```

- [ ] Step 5: Copy `matcher.py`.
  ```powershell
  Copy-Item -LiteralPath E:\code\pdftool\matcher.py -Destination server\pdf_team_splitter\matcher.py -Force
  ```

- [ ] Step 6: Copy `reporting.py`.
  ```powershell
  Copy-Item -LiteralPath E:\code\pdftool\reporting.py -Destination server\pdf_team_splitter\reporting.py -Force
  ```

- [ ] Step 7: Copy `writer.py`.
  ```powershell
  Copy-Item -LiteralPath E:\code\pdftool\writer.py -Destination server\pdf_team_splitter\writer.py -Force
  ```

### Task 2: Switch the module imports to package-relative references

**Files:**
- Modify: `server/pdf_team_splitter/pdf_parser.py`
- Modify: `server/pdf_team_splitter/matcher.py`
- Modify: `server/pdf_team_splitter/reporting.py`
- Modify: `server/pdf_team_splitter/writer.py`

- [ ] Step 1: Update `pdf_parser.py` to import `normalize_name` from `.team_roster`.
  ```python
  from pypdf import PdfReader

  from .team_roster import normalize_name
  ```

- [ ] Step 2: Update `matcher.py` to import `PageScan` and `RosterData`.
  ```python
  from rapidfuzz import fuzz, process

  from .pdf_parser import PageScan
  from .team_roster import RosterData
  ```

- [ ] Step 3: Update `reporting.py` to import domain classes locally.
  ```python
  from .matcher import MatchResults, ReportRow
  from .pdf_parser import PageScan
  from .team_roster import RosterData
  ```

- [ ] Step 4: Update `writer.py` to import `PageMatch`.
  ```python
  from .matcher import PageMatch
  ```

### Task 3: Bring the regression tests under `server/tests/pdf_team_splitter` and point them at the package

**Files:**
- Create: `server/tests/pdf_team_splitter/test_team_roster.py`
- Create: `server/tests/pdf_team_splitter/test_pdf_parser.py`
- Create: `server/tests/pdf_team_splitter/test_matcher.py`
- Create: `server/tests/pdf_team_splitter/test_reporting.py`
- Create: `server/tests/pdf_team_splitter/test_writer.py`

- [ ] Step 1: Create the target test directory.
  ```powershell
  New-Item -ItemType Directory -Path server\tests\pdf_team_splitter -Force
  ```

- [ ] Step 2: Copy `test_team_roster.py`.
  ```powershell
  Copy-Item -LiteralPath E:\code\pdftool\tests\test_team_roster.py -Destination server\tests\pdf_team_splitter\test_team_roster.py -Force
  ```

- [ ] Step 3: Copy `test_pdf_parser.py`.
  ```powershell
  Copy-Item -LiteralPath E:\code\pdftool\tests\test_pdf_parser.py -Destination server\tests\pdf_team_splitter\test_pdf_parser.py -Force
  ```

- [ ] Step 4: Copy `test_matcher.py`.
  ```powershell
  Copy-Item -LiteralPath E:\code\pdftool\tests\test_matcher.py -Destination server\tests\pdf_team_splitter\test_matcher.py -Force
  ```

- [ ] Step 5: Copy `test_reporting.py`.
  ```powershell
  Copy-Item -LiteralPath E:\code\pdftool\tests\test_reporting.py -Destination server\tests\pdf_team_splitter\test_reporting.py -Force
  ```

- [ ] Step 6: Copy `test_writer.py`.
  ```powershell
  Copy-Item -LiteralPath E:\code\pdftool\tests\test_writer.py -Destination server\tests\pdf_team_splitter\test_writer.py -Force
  ```

- [ ] Step 7: Update `test_team_roster.py` imports.
  ```python
  from server.pdf_team_splitter.team_roster import load_roster, normalize_name
  ```

- [ ] Step 8: Update `test_pdf_parser.py` imports and monkeypatch target.
  ```python
  from server.pdf_team_splitter.pdf_parser import extract_candidate_name, scan_pdf
  monkeypatch.setattr("server.pdf_team_splitter.pdf_parser.PdfReader", FakeReader)
  ```

- [ ] Step 9: Update `test_matcher.py` imports.
  ```python
  from server.pdf_team_splitter.pdf_parser import PageScan
  from server.pdf_team_splitter.team_roster import DEFAULT_NAME_COLUMN, DEFAULT_TEAM_COLUMN, load_roster
  from server.pdf_team_splitter.matcher import match_pages
  ```

- [ ] Step 10: Update `test_reporting.py` imports.
  ```python
  from server.pdf_team_splitter.matcher import MatchResults, PageMatch, ReportRow
  from server.pdf_team_splitter.pdf_parser import PageScan
  from server.pdf_team_splitter.reporting import build_summary, print_summary, write_report
  from server.pdf_team_splitter.team_roster import RosterData, RosterEntry, RosterGroup, load_roster
  ```

- [ ] Step 11: Update `test_writer.py` imports and monkeypatch paths.
  ```python
  from server.pdf_team_splitter.matcher import PageMatch
  from server.pdf_team_splitter.writer import order_matches_for_team, write_team_pdfs
  monkeypatch.setattr("server.pdf_team_splitter.writer.PdfReader", FakeReader)
  monkeypatch.setattr("server.pdf_team_splitter.writer.PdfWriter", FakeWriter)
  ```

### Task 4: Verify the regression suite and commit

**Files:**
- Modify: everything under `server/pdf_team_splitter/**`
- Create: the tests and plan inside the server tree as above

- [ ] Step 1: Run the regression suite targeted at the new tests.
  ```bash
  py -3.12 -m pytest server/tests/pdf_team_splitter -v
  ```

- [ ] Step 2: Stage and commit the package and tests.
  ```bash
  git add server/pdf_team_splitter server/tests/pdf_team_splitter
  git commit -m "feat: port pdf team splitter core modules"
  ```

## Self-Review

- Spec coverage: Every requirement from the task (copy modules, fix imports, copy tests, run pytest) is captured by a step above.
- Placeholder scan: No TBD/TODO text remains; every step shows the exact command or code snippet.
- Type consistency: All references to the pdftool modules now use the `server.pdf_team_splitter` namespace.

Plan complete and saved as `server/pdf_team_splitter/2026-04-07-pdf-team-splitter-porting-plan.md` because the user limited edits to the `server` tree. Inline execution will follow using the executing-plans skill.
