"""CSV export helpers."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path

from database import Task

# Excel with a Russian locale expects a semicolon delimiter and a UTF-8 BOM.
CSV_DELIMITER = ";"
CSV_ENCODING = "utf-8-sig"
CSV_FIELDS = ("id", "text", "user", "created_at")


def write_tasks_csv(tasks: Iterable[Task], destination: str | Path) -> Path:
    """Write tasks to an Excel/LibreOffice friendly CSV file.

    Args:
        tasks: Tasks to export, usually the result of TaskRepository.list_tasks.
        destination: Target file path. Parent directories are created.

    Returns:
        The path of the written CSV file.
    """
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding=CSV_ENCODING, newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=CSV_FIELDS,
            delimiter=CSV_DELIMITER,
        )
        writer.writeheader()
        for task in tasks:
            writer.writerow(
                {
                    "id": task.id,
                    "text": task.text,
                    "user": task.user,
                    "created_at": task.created_at,
                }
            )
    return path
