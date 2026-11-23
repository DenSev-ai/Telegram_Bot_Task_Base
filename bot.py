"""Telegram bot that stores tasks in SQLite."""

from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from collections.abc import Sequence
from pathlib import Path

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import FSInputFile, Message, User

from config import load_settings
from database import Task, TaskRepository
from export import write_tasks_csv

logger = logging.getLogger(__name__)
router = Router()

DONE_STATUS = "выполнена"

START_TEXT = (
    "Привет! Я сохраняю задачи в SQLite.\n\n"
    "/add <текст> — добавить задачу\n"
    "/list — показать задачи\n"
    "/done <id> — отметить задачу выполненной\n"
    "/export — скачать CSV\n"
    "/help — помощь"
)

MAX_MESSAGE_LENGTH = 4000


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Send a greeting with the list of available commands."""
    await message.answer(START_TEXT)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Explain how to use each bot command."""
    await message.answer(
        "Как пользоваться ботом:\n\n"
        "/add Купить молоко — добавить задачу\n"
        "/list — показать все задачи в порядке добавления\n"
        "/done 3 — отметить задачу #3 выполненной\n"
        "/export — получить CSV-файл для Excel/LibreOffice"
    )


@router.message(Command("add"))
async def cmd_add(
    message: Message,
    command: CommandObject,
    repo: TaskRepository,
) -> None:
    """Save the text after /add as a new task."""
    text = (command.args or "").strip()
    if not text:
        await message.answer("Использование: /add <текст задачи>")
        return
    user = user_display_name(message.from_user)
    task_id = repo.add_task(text=text, user=user)
    await message.answer(f"Задача #{task_id} добавлена.")


@router.message(Command("done"))
async def cmd_done(
    message: Message,
    command: CommandObject,
    repo: TaskRepository,
) -> None:
    """Mark the task with the given id as completed."""
    raw_id = (command.args or "").strip()
    if not raw_id.isdigit():
        await message.answer("Использование: /done <id задачи>")
        return
    if repo.set_status(int(raw_id), DONE_STATUS):
        await message.answer(f"Задача #{raw_id} отмечена как «{DONE_STATUS}».")
    else:
        await message.answer(f"Задача #{raw_id} не найдена.")


@router.message(Command("list"))
async def cmd_list(message: Message, repo: TaskRepository) -> None:
    """Show every task ordered by insertion time."""
    tasks = repo.list_tasks()
    if not tasks:
        await message.answer("Список задач пуст. Добавьте задачу через /add.")
        return
    for chunk in split_message(format_tasks(tasks)):
        await message.answer(chunk)


@router.message(Command("export"))
async def cmd_export(message: Message, repo: TaskRepository) -> None:
    """Generate a CSV file and send it to the user."""
    tasks = repo.list_tasks()
    if not tasks:
        await message.answer("Нет задач для экспорта. Добавьте задачу через /add.")
        return
    path = create_temp_csv(tasks)
    try:
        await message.answer_document(
            FSInputFile(path, filename="tasks.csv"),
            caption=f"Экспорт задач: {len(tasks)} шт.",
        )
    finally:
        path.unlink(missing_ok=True)


def user_display_name(user: User | None) -> str:
    """Return the human-readable author name stored in the tasks.user column.

    Falls back to the numeric Telegram id when no name is available.
    """
    if user is None:
        return "unknown"
    return user.full_name.strip() or str(user.id)


def format_tasks(tasks: Sequence[Task]) -> str:
    """Format tasks as numbered lines with status and creation timestamps."""
    return "\n".join(
        f"{task.id}. {task.text} — {task.created_at} [{task.status}]" for task in tasks
    )


def split_message(text: str, limit: int = MAX_MESSAGE_LENGTH) -> list[str]:
    """Split text into chunks that fit into one Telegram message."""
    chunks: list[str] = []
    current: list[str] = []
    current_length = 0
    for line in text.splitlines():
        if current and current_length + len(line) + 1 > limit:
            chunks.append("\n".join(current))
            current = []
            current_length = 0
        current.append(line)
        current_length += len(line) + 1
    if current:
        chunks.append("\n".join(current))
    return chunks


def create_temp_csv(tasks: Sequence[Task]) -> Path:
    """Write tasks to a temporary CSV file and return its path."""
    file_descriptor, raw_path = tempfile.mkstemp(prefix="tasks_", suffix=".csv")
    os.close(file_descriptor)
    return write_tasks_csv(tasks, Path(raw_path))


async def main() -> None:
    """Configure the dispatcher and start long polling."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    settings = load_settings()
    repository = TaskRepository(settings.db_path)
    repository.init_schema()

    bot = Bot(token=settings.bot_token)
    dispatcher = Dispatcher()
    dispatcher["repo"] = repository
    dispatcher.include_router(router)
    logger.info("Bot started, database: %s", settings.db_path)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
