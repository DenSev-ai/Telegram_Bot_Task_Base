"""SQLite persistence layer for the task bot."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Task:
    """A single row from the tasks table."""

    id: int
    text: str
    user: str
    created_at: str


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
        """Create the tasks table if it does not exist yet."""
        with closing(self._connect()) as connection, connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    user TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def add_task(self, text: str, user: str) -> int:
        """Insert a task and return its generated identifier."""
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with closing(self._connect()) as connection, connection:
            cursor = connection.execute(
                "INSERT INTO tasks (text, user, created_at) VALUES (?, ?, ?)",
                (text, user, created_at),
            )
            return int(cursor.lastrowid)

    def list_tasks(self) -> list[Task]:
        """Return all tasks in insertion order (oldest first)."""
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT id, text, user, created_at FROM tasks ORDER BY id ASC"
            ).fetchall()
        return [Task(**dict(row)) for row in rows]
