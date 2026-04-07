from pathlib import Path

import pandas as pd
import pytest

from server.pdf_team_splitter.team_roster import load_roster, normalize_name


def _write_roster_csv(tmp_path: Path, content: str) -> Path:
    roster_path = tmp_path / "roster.csv"
    roster_path.write_text(content, encoding="utf-8-sig")
    return roster_path


def test_normalize_name_uppercases_and_removes_formatting_noise():
    assert normalize_name(" zhu / xiuwu ") == "ZHU/XIUWU"


def test_load_roster_groups_duplicate_names_by_team(tmp_path: Path):
    roster_path = tmp_path / "roster.csv"
    roster_path.write_text(
        "姓名,团队\n"
        "ZHU/XIUWU,A团\n"
        " zhu / xiuwu ,A团\n"
        "LI/LEI,B团\n",
        encoding="utf-8-sig",
    )

    roster = load_roster(roster_path)

    assert [entry.name_normalized for entry in roster.entries] == [
        "ZHU/XIUWU",
        "ZHU/XIUWU",
        "LI/LEI",
    ]
    assert roster.groups_by_name["ZHU/XIUWU"].team_name == "A团"
    assert roster.groups_by_name["ZHU/XIUWU"].expected_count == 2
    assert roster.team_names == ["A团", "B团"]


def test_load_roster_rejects_cross_team_duplicate_name(tmp_path: Path):
    roster_path = tmp_path / "roster.csv"
    roster_path.write_text(
        "姓名,团队\n"
        "ZHU/XIUWU,A团\n"
        "ZHU/XIUWU,B团\n",
        encoding="utf-8-sig",
    )

    with pytest.raises(ValueError, match="appears in multiple teams"):
        load_roster(roster_path)


def test_load_roster_reads_excel_file(tmp_path: Path):
    roster_path = tmp_path / "roster.xlsx"
    pd.DataFrame(
        {
            "姓名": ["ZHU/XIUWU", "LI/LEI"],
            "团队": ["A团", "B团"],
        }
    ).to_excel(roster_path, index=False)

    roster = load_roster(roster_path)

    assert [entry.name_normalized for entry in roster.entries] == [
        "ZHU/XIUWU",
        "LI/LEI",
    ]
    assert roster.team_names == ["A团", "B团"]


def test_load_roster_rejects_missing_required_columns(tmp_path: Path):
    roster_path = _write_roster_csv(
        tmp_path,
        "姓名,部门\n"
        "ZHU/XIUWU,A团\n",
    )

    with pytest.raises(ValueError, match="Missing required roster columns"):
        load_roster(roster_path)


def test_load_roster_rejects_empty_team_name(tmp_path: Path):
    roster_path = _write_roster_csv(
        tmp_path,
        "姓名,团队\n"
        "ZHU/XIUWU,\n",
    )

    with pytest.raises(ValueError, match="empty team name"):
        load_roster(roster_path)


def test_load_roster_rejects_empty_passenger_name(tmp_path: Path):
    roster_path = _write_roster_csv(
        tmp_path,
        "姓名,团队\n"
        ",A团\n",
    )

    with pytest.raises(ValueError, match="empty passenger name"):
        load_roster(roster_path)
