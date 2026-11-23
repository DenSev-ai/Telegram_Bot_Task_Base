from __future__ import annotations

from types import SimpleNamespace

from bot import format_tasks, split_message, user_display_name


def test_user_display_name_prefers_full_name() -> None:
    user = SimpleNamespace(full_name="Denis D.", id=1777628643)

    assert user_display_name(user) == "Denis D."


def test_user_display_name_falls_back_to_id() -> None:
    user = SimpleNamespace(full_name="   ", id=1777628643)

    assert user_display_name(user) == "1777628643"


def test_user_display_name_without_user() -> None:
    assert user_display_name(None) == "unknown"


def test_format_tasks_lists_id_text_and_date() -> None:
    from database import Task

    tasks = [
        Task(
            id=1,
            text="Сделать ДЗ",
            user="Denis D.",
            created_at="2026-11-22 21:17",
        )
    ]

    assert format_tasks(tasks) == "1. Сделать ДЗ — 2026-11-22 21:17 [новая]"


def test_split_message_keeps_all_lines() -> None:
    text = "\n".join(f"{i}. task" for i in range(1, 101))

    joined = "\n".join(split_message(text, limit=200))

    assert joined == text
