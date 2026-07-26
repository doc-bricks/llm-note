"""SQLite and plain-text note stores."""

from __future__ import annotations

import os
import re
import sqlite3
import tempfile
import time
import unicodedata
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import uuid4

MAX_QUERY_LIMIT = 1000
_WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "CLOCK$",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}
_TRANSFER_ID_RE = re.compile(
    r"(?m)^#LLM-NOTE-ID:[^\S\r\n]*([0-9a-fA-F-]{36})[^\S\r\n]*(?=\r?$)"
)


def _validate_limit(limit: int) -> int:
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise TypeError("limit must be an integer")
    if not 0 <= limit <= MAX_QUERY_LIMIT:
        raise ValueError(f"limit must be between 0 and {MAX_QUERY_LIMIT}")
    return limit


@contextmanager
def _exclusive_file_lock(path: Path, *, timeout: float = 10.0) -> Iterator[None]:
    """Hold a cross-process exclusive lock backed by a stable lock file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+b")
    handle.seek(0, os.SEEK_END)
    if handle.tell() == 0:
        handle.write(b"\0")
        handle.flush()
    handle.seek(0)

    deadline = time.monotonic() + timeout
    locked = False
    try:
        while not locked:
            try:
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
            except OSError as exc:
                if time.monotonic() >= deadline:
                    raise TimeoutError(
                        f"Timed out waiting for notebook lock: {path}"
                    ) from exc
                time.sleep(0.05)
        yield
    finally:
        if locked:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def _atomic_write_text(path: Path, content: str) -> None:
    """Durably replace a UTF-8 text file without exposing a truncated state."""

    descriptor, temp_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)


@dataclass(frozen=True)
class Entry:
    id: int
    entry_type: str
    content: str
    category: str
    title: str | None = None
    mood: int | None = None
    promoted_to: str | None = None
    created_at: str | None = None


class NoteStore:
    """Small SQLite-backed note store extracted from BACH Denkarium ideas."""

    def __init__(self, db_path: str | Path = "llm-note.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout = 30000")
        try:
            yield conn
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS note_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_type TEXT NOT NULL DEFAULT 'note',
                    title TEXT,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'note',
                    tags TEXT,
                    source TEXT DEFAULT 'user',
                    mood INTEGER,
                    promoted_to TEXT,
                    promoted_id INTEGER,
                    created_at TEXT DEFAULT (datetime('now', 'localtime')),
                    updated_at TEXT
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_note_type ON note_entries(entry_type)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_note_category ON note_entries(category)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_note_created ON note_entries(created_at)"
            )

    def write(
        self,
        content: str,
        *,
        entry_type: str = "note",
        category: str = "note",
        title: str | None = None,
        mood: int | None = None,
        source: str = "user",
    ) -> Entry:
        now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
        if entry_type == "logbook" and not title:
            title = f"Log {now}"

        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO note_entries
                    (entry_type, title, content, category, source, mood, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (entry_type, title, content, category, source, mood, now),
            )
            entry_id = int(cur.lastrowid)
        return self.get(entry_id)

    def get(self, entry_id: int) -> Entry:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM note_entries WHERE id = ?", (entry_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"Entry not found: {entry_id}")
        return self._row_to_entry(row)

    def list_entries(
        self,
        *,
        entry_type: str | None = None,
        category: str | None = None,
        limit: int = 10,
    ) -> list[Entry]:
        limit = _validate_limit(limit)
        query = "SELECT * FROM note_entries"
        where: list[str] = []
        params: list[object] = []
        if entry_type:
            where.append("entry_type = ?")
            params.append(entry_type)
        if category:
            where.append("category = ?")
            params.append(category)
        if where:
            query += " WHERE " + " AND ".join(where)
        query += " ORDER BY created_at DESC, id DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_entry(row) for row in rows]

    def search(self, term: str, *, limit: int = 20) -> list[Entry]:
        limit = _validate_limit(limit)
        escaped_term = (
            term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        )
        pattern = f"%{escaped_term}%"
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM note_entries
                WHERE content LIKE ? ESCAPE '\\'
                   OR title LIKE ? ESCAPE '\\'
                   OR category LIKE ? ESCAPE '\\'
                   OR tags LIKE ? ESCAPE '\\'
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (pattern, pattern, pattern, pattern, limit),
            ).fetchall()
        return [self._row_to_entry(row) for row in rows]

    def brainstorm(self, topic: str) -> Entry:
        return self.write(
            f"Topic: {topic}\n\nIdeas:\n- ",
            entry_type="note",
            category="brainstorm",
            title=f"Brainstorm: {topic}",
        )

    def promote(self, entry_id: int, target: str) -> Entry:
        if target not in {"task", "wiki", "issue"}:
            raise ValueError("target must be task, wiki, or issue")
        now = datetime.now().astimezone().isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute(
                "UPDATE note_entries SET promoted_to = ?, updated_at = ? WHERE id = ?",
                (target, now, entry_id),
            )
        return self.get(entry_id)

    def stats(self) -> dict[str, int]:
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) FROM note_entries").fetchone()[0]
            promoted = conn.execute(
                "SELECT COUNT(*) FROM note_entries WHERE promoted_to IS NOT NULL"
            ).fetchone()[0]
            logbook = conn.execute(
                "SELECT COUNT(*) FROM note_entries WHERE entry_type = 'logbook'"
            ).fetchone()[0]
        return {"total": int(total), "promoted": int(promoted), "logbook": int(logbook)}

    @staticmethod
    def _row_to_entry(row: sqlite3.Row) -> Entry:
        return Entry(
            id=int(row["id"]),
            entry_type=str(row["entry_type"]),
            title=row["title"],
            content=str(row["content"]),
            category=str(row["category"]),
            mood=row["mood"],
            promoted_to=row["promoted_to"],
            created_at=row["created_at"],
        )


class FileNotebookStore:
    """Plain-text notebook inbox compatible with the BACH Notizblock pattern."""

    def __init__(self, root: str | Path = "notebooks") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._resolved_root = self.root.resolve()
        self._lock_path = self._resolved_root / ".llm-note.lock"

    def notebook_path(self, name: str | None = None) -> Path:
        raw_name = name or "Notizblock"
        parts = [
            self._sanitize(part)
            for part in re.split(r"[\\/]+", raw_name)
            if part.strip()
        ]
        if not parts:
            parts = ["Notizblock"]
        filename = parts[-1]
        if not filename.lower().endswith(".txt"):
            filename += ".txt"
        path = self.root.joinpath(*parts[:-1], filename)
        resolved_path = path.resolve(strict=False)
        try:
            resolved_path.relative_to(self._resolved_root)
        except ValueError as exc:
            raise ValueError("Notebook path escapes the configured root") from exc
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def write(self, content: str, notebook: str | None = None) -> Path:
        path = self.notebook_path(notebook)
        timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
        with (
            _exclusive_file_lock(self._lock_path),
            path.open("a", encoding="utf-8", newline="") as handle,
        ):
            handle.write(f"---\n[{timestamp}]\n{content.rstrip()}\n\n")
        return path

    def read(self, notebook: str | None = None) -> str:
        path = self.notebook_path(notebook)
        with _exclusive_file_lock(self._lock_path):
            return self._read_path(path)

    def transfer_marked_entries(self, notebook: str | None = None) -> int:
        source_path = self.notebook_path(notebook)
        with _exclusive_file_lock(self._lock_path):
            text = self._read_path(source_path)
            if not text.strip():
                return 0

            entries = re.split(r"(?m)(?=^---[^\S\r\n]*\r?\n)", text)
            kept: list[str] = []
            prepared_entries: list[str] = []
            transfers: dict[Path, list[tuple[str, str]]] = {}
            seen_ids: set[str] = set()
            transferred = 0
            for block in entries:
                marker = re.search(
                    r"(?m)^#NB:[^\S\r\n]*(.+?)[^\S\r\n]*$",
                    block,
                )
                if not marker:
                    kept.append(block)
                    prepared_entries.append(block)
                    continue
                target_path = self.notebook_path(marker.group(1))
                if target_path.resolve() == source_path.resolve():
                    kept.append(block)
                    prepared_entries.append(block)
                    continue

                id_match = _TRANSFER_ID_RE.search(block)
                entry_id = id_match.group(1).lower() if id_match else ""
                if not entry_id or entry_id in seen_ids:
                    entry_id = str(uuid4())
                seen_ids.add(entry_id)

                if id_match:
                    prepared = (
                        block[: id_match.start(1)] + entry_id + block[id_match.end(1) :]
                    )
                else:
                    newline = "\r\n" if "\r\n" in block else "\n"
                    prepared = (
                        block[: marker.start()]
                        + f"#LLM-NOTE-ID: {entry_id}{newline}"
                        + block[marker.start() :]
                    )
                prepared_entries.append(prepared)

                cleaned = re.sub(
                    r"(?m)^#NB:[^\S\r\n]*.+?[^\S\r\n]*(?:\r?\n|$)",
                    "",
                    prepared,
                )
                if not cleaned.endswith(("\n", "\r")):
                    cleaned += "\n"
                transfers.setdefault(target_path, []).append((entry_id, cleaned))
                transferred += 1

            if transferred == 0:
                return 0

            prepared_source = "".join(prepared_entries)
            if prepared_source != text:
                _atomic_write_text(source_path, prepared_source)

            for target_path, target_entries in transfers.items():
                target_text = self._read_path(target_path)
                existing_ids = {
                    match.group(1).lower()
                    for match in _TRANSFER_ID_RE.finditer(target_text)
                }
                updated_target = target_text
                for entry_id, cleaned in target_entries:
                    if entry_id not in existing_ids:
                        updated_target += cleaned
                        existing_ids.add(entry_id)
                if updated_target != target_text:
                    _atomic_write_text(target_path, updated_target)

            _atomic_write_text(source_path, "".join(kept))
            return transferred

    @staticmethod
    def _read_path(path: Path) -> str:
        if not path.exists():
            return ""
        with path.open("r", encoding="utf-8", newline="") as handle:
            return handle.read()

    @staticmethod
    def _sanitize(name: str) -> str:
        normalized = unicodedata.normalize("NFC", name.strip())
        safe = "".join(
            char
            if char in "._-" or unicodedata.category(char)[0] in {"L", "M", "N"}
            else "_"
            for char in normalized
        )
        safe = re.sub(r"_+", "_", safe).strip("._") or "Notebook"
        if safe.split(".", 1)[0].upper() in _WINDOWS_RESERVED_NAMES:
            safe = f"_{safe}"
        return safe
