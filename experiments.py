"""Run the Part 2 experiments without a live Telegram connection."""

from __future__ import annotations

import csv
from pathlib import Path

from database import TaskRepository
from export import CSV_DELIMITER, CSV_ENCODING, write_tasks_csv

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "experiments.db"
EXPORT_DIR = BASE_DIR / "exports"
DEMO_TASKS = (
    ("Купить молоко", "demo-user"),
    ("Позвонить маме", "demo-user"),
    ("Сдать отчёт", "demo-user"),
)


def reset_database(path: Path) -> TaskRepository:
    """Recreate the experiment database and return a ready repository."""
    path.unlink(missing_ok=True)
    repository = TaskRepository(path)
    repository.init_schema()
    return repository


def add_demo_tasks(repository: TaskRepository) -> None:
    """Insert several different tasks for the experiments."""
    for text, user in DEMO_TASKS:
        repository.add_task(text=text, user=user)


def check_persistence(db_path: Path) -> list[str]:
    """Reopen the database and verify that tasks and their order survived."""
    tasks = TaskRepository(db_path).list_tasks()
    actual = [task.text for task in tasks]
    expected = [text for text, _ in DEMO_TASKS]
    if actual != expected:
        raise AssertionError(f"Expected {expected!r}, got {actual!r}")
    return actual


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a semicolon-separated CSV file saved with a UTF-8 BOM."""
    with path.open(encoding=CSV_ENCODING, newline="") as file:
        return list(csv.DictReader(file, delimiter=CSV_DELIMITER))


def add_status_and_category(source: Path, destination: Path) -> Path:
    """Rename status to «Статус» and add the «Категория» column."""
    rows = read_csv_rows(source)
    fieldnames = ["id", "text", "user", "created_at", "Статус", "Категория"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding=CSV_ENCODING, newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=CSV_DELIMITER)
        writer.writeheader()
        for row in rows:
            row["Статус"] = row.pop("status", "новая")
            row["Категория"] = "личное"
            writer.writerow(row)
    return destination


def main() -> None:
    """Execute all experiments and print their results."""
    repository = reset_database(DB_PATH)
    add_demo_tasks(repository)
    print(f"1. Добавлено задач: {len(DEMO_TASKS)}")

    saved = check_persistence(DB_PATH)
    print(f"2. После повторного подключения данные на месте: {saved}")

    csv_path = write_tasks_csv(repository.list_tasks(), EXPORT_DIR / "tasks.csv")
    rows = read_csv_rows(csv_path)
    print(f"3. CSV создан: {csv_path} (строк: {len(rows)})")

    extended_path = add_status_and_category(
        csv_path,
        EXPORT_DIR / "tasks_with_status.csv",
    )
    print(f"4. CSV с колонками «Статус» и «Категория»: {extended_path}")
    print("   Откройте exports/tasks.csv в Excel или LibreOffice для проверки.")


if __name__ == "__main__":
    main()
