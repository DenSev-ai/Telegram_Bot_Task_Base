from __future__ import annotations

from pathlib import Path

from database import Task
from experiments import add_status_and_category, read_csv_rows
from export import write_tasks_csv


def test_exported_csv_can_be_extended_with_status_and_category(
    tmp_path: Path,
) -> None:
    tasks = [
        Task(id=1, text="Купить молоко", user="42", created_at="2026-11-22 10:00:00")
    ]
    source = write_tasks_csv(tasks, tmp_path / "tasks.csv")

    destination = add_status_and_category(source, tmp_path / "tasks_with_status.csv")
    rows = read_csv_rows(destination)

    assert rows[0]["Статус"] == "новая"
    assert rows[0]["Категория"] == "личное"
    assert rows[0]["text"] == "Купить молоко"
