"""SQLite persistence layer for the task bot."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

DEFAULT_STATUS = "новая"
COLUMN_STATUS = "status"


@dataclass(frozen=True, slots=True)
class Task:
    """A single row from the tasks table."""

    id: int
    text: str
    user: str
    created_at: str
    status: str = DEFAULT_STATUS


class TaskRepository:
    """Store and read tasks in a SQLite database."""

    def __init__(self, db_path: str | Path) -> None:
        """Remember the database path and create its parent directory."""
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        """Open a connection that returns rows addressable by column name."""
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def init_schema(self) -> None:
        """Create the tasks table and add missing columns to older databases."""
        with closing(self._connect()) as connection, connection:
            connection.execute(
                f"""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    user TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    {COLUMN_STATUS} TEXT NOT NULL DEFAULT '{DEFAULT_STATUS}'
                )
                """
            )
            self._add_missing_status_column(connection)

    @staticmethod
    def _add_missing_status_column(connection: sqlite3.Connection) -> None:
        """Add the status column to a table created by an earlier version."""
        columns = {
            row["name"] for row in connection.execute("PRAGMA table_info(tasks)")
        }
        if COLUMN_STATUS not in columns:
            connection.execute(
                f"ALTER TABLE tasks ADD COLUMN {COLUMN_STATUS} "
                f"TEXT NOT NULL DEFAULT '{DEFAULT_STATUS}'"
            )

    def add_task(self, text: str, user: str, status: str = DEFAULT_STATUS) -> int:
        """Insert a task and return its generated identifier."""
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with closing(self._connect()) as connection, connection:
            cursor = connection.execute(
                "INSERT INTO tasks (text, user, created_at, status) "
                "VALUES (?, ?, ?, ?)",
                (text, user, created_at, status),
            )
            return int(cursor.lastrowid)

    def set_status(self, task_id: int, status: str) -> bool:
        """Update the status of one task.

        Returns:
            True if a task with this id exists and was updated.
        """
        with closing(self._connect()) as connection, connection:
            cursor = connection.execute(
                "UPDATE tasks SET status = ? WHERE id = ?",
                (status, task_id),
            )
            return cursor.rowcount > 0

    def list_tasks(self) -> list[Task]:
        """Return all tasks in insertion order (oldest first)."""
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT id, text, user, created_at, status FROM tasks ORDER BY id ASC"
            ).fetchall()
        return [Task(**dict(row)) for row in rows]
