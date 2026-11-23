# Telegram-бот для хранения задач

Минимальный бот на Python, [aiogram 3](https://docs.aiogram.dev/) и SQLite3.
Задачи сохраняются в локальную базу, показываются в порядке добавления и
выгружаются в CSV, который открывается в Excel и LibreOffice.

## Команды

| Команда | Назначение |
| --- | --- |
| `/start` | Приветствие и список команд |
| `/help` | Краткая инструкция |
| `/add <текст>` | Добавить задачу |
| `/list` | Показать все задачи по порядку добавления |
| `/done <id>` | Отметить задачу выполненной |
| `/export` | Скачать CSV-файл с задачами |

## Структура проекта

```text
bot.py              — запуск бота и обработчики команд
config.py           — чтение BOT_TOKEN и DB_PATH из .env
database.py         — слой SQLite: таблица tasks и операции с ней
export.py           — запись задач в CSV для Excel/LibreOffice
experiments.py      — автоматическая проверка сценариев из части 2
tests/              — pytest-тесты
.env.example        — шаблон настроек
```

Таблица `tasks` создаётся автоматически:

```sql
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    user TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'новая'
);
```

Колонка `status` хранит состояние задачи: `новая` при добавлении и
`выполнена` после команды `/done <id>`. Если база была создана более ранней
версией бота, `init_schema()` добавит колонку `status` автоматически
(`ALTER TABLE`), данные при этом сохранятся.
```

## Запуск

Нужен Python 3.10 или новее и токен от [@BotFather](https://t.me/BotFather).

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Откройте `.env` и вставьте токен:

```dotenv
BOT_TOKEN=123456789:ваш_токен
DB_PATH=data/tasks.db
```

Запустите бота:

```powershell
python bot.py
```

В Linux/macOS активация окружения: `source .venv/bin/activate`.

## Эксперименты (часть 2)

### Автоматически

```powershell
python experiments.py
```

Скрипт создаёт `data/experiments.db`, добавляет три задачи, заново открывает
базу (имитация перезапуска), проверяет порядок и создаёт:

- `exports/tasks.csv` — обычный экспорт;
- `exports/tasks_with_status.csv` — тот же файл с колонками «Статус» и
  «Категория».

### Вручную через бота

1. Отправьте боту несколько команд `/add` с разными задачами.
2. Остановите бота (`Ctrl+C`) и снова запустите `python bot.py`.
3. Выполните `/list` — задачи должны остаться на месте и идти в порядке
   добавления.
4. Выполните `/export` и откройте полученный `tasks.csv` в Excel или
   LibreOffice. Колонка `status` уже есть в файле.
5. Отметьте задачу выполненной через `/done <id>` — в `/list` и в новом
   экспорте её статус станет `выполнена`.
6. В Excel/LibreOffice добавьте колонку «Категория», заполните её и сохраните
   файл. CSV использует `;` как разделитель и кодировку UTF-8 с BOM, поэтому
   русский текст не превращается в «кракозябры».

## Тесты

```powershell
pip install -r requirements-dev.txt
pytest
```

Тесты проверяют:

- сохранение задач и их порядок;
- сохранение данных при повторном подключении к базе;
- формат `created_at`;
- BOM, разделитель и экранирование в CSV;
- колонку `status` в базе и в CSV;
- миграцию старой базы без колонки `status`;
- добавление колонок «Статус» и «Категория» в готовый CSV.

## Публикация на GitHub

Файл `.env` и папки `data/`, `exports/` исключены через `.gitignore`, поэтому
токен и локальная база не попадут в репозиторий.

```powershell
git init
git add .
git commit -m "Telegram tasks bot with SQLite and CSV export"
git branch -M main
git remote add origin https://github.com/ВАШ_ЛОГИН/ИМЯ_РЕПОЗИТОРИЯ.git
git push -u origin main
```

Если репозиторий ещё не создан, создайте пустой репозиторий на GitHub без
README и `.gitignore`, затем выполните команды выше.
