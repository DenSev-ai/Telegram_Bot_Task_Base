from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

import pytest

from database import DEFAULT_STATUS, TaskRepository


@pytest.fixture
def repository(tmp_path: Path) -> TaskRepository:
    """Create an initialized repository backed by a temporary database."""
    repo = TaskRepository(tmp_path / "tasks.db")
    repo.init_schema()
    return repo


def test_add_task_returns_incrementing_ids(repository: TaskRepository) -> None:
    first_id = repository.add_task("First", "user-1")
    second_id = repository.add_task("Second", "user-1")

    assert (first_id, second_id) == (1, 2)


def test_list_tasks_returns_tasks_in_insertion_order(
    repository: TaskRepository,
) -> None:
    for text in ("one", "two", "three"):
        repository.add_task(text, "user-1")

    assert [task.text for task in repository.list_tasks()] == ["one", "two", "three"]


def test_tasks_survive_new_repository_instance(tmp_path: Path) -> None:
    db_path = tmp_path / "tasks.db"
    first_repository = TaskRepository(db_path)
    first_repository.init_schema()
    first_repository.add_task("Persistent task", "user-1")

    second_repository = TaskRepository(db_path)
    tasks = second_repository.list_tasks()

    assert [task.text for task in tasks] == ["Persistent task"]


def test_init_schema_can_be_called_twice(repository: TaskRepository) -> None:
    repository.init_schema()
    repository.add_task("Still works", "user-1")

    assert len(repository.list_tasks()) == 1


def test_created_at_has_human_readable_format(repository: TaskRepository) -> None:
    repository.add_task("Task", "user-1")
    created_at = repository.list_tasks()[0].created_at

    datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")


def test_new_task_gets_default_status(repository: TaskRepository) -> None:
    repository.add_task("Task", "user-1")

    assert repository.list_tasks()[0].status == DEFAULT_STATUS


def test_set_status_updates_existing_task(repository: TaskRepository) -> None:
    task_id = repository.add_task("Task", "user-1")

    assert repository.set_status(task_id, "выполнена") is True
    assert repository.list_tasks()[0].status == "выполнена"


def test_set_status_returns_false_for_unknown_task(
    repository: TaskRepository,
) -> None:
    assert repository.set_status(999, "выполнена") is False


def test_init_schema_adds_status_column_to_legacy_database(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "legacy.db"
    with closing(sqlite3.connect(db_path)) as connection, connection:
        connection.execute(
            "CREATE TABLE tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "text TEXT NOT NULL, user TEXT NOT NULL, created_at TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO tasks (text, user, created_at) VALUES ('Old', 'u', 'now')"
        )

    repository = TaskRepository(db_path)
    repository.init_schema()

    assert repository.list_tasks()[0].status == DEFAULT_STATUS
