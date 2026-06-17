"""SQLite and plain-text note stores."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import sqlite3


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

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

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
            conn.execute("CREATE INDEX IF NOT EXISTS idx_note_type ON note_entries(entry_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_note_category ON note_entries(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_note_created ON note_entries(created_at)")

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
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
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
            row = conn.execute("SELECT * FROM note_entries WHERE id = ?", (entry_id,)).fetchone()
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
        pattern = f"%{term}%"
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM note_entries
                WHERE content LIKE ? OR title LIKE ? OR category LIKE ? OR tags LIKE ?
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
        now = datetime.now().isoformat(timespec="seconds")
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

    def notebook_path(self, name: str | None = None) -> Path:
        raw_name = name or "Notizblock"
        parts = [self._sanitize(part) for part in re.split(r"[\\/]+", raw_name) if part.strip()]
        if not parts:
            parts = ["Notizblock"]
        filename = parts[-1]
        if not filename.endswith(".txt"):
            filename += ".txt"
        path = self.root.joinpath(*parts[:-1], filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def write(self, content: str, notebook: str | None = None) -> Path:
        path = self.notebook_path(notebook)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"---\n[{timestamp}]\n{content.rstrip()}\n\n")
        return path

    def read(self, notebook: str | None = None) -> str:
        path = self.notebook_path(notebook)
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")

    def transfer_marked_entries(self, notebook: str | None = None) -> int:
        source_path = self.notebook_path(notebook)
        text = self.read(notebook)
        if not text.strip():
            return 0

        entries = re.split(r"(?m)^---\s*\n", text)
        kept: list[str] = []
        transferred = 0
        for raw in entries:
            block = raw.strip()
            if not block:
                continue
            marker = re.search(r"(?m)^#NB:\s*(.+?)\s*$", block)
            if not marker:
                kept.append(block)
                continue
            target = marker.group(1)
            cleaned = re.sub(r"(?m)^#NB:\s*.+?\s*$", "", block).strip()
            with self.notebook_path(target).open("a", encoding="utf-8") as handle:
                handle.write(f"---\n{cleaned}\n\n")
            transferred += 1

        new_text = "".join(f"---\n{block}\n\n" for block in kept)
        source_path.write_text(new_text, encoding="utf-8")
        return transferred

    @staticmethod
    def _sanitize(name: str) -> str:
        safe = name.strip().replace(" ", "_")
        safe = re.sub(r"[^A-Za-z0-9_.\-äöüÄÖÜß]+", "_", safe)
        return safe.strip("._") or "Notebook"
