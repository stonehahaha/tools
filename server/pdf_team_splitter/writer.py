from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from .matcher import PageMatch

INVALID_FILENAME_CHARACTERS = set('?*|<>"\\:/')

def order_matches_for_team(matches: list[PageMatch]) -> list[PageMatch]:
    return sorted(matches, key=lambda match: (match.excel_order, match.pdf_page_number))


def _output_path_for_team(output_dir: Path, team_name: str) -> Path:
    if not team_name or team_name in {".", ".."}:
        raise ValueError(f"Unsafe team name: {team_name!r}")
    if any(character in INVALID_FILENAME_CHARACTERS for character in team_name):
        raise ValueError(f"Unsafe team name: {team_name!r}")
    if any(ord(character) < 32 for character in team_name):
        raise ValueError(f"Unsafe team name: {team_name!r}")

    output_path = output_dir / f"{team_name}_\u884c\u7a0b\u5355.pdf"
    resolved_output_dir = output_dir.resolve()
    resolved_output_path = output_path.resolve()
    if resolved_output_dir not in resolved_output_path.parents:
        raise ValueError(f"Unsafe team name: {team_name!r}")
    return output_path


def write_team_pdfs(
    pdf_path: str | Path,
    matches: list[PageMatch],
    outdir: str | Path,
) -> list[Path]:
    output_dir = Path(outdir)

    reader = PdfReader(str(pdf_path))
    grouped_matches: dict[str, list[PageMatch]] = defaultdict(list)
    for match in matches:
        grouped_matches[match.team_name].append(match)

    output_paths_by_team = {
        team_name: _output_path_for_team(output_dir, team_name)
        for team_name in sorted(grouped_matches.keys())
    }

    output_dir.mkdir(parents=True, exist_ok=True)

    written_paths: list[Path] = []
    for team_name in sorted(grouped_matches.keys()):
        output_path = output_paths_by_team[team_name]
        writer = PdfWriter()
        ordered_matches = order_matches_for_team(grouped_matches[team_name])
        for match in ordered_matches:
            writer.add_page(reader.pages[match.pdf_page_number - 1])

        with output_path.open("wb") as stream:
            writer.write(stream)
        written_paths.append(output_path)

    return written_paths
