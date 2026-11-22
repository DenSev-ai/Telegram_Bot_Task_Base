from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from database import TaskRepository


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
