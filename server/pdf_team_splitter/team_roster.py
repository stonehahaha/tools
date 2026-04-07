from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

DEFAULT_NAME_COLUMN = "姓名"
DEFAULT_TEAM_COLUMN = "团队"


@dataclass(frozen=True)
class RosterEntry:
    row_index: int
    team_name: str
    name_raw: str
    name_normalized: str


@dataclass(frozen=True)
class RosterGroup:
    team_name: str
    name_normalized: str
    roster_names_raw: tuple[str, ...]
    expected_count: int
    roster_row_indices: tuple[int, ...] = ()
    first_row_index: int | None = None

    def __post_init__(self) -> None:
        if self.roster_row_indices:
            if self.first_row_index is None:
                object.__setattr__(self, "first_row_index", self.roster_row_indices[0])
            elif self.first_row_index != self.roster_row_indices[0]:
                raise ValueError("first_row_index must match the first roster row index")
            return

        if self.first_row_index is None:
            raise ValueError("RosterGroup requires at least one roster row index")

        object.__setattr__(self, "roster_row_indices", (self.first_row_index,))


@dataclass(frozen=True)
class RosterData:
    entries: list[RosterEntry]
    groups_by_name: dict[str, RosterGroup]
    team_names: list[str]


def normalize_name(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""

    text = str(value).strip().upper()
    text = " ".join(text.split())
    text = text.replace(" /", "/").replace("/ ", "/")
    return text.replace(" ", "")


def _read_roster_frame(path: Path, sheet: str | int | None) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path, encoding="utf-8-sig")
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path, sheet_name=sheet if sheet is not None else 0)
    raise ValueError(f"Unsupported roster format: {suffix}")


def load_roster(
    path: str | Path,
    *,
    sheet: str | int | None = None,
    name_column: str = DEFAULT_NAME_COLUMN,
    team_column: str = DEFAULT_TEAM_COLUMN,
) -> RosterData:
    roster_path = Path(path)
    frame = _read_roster_frame(roster_path, sheet)

    missing_columns = [
        column for column in (name_column, team_column) if column not in frame.columns
    ]
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(f"Missing required roster columns: {missing_text}")

    entries: list[RosterEntry] = []
    grouped_rows: OrderedDict[str, list[RosterEntry]] = OrderedDict()
    team_order: OrderedDict[str, None] = OrderedDict()

    for row_index, row in frame.iterrows():
        team_name = "" if pd.isna(row[team_column]) else str(row[team_column]).strip()
        name_raw = "" if pd.isna(row[name_column]) else str(row[name_column]).strip()
        name_normalized = normalize_name(row[name_column])

        if not team_name:
            raise ValueError(f"Roster row {row_index + 2} has an empty team name")
        if not name_normalized:
            raise ValueError(f"Roster row {row_index + 2} has an empty passenger name")

        team_order.setdefault(team_name, None)

        entry = RosterEntry(
            row_index=row_index,
            team_name=team_name,
            name_raw=name_raw,
            name_normalized=name_normalized,
        )
        entries.append(entry)
        grouped_rows.setdefault(name_normalized, []).append(entry)

    groups_by_name: dict[str, RosterGroup] = {}
    for name_normalized, grouped_entries in grouped_rows.items():
        team_names = {entry.team_name for entry in grouped_entries}
        if len(team_names) > 1:
            raise ValueError(
                f"Roster name {name_normalized!r} appears in multiple teams: {sorted(team_names)}"
            )

        first_entry = grouped_entries[0]
        groups_by_name[name_normalized] = RosterGroup(
            team_name=first_entry.team_name,
            name_normalized=name_normalized,
            roster_names_raw=tuple(entry.name_raw for entry in grouped_entries),
            expected_count=len(grouped_entries),
            roster_row_indices=tuple(entry.row_index for entry in grouped_entries),
        )

    return RosterData(
        entries=entries,
        groups_by_name=groups_by_name,
        team_names=list(team_order.keys()),
    )
