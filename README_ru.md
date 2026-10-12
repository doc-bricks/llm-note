<img src="assets/banner.png" width="100%" alt="llm-note banner">

# llm-note

[![CI](https://github.com/doc-bricks/llm-note/actions/workflows/ci.yml/badge.svg)](https://github.com/doc-bricks/llm-note/actions/workflows/ci.yml)
[![Version: 1.0.5](https://img.shields.io/badge/version-1.0.5-blue.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10-3.13](https://img.shields.io/badge/Python-3.10%20--%203.13-blue.svg)](pyproject.toml)
[![Platform: Windows | Linux | macOS](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](pyproject.toml)
[![Dependencies: 0 Stdlib Only](https://img.shields.io/badge/Dependencies-0%20(Stdlib)-brightgreen.svg)](THIRD_PARTY_LICENSES.md)
[![Code Style: Ruff](https://img.shields.io/badge/Code%20Style-Ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Ecosystem: doc-bricks](https://img.shields.io/badge/Ecosystem-doc--bricks-0055ff.svg)](https://github.com/doc-bricks)
[![Umbrella: open-bricks](https://img.shields.io/badge/Umbrella-open--bricks-blueviolet.svg)](https://github.com/open-bricks)
[![LLM Ready: llms.txt](https://img.shields.io/badge/LLM%20Ready-llms.txt-teal.svg)](llms.txt)

[English](README.md) · [Deutsch](README_de.md) · [Español](README_es.md) · [简体中文](README_zh-Hans.md) · [日本語](README_ja.md) · [Русский](README_ru.md)

*Перевод выполнен с помощью машинного перевода; приоритетной является английская версия README.*

> [!NOTE]
> **Локальное хранение заметок:** `llm-note` хранит заметки в локальной SQLite и текстовых файлах. Основному хранилищу заметок не нужны размещённый сервис заметок или ключ API. Дополнительный веб-интерфейс привязывается к loopback; сетевой доступ определяется настройками хоста.

---

## Быстрая навигация

1. [Обзор и зачем это нужно](#1-overview--why-this-exists)
2. [Ключевые возможности и архитектура](#2-key-capabilities--architecture)
3. [Наглядная архитектура системы](#3-visual-system-architecture)
4. [Последовательность жизненного цикла заметок и переноса](#4-note--transfer-lifecycle-sequence)
5. [Целевые персоны и поиск проекта](#5-target-personas--discoverability)
6. [Сравнительная матрица с альтернативами](#6-comparative-matrix-vs-alternatives)
7. [Управление и заметки о реализации](#7-governance--runtime-invariants)
8. [Руководство по локальному веб-интерфейсу Denkarium](#8-denkarium-local-web-gui-guide)
9. [Полный справочник по CLI и примеры](#9-cli-complete-reference--examples)
10. [Руководство по Python API и примеры кода](#10-python-api-guide--code-examples)
11. [Навык агента и интеграция в рабочие процессы](#11-agent-skill--workflow-integration)
12. [Файловые входящие и семантика переноса](#12-file-based-inboxes--transfer-semantics)
13. [Матрица родственной экосистемы](#13-sibling-ecosystem-matrix)
14. [Сторонние зависимости и границы лицензионных сведений](#14-third-party-licenses--transparency)
15. [Политика безопасности и цели реагирования](#15-security-policy--slas)
16. [Проверка и набор контрактных тестов](#16-verification--contract-test-suite)
17. [Правовое пояснение: § 521 BGB](#17-german-statutory-notice--521-bgb)
18. [Дорожная карта и журнал изменений](#18-roadmap--changelog)

---

<a id="1-overview--why-this-exists"></a>
<a id="overview--why-this-exists"></a>
<a id="1-ueberblick--warum-dieses-projekt-existiert"></a>
<a id="ueberblick--warum-dieses-projekt-existiert"></a>
## 1. Обзор и зачем это нужно

**llm-note** - это сверхлёгкий локальный движок блокнота, не требующий никаких сервисов. В первую очередь это блокнот для людей, в который ИИ-ассистенты и кодирующие агенты пишут для своего пользователя, а в зависимости от способа использования - блокнот, общий для обоих.

ИИ-ассистентам и LLM-агентам часто нужно место, где можно записывать решения, фиксировать наблюдения о контексте и обдумывать идеи, чтобы пользователь мог прочитать их позже, а при совместном использовании - чтобы и человек, и агент могли к ним возвращаться. Традиционные решения требуют тяжёлых векторных баз данных, платных облачных SaaS-подписок или раздутых Electron-приложений, которые потребляют системные ресурсы и отправляют телеметрию.

### Режимы

`llm-note` не навязывает режим - это один и тот же простой блокнот, который используется так, как подходит в данный момент:

- **Для людей, от LLM** (по умолчанию): человек читает, а его ИИ-ассистент пишет для него заметки.
- **От людей, для LLM**: человек оставляет заметки, которые прочитает его ассистент.
- **Общее рабочее пространство**: человек и ИИ-ассистенты пишут в один и тот же блокнот - ваши LLM делят с вами пространство.

`llm-note` предлагает идеальный архитектурный компромисс:
- **Ноль внешних зависимостей времени выполнения**: построен целиком на стандартной библиотеке Python (`sqlite3`, `http.server`, `urllib`, `argparse`, `json`, `pathlib`).
- **Гибкость двух хранилищ**: сочетает структурированные записи мыслей в SQLite (файл CLI по умолчанию — `llm-note.db`, путь настраивается) с редактируемыми человеком текстовыми входящими (`notebooks/*.txt`).
- **Происхождение из BACH**: чисто отделён от [кодовой базы настольного ассистента BACH](https://github.com/ellmos-ai/bach) (в частности, Notizblock и Denkarium) и выпущен под свободной лицензией MIT.

---

<a id="2-key-capabilities--architecture"></a>
<a id="key-capabilities--architecture"></a>
<a id="2-kernfaehigkeiten--architektur"></a>
<a id="kernfaehigkeiten--architektur"></a>
## 2. Ключевые возможности и архитектура

- **Журнал мыслей в SQLite (`NoteStore`)**: хранит структурированные заметки, записи журнала, категории, значения настроения и маркеры повышения до задачи с полной надёжностью ACID.
- **Текстовые входящие блокнотов (`FileNotebookStore`)**: управляет переносимыми текстовыми заметками с маркерами категорий `#NB:` и атомарной межпроцессной блокировкой файлов.
- **Встроенный веб-интерфейс Denkarium**: не требующий установки браузерный интерфейс, привязанный строго к `127.0.0.1` (loopback), на основе стандартного `http.server` и системных шрифтов.
- **Многоязычная локализация**: встроенная локализация сообщений на 6 языках: английском, немецком, испанском, китайском (упрощённом), японском и русском.
- **Навык агента в репозитории исходников**: репозиторий содержит `skills/llm-note/SKILL.md`; `pyproject.toml` упаковывает только `llm_note`, поэтому этот исходный путь не включён в wheel.
- **Детерминированный поиск**: поиск буквальной подстроки без сюрпризов с подстановочными символами и со строгими ограничениями запроса (от `0` до `1000`).

---

<a id="3-visual-system-architecture"></a>
<a id="visual-system-architecture"></a>
<a id="3-visuelle-systemarchitektur"></a>
<a id="visuelle-systemarchitektur"></a>
## 3. Наглядная архитектура системы

```mermaid
graph TD
    subgraph Clients["Клиенты и интерфейсы"]
        CLI["llm-note CLI (argparse)"]
        GUI["Веб-интерфейс Denkarium (127.0.0.1)"]
        PyAPI["Python API (llm_note)"]
        Skill["Навык агента (SKILL.md)"]
    end

    subgraph CoreEngine["Ядро llm-note"]
        NoteStore["NoteStore (движок SQLite)"]
        FileStore["FileNotebookStore (текстовый движок)"]
        HTTP["http.server (только loopback)"]
        I18N["Локали (EN, DE, ES, ZH, JA, RU)"]
    end

    subgraph LocalStorage["Слой локального хранилища"]
        DB[("llm-note.db<br/>(журнал мыслей SQLite; CLI по умолчанию)")]
        Notebooks["notebooks/*.txt<br/>(текстовые входящие)"]
        LockFile[".llm-note.lock (атомарная координация)"]
    end

    CLI -->|"Прямая команда"| NoteStore
    CLI -->|"Файловые операции"| FileStore
    GUI -->|"HTTP-запросы"| HTTP
    HTTP -->|"Внутренние вызовы"| NoteStore
    PyAPI -->|"API внутри процесса"| NoteStore
    PyAPI -->|"API внутри процесса"| FileStore
    Skill -->|"Вызов инструмента"| CLI
    Skill -->|"Прямой импорт"| PyAPI

    NoteStore -->|"Запросы ACID"| DB
    NoteStore -->|"Локализованные строки"| I18N
    FileStore -->|"Атомарная запись файлов"| Notebooks
    FileStore -->|"Межпроцессная блокировка"| LockFile
```

---

<a id="4-note--transfer-lifecycle-sequence"></a>
<a id="note--transfer-lifecycle-sequence"></a>
<a id="4-sequenzdiagramm-notiz--und-transfer-lebenszyklus"></a>
<a id="sequenzdiagramm-notiz--und-transfer-lebenszyklus"></a>
## 4. Последовательность жизненного цикла заметок и переноса

```mermaid
sequenceDiagram
    autonumber
    actor UserOrAgent as "Агент / разработчик"
    participant CLI as "CLI / Python API"
    participant FileStore as "FileNotebookStore"
    participant NoteStore as "NoteStore (SQLite)"
    participant Denkarium as "Denkarium GUI (127.0.0.1)"

    UserOrAgent ->> NoteStore: write("Architecture decision", category="design")
    NoteStore ->> NoteStore: Вставка записи мысли с временной меткой и настроением
    NoteStore -->> UserOrAgent: Возврат Entry(id=1, category="design")

    UserOrAgent ->> FileStore: write("Inbox item - #NB: Project Ideas")
    FileStore ->> FileStore: Получение .llm-note.lock и дозапись в inbox.txt
    FileStore -->> UserOrAgent: Заметка сохранена во входящие в виде текста

    UserOrAgent ->> FileStore: transfer_marked_entries()
    FileStore ->> FileStore: Разбор целевого блокнота #NB: и назначение стабильного #LLM-NOTE-ID
    FileStore ->> FileStore: Атомарное перемещение записи в целевой блокнот и снятие блокировки
    FileStore -->> UserOrAgent: Перенос завершён (риск дубликатов отсутствует)

    UserOrAgent ->> Denkarium: Открытие loopback-интерфейса (http://127.0.0.1:8000/)
    Denkarium ->> NoteStore: GET /api/notes (запрос мыслей из SQLite)
    NoteStore -->> Denkarium: JSON-ответ с отфильтрованным потоком мыслей
    Denkarium -->> UserOrAgent: Интерактивное визуальное представление с системными шрифтами
```

---

<a id="5-target-personas--discoverability"></a>
<a id="target-personas--discoverability"></a>
<a id="5-zielgruppen--suchbegriffe"></a>
<a id="zielgruppen--suchbegriffe"></a>
## 5. Целевые персоны и поиск проекта

`llm-note` рассчитан на четыре конкретные персоны и сценария использования:

| ID персоны | Целевая персона | Основная потребность | Ключевая ценность |
| :--- | :--- | :--- | :--- |
| `[PERSONA-01]` | **Разработчики автономных агентов** | Лёгкая память мыслей между сбросами контекста LLM | Хранилище SQLite без зависимостей, которое мгновенно встраивается |
| `[PERSONA-02]` | **Разработчики, заботящиеся о конфиденциальности** | Локальные заметки SQLite и текстовые входящие без размещённого сервиса заметок | Локальное хранение; сетевой доступ контролируется политикой хоста |
| `[PERSONA-03]` | **Пользователи настольных ИИ-ассистентов** | Мгновенный визуальный браузер мыслей без Node/Electron | Встроенный loopback-интерфейс Denkarium (`127.0.0.1`) |
| `[PERSONA-04]` | **Исследователи открытой науки** | Журналы мыслей и экспериментов, отслеживаемые в Git и пригодные для аудита | Текстовые входящие и стандартные однофайловые базы данных SQLite |

### Поисковые запросы с высоким намерением

- **Английский**: `local-first LLM notes`, `SQLite note store for agents`, `agent notebook CLI`, `private AI notebook`, `zero-dependency agent memory python`, `Denkarium agent thought browser`.
- **Немецкий**: `lokaler KI Agenten Notizspeicher`, `autonomes Agenten Gedächtnis ohne Cloud`, `datenschutzkonformer Notizblock offline`, `Agenten Denkarium Browser UI`.

---

<a id="6-comparative-matrix-vs-alternatives"></a>
<a id="comparative-matrix-vs-alternatives"></a>
<a id="6-vergleichsmatrix-gegenueber-alternativen"></a>
<a id="vergleichsmatrix-gegenueber-alternativen"></a>
## 6. Сравнительная матрица с альтернативами

| Архитектурный аспект | `llm-note` | Obsidian | Joplin | Векторные базы данных | «Голый» SQLite CLI |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **1. Движок хранения** | **SQLite + TXT** | Файлы Markdown | SQLite / синхронизация | Векторные эмбеддинги | Один файл SQLite |
| **2. Зависимости времени выполнения** | **0 (только stdlib)** | Electron / Node | Electron / БД | Тяжёлые C++ / Py | 0 (бинарник на C) |
| **3. Сетевые требования** | **Локальное хранение; действует политика хоста** | Не оценивалось | Не оценивалось | Не оценивалось | Не оценивалось |
| **4. Python API для агентов** | **Нативный, первоклассный** | REST от сообщества | API от сообщества | Сложный клиент | Требуется чистый SQL |
| **5. Встроенный веб-интерфейс** | **Встроен (127.0.0.1)** | Настольное приложение | Настольное приложение | Отдельный SaaS | Нет |
| **6. Синхронизация текстовых входящих** | **Встроена (`#NB:`)** | Ручные папки | Ручной импорт | Не применимо | Ручные скрипты |
| **7. Многоязычный движок** | **6 встроенных локалей** | Пакет от сообщества | Пакет от сообщества | Ориентирован на английский | Только английский |
| **8. Права процесса** | **Наследуются от запускающего процесса** | Не оценивалось | Не оценивалось | Не оценивалось | Не оценивалось |
| **9. Исходный навык агента** | **В репозитории; не в wheel** | Сторонний | Сторонний | Собственный код | Нет |
| **10. Информация о реагировании на уязвимости** | **Цели сопровождающего в SECURITY.md** | Не оценивалось | Не оценивалось | Не оценивалось | Не оценивалось |

---

<a id="7-governance--runtime-invariants"></a>
<a id="governance--runtime-invariants"></a>
<a id="7-governance--laufzeit-invarianten"></a>
<a id="governance--laufzeit-invarianten"></a>
## 7. Управление и заметки о реализации

Ниже описаны текущие характеристики реализации, подтверждённые исходным кодом. Это не неизменные гарантии и не независимая сертификация безопасности:

- `INV-LOCAL-01`: **Локальное хранение прежде всего** — заметки хранятся в локальной SQLite и текстовых файлах; это не блокирует сетевой доступ на уровне хоста.
- `INV-LOCAL-02`: **Однофайловое хранилище SQLite** — структурированная база данных ACID; файл CLI по умолчанию — `llm-note.db`, путь настраивается.
- `INV-LOCAL-03`: **Текстовые входящие блокнотов** — читаемые человеком текстовые входящие (`notebooks/*.txt`) с категоризацией через `#NB:`.
- `INV-LOCAL-04`: **Только стандартная библиотека** — ноль сторонних зависимостей времени выполнения; работает в любой стандартной среде Python 3.10+.
- `INV-LOCAL-05`: **Атомарные переносы, устойчивые к сбоям** — межпроцессная блокировка через `.llm-note.lock` и маркеры идемпотентности `#LLM-NOTE-ID`.
- `INV-LOCAL-06`: **Веб-интерфейс, привязанный к loopback** — Denkarium слушает строго `127.0.0.1`; поддерживается `--no-browser`.
- `INV-LOCAL-07`: **Многоязычный I18N** — 6 встроенных каталогов локализации: EN, DE, ES, ZH, JA, RU.
- `INV-LOCAL-08`: **Права процесса** — приложение не запрашивает повышение привилегий и наследует права запускающего процесса.
- `INV-LOCAL-09`: **Исходный навык агента** — репозиторий содержит [`skills/llm-note/SKILL.md`](skills/llm-note/SKILL.md); `pyproject.toml` упаковывает только `llm_note`, поэтому исходный путь не заявлен как содержимое wheel.
- `INV-LOCAL-10`: **Цели сопровождающего по реагированию** — `SECURITY.md` содержит цели подтверждения получения и первичной оценки; это не SLA и не обещанный срок исправления.

---

<a id="8-denkarium-local-web-gui-guide"></a>
<a id="denkarium-local-web-gui-guide"></a>
<a id="8-lokale-denkarium-weboberflaeche"></a>
<a id="lokale-denkarium-weboberflaeche"></a>
## 8. Руководство по локальному веб-интерфейсу Denkarium

Интерфейс Denkarium — это мгновенная визуальная панель мыслей, не требующая установки. Выберите один из шести языков в меню «Язык». Выбор хранится отдельно для каждого браузера в его локальном хранилище. При запуске GUI с явным параметром `--locale` он задаёт начальный язык; без него используется сохранённый выбор браузера, а по умолчанию — английский.

```bash
# Запуск Denkarium с настройками по умолчанию (открывает http://127.0.0.1:8000/)
llm-note gui

# Указание своего порта, базы данных и немецкой локали
llm-note --db data/notes.db --locale de gui --port 8765

# Режим без интерфейса для фоновых серверов или автоматического тестирования
llm-note gui --port 8765 --no-browser
```

### Архитектурные особенности GUI
- **Никакой раздутости фреймворков**: чистые HTML/CSS/JavaScript без фреймворков, раздаваемые напрямую через стандартный `http.server` Python.
- **Адаптивная вёрстка**: рассчитана как на настольные, так и на мобильные окна просмотра, с нативными системными шрифтами (`Segoe UI`, `SF Pro`, `system-ui`).
- **REST JSON-эндпоинты**:
  - `GET /api/notes?search=<query>&category=<cat>&limit=<n>`
  - `POST /api/notes` (создаёт новую запись мысли)

---

<a id="9-cli-complete-reference--examples"></a>
<a id="cli-complete-reference--examples"></a>
<a id="9-cli-befehlsreferenz--beispiele"></a>
<a id="cli-befehlsreferenz--beispiele"></a>
## 9. Полный справочник по CLI и примеры

### Установка

`llm-note` пока не опубликован на PyPI. Установите его из репозитория (Python 3.10+, без сторонних зависимостей времени выполнения):

```bash
pip install git+https://github.com/doc-bricks/llm-note.git
# или из локального клона
git clone https://github.com/doc-bricks/llm-note.git && cd llm-note && pip install .
```

Это устанавливает команду `llm-note` и пакет Python `llm_note`.


```bash
# Написать заметку с категорией и настроением
llm-note write "Refactor caching layer" --cat dev --mood 4

# Прочитать недавние заметки (лимит по умолчанию - 10)
llm-note read --limit 5

# Буквальный поиск по заметкам (без расширения подстановочных символов SQL)
llm-note search "caching"

# Обдумать идеи для будущего повышения
llm-note brainstorm "Zero-copy serialization options"

# Просмотреть сводную статистику
llm-note stats

# Запуск с собственной базой данных и немецкой локалью
llm-note --db custom/notes.db --locale de read --limit 3
```

---

<a id="10-python-api-guide--code-examples"></a>
<a id="python-api-guide--code-examples"></a>
<a id="10-python-api--programmierbeispiele"></a>
<a id="python-api--programmierbeispiele"></a>
## 10. Руководство по Python API и примеры кода

```python
from llm_note import NoteStore, FileNotebookStore

# 1. Инициализация NoteStore на SQLite
notes = NoteStore("data/notes.db")

# 2. Запись структурированной записи мысли
entry = notes.write(
    content="Implement deterministic seed for test suite",
    category="testing",
    mood=4
)
print(f"Created entry #{entry.id} at {entry.created_at}")

# 3. Поиск заметок
matches = notes.search("deterministic")
for match in matches:
    print(f"Found: {match.content} [{match.category}]")

# 4. Повышение мысли до задачи
notes.promote(entry.id, target="task")

# 5. Работа с текстовыми блокнотами
notebooks = FileNotebookStore("notebooks")
notebooks.write("Draft release announcement\n#NB: Marketing")
transferred = notebooks.transfer_marked_entries()
print(f"Transferred {transferred} entries to topic notebooks.")
```

---

<a id="11-agent-skill--workflow-integration"></a>
<a id="agent-skill--workflow-integration"></a>
<a id="11-agenten-skill--workflow-integration"></a>
<a id="agenten-skill--workflow-integration"></a>
## 11. Навык агента и интеграция в рабочие процессы

Репозиторий исходников содержит определение навыка агента [`skills/llm-note/SKILL.md`](skills/llm-note/SKILL.md). Согласно [`pyproject.toml`](pyproject.toml), wheel включает только `llm_note`, поэтому этот исходный путь не заявляется как содержимое wheel. Агент может вызывать `llm-note`, чтобы сохранять наблюдения и черновики.

```markdown
# Agent Tool Invocation Example
To save an interim research observation:
`llm-note write "Identified 3 edge cases in token parsing" --cat research`
```

---

<a id="12-file-based-inboxes--transfer-semantics"></a>
<a id="file-based-inboxes--transfer-semantics"></a>
<a id="12-text-notizbuecher--transfer-semantik"></a>
<a id="text-notizbuecher--transfer-semantik"></a>
## 12. Файловые входящие и семантика переноса

- **Входящие по умолчанию**: записи без маркеров записываются в `notebooks/inbox.txt`.
- **Адресация по теме**: добавьте `#NB: <Topic Name>`, чтобы направить запись в `notebooks/<Topic Name>.txt`.
- **Атомарный перенос**: вызов `transfer_marked_entries()` извлекает все помеченные записи, назначает идемпотентный маркер `#LLM-NOTE-ID: <hash>`, дописывает их в целевой файл темы и атомарно перезаписывает исходный файл.
- **Безопасность при параллельной работе**: конкуренция между несколькими процессами предотвращается консультативным файлом `.llm-note.lock` в каталоге блокнотов.

---

<a id="13-sibling-ecosystem-matrix"></a>
<a id="sibling-ecosystem-matrix"></a>
<a id="13-oekosystem-matrix--verwandte-module"></a>
<a id="oekosystem-matrix--verwandte-module"></a>
## 13. Матрица родственной экосистемы

Ниже перечислены связанные репозитории из более широкой экосистемы; само упоминание не означает прямую интеграцию с llm-note:

| Проект | Фокус и роль в экосистеме | Ссылка |
| :--- | :--- | :--- |
| **doc-bricks/llm-note** | Local-first ядро мыслей и блокнотов для агентов | [doc-bricks/llm-note](https://github.com/doc-bricks/llm-note) |
| **doc-bricks/MediaBrain** | Личная библиотека видео и музыки со смарт-плейлистами и историей просмотра потокового видео | [doc-bricks/MediaBrain](https://github.com/doc-bricks/MediaBrain) |
| **doc-bricks/MailProcessor** | Приложение в системном трее Windows для запуска локальных инструментов Universal Mail | [doc-bricks/MailProcessor](https://github.com/doc-bricks/MailProcessor) |
| **file-bricks/ProSync** | Надёжная кроссплатформенная синхронизация каталогов | [file-bricks/ProSync](https://github.com/file-bricks/ProSync) |
| **file-bricks/CloudLockFixer** | Откладывает файловые операции в папках облачной синхронизации и проверяет копирование с последующим удалением с помощью SHA-256 | [file-bricks/CloudLockFixer](https://github.com/file-bricks/CloudLockFixer) |
| **open-bricks organization profile** | Профиль организации и общий каталог, а не отдельный репозиторий | [open-bricks на GitHub](https://github.com/open-bricks) |

---

<a id="14-third-party-licenses--transparency"></a>
<a id="third-party-licenses--transparency"></a>
<a id="14-drittanbieter-lizenzen--transparenz"></a>
<a id="drittanbieter-lizenzen--transparenz"></a>
## 14. Сторонние зависимости и границы лицензионных сведений

`pyproject.toml` не объявляет дополнительные пакеты Python как зависимости времени выполнения. Ядро использует стандартную библиотеку Python и SQLite из среды Python.

- Ограниченные сведения о прямо объявленных зависимостях: [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md) и [`THIRD_PARTY_LICENSES.txt`](THIRD_PARTY_LICENSES.txt). Это не полные SBOM.
- Эти заметки не подтверждают лицензионный статус всех транзитивных деревьев сборочных и разработческих зависимостей.
- Процесс не запрашивает административное повышение и наследует права запускающего процесса; это не сертификация платформы.
---

<a id="15-security-policy--slas"></a>
<a id="security-policy--slas"></a>
<a id="15-sicherheitsrichtlinie--slas"></a>
<a id="sicherheitsrichtlinie--slas"></a>
## 15. Политика безопасности и цели реагирования

Канал для сообщений и цели реагирования сопровождающего описаны в [`SECURITY.md`](SECURITY.md):

- **Граница реализации:** ядро заметок использует локальное хранилище, а дополнительный веб-интерфейс привязывается к loopback. Приложение не блокирует сетевой доступ хоста и не предоставляет песочницу.
- **Цели сопровождающего:** подтверждение получения в течение 48 часов и начало первичной оценки в течение 5 рабочих дней — это цели, а не SLA или обещанный срок исправления.
- **Контакт:** конфиденциальные сообщения о безопасности отправляйте способом, описанным в [SECURITY.md](SECURITY.md).
---

<a id="16-verification--contract-test-suite"></a>
<a id="verification--contract-test-suite"></a>
<a id="16-verifikation--test-suite"></a>
<a id="verifikation--test-suite"></a>
## 16. Проверка и набор контрактных тестов

Запустите полный набор проверок локально:

```bash
# Запуск модульных и контрактных тестов
python -m pytest -ra -v

# Запуск быстрого линтера Ruff
ruff check .

# Проверка компиляции байт-кода
python -m compileall -q .
```

---

<a id="17-german-statutory-notice--521-bgb"></a>
<a id="german-statutory-notice--521-bgb"></a>
<a id="17-gesetzlicher-haftungshinweis--521-bgb"></a>
<a id="gesetzlicher-haftungshinweis--521-bgb"></a>
## 17. Правовое пояснение: § 521 BGB

Применимость § 521 BGB к конкретному предоставлению и его возможные последствия для ответственности зависят от обстоятельств. Это пояснение не определяет их.
---

<a id="18-roadmap--changelog"></a>
<a id="roadmap--changelog"></a>
<a id="18-roadmap--aenderungsprotokoll"></a>
<a id="roadmap--aenderungsprotokoll"></a>
## 18. Дорожная карта и журнал изменений

- **Журнал изменений**: подробная история версий — в [`CHANGELOG.md`](CHANGELOG.md).
- **Дорожная карта и задачи**: текущие вехи и открытые пункты бэклога — в [`TODO.md`](TODO.md).
- **Индекс контекста для ИИ**: полный индекс для обнаружения LLM доступен в [`llms.txt`](llms.txt).

---

## Лицензия

[MIT](LICENSE) - Copyright (c) 2026 Lukas Geiger.
