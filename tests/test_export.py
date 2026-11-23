from __future__ import annotations

import csv
from pathlib import Path

from database import Task
from export import CSV_DELIMITER, CSV_ENCODING, write_tasks_csv

TASKS = [
    Task(id=1, text="Купить молоко", user="42", created_at="2026-11-22 10:00:00"),
    Task(
        id=2,
        text="Сдать отчёт; срочно",
        user="42",
        created_at="2026-11-22 10:05:00",
    ),
]


def read_rows(path: Path) -> list[dict[str, str]]:
    """Read the exported CSV the same way Excel/LibreOffice would."""
    with path.open(encoding=CSV_ENCODING, newline="") as file:
        return list(csv.DictReader(file, delimiter=CSV_DELIMITER))


def test_csv_has_bom_and_expected_header(tmp_path: Path) -> None:
    path = write_tasks_csv(TASKS, tmp_path / "tasks.csv")

    assert path.read_bytes().startswith(b"\xef\xbb\xbf")
    assert path.read_text(encoding=CSV_ENCODING).splitlines()[0] == (
        "id;text;user;created_at;status"
    )


def test_csv_preserves_order_and_special_characters(tmp_path: Path) -> None:
    path = write_tasks_csv(TASKS, tmp_path / "tasks.csv")

    rows = read_rows(path)

    assert [row["text"] for row in rows] == [task.text for task in TASKS]
    assert rows[1]["text"] == "Сдать отчёт; срочно"


def test_csv_without_tasks_contains_only_header(tmp_path: Path) -> None:
    path = write_tasks_csv([], tmp_path / "tasks.csv")

    assert read_rows(path) == []
    assert path.read_text(encoding=CSV_ENCODING).strip() == (
        "id;text;user;created_at;status"
    )


def test_csv_contains_status_column(tmp_path: Path) -> None:
    tasks = [Task(id=1, text="Task", user="42", created_at="2026-11-22 10:00:00")]
    path = write_tasks_csv(tasks, tmp_path / "tasks.csv")

    assert read_rows(path)[0]["status"] == "новая"
