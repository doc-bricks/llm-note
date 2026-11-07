"""PB-11: one-off migration BACH denkarium_entries -> llm-note (synthetic data only)."""

import sqlite3
from pathlib import Path

import pytest

from llm_note import NoteStore
from llm_note.migrate_denkarium import MigrationError, migrate

SRC_SCHEMA = """
CREATE TABLE denkarium_entries (
    id INTEGER PRIMARY KEY, entry_type TEXT, title TEXT, content TEXT,
    category TEXT, source TEXT, mood INTEGER, promoted_to TEXT, promoted_id INTEGER,
    created_at TEXT, updated_at TEXT, is_archived INTEGER DEFAULT 0,
    archived_reason TEXT, archived_at TEXT
)
"""


def make_source(path: Path, rows: list[tuple]) -> Path:
    conn = sqlite3.connect(path)
    conn.execute(SRC_SCHEMA)
    conn.executemany(
        "INSERT INTO denkarium_entries VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows
    )
    conn.commit()
    conn.close()
    return path


ROWS = [
    (10, "denkarium", None, "first", "notiz", "user", 0, None, None, "2026-02-19 08:00", None, 0, None, None),
    (11, "logbuch", "Log", "second", "test", "user", 4, "task", 5, "2026-03-01 09:30", "2026-03-02 10:00", 0, None, None),
    (12, "denkarium", "T", "third", "brainstorm", "user", None, None, None, "2026-09-15 12:00", None, 1, "weg", "2026-09-16 08:00"),
]


def test_dry_run_is_default_and_writes_nothing(tmp_path: Path) -> None:
    src = make_source(tmp_path / "source.db", ROWS)
    target = tmp_path / "llm-note.db"

    report = migrate(src, target)

    assert report["dry_run"] is True
    assert report["source_count"] == 3
    assert not target.exists()


def test_apply_keeps_dates_types_mood_archive_and_mapping(tmp_path: Path) -> None:
    src = make_source(tmp_path / "source.db", ROWS)
    target = tmp_path / "llm-note.db"

    report = migrate(src, target, apply=True, snapshot_dir=tmp_path / "snap")

    store = NoteStore(target)
    entries = {e.legacy_id: e for e in store.list_entries(include_archived=True, limit=100)}
    assert set(entries) == {10, 11, 12}
    assert entries[10].created_at == "2026-02-19 08:00"
    assert entries[10].entry_type == "note" and entries[10].mood is None  # 0 -> NULL
    assert entries[11].entry_type == "logbook" and entries[11].mood == 4
    assert entries[11].promoted_to == "task" and entries[11].promoted_id == 5
    assert entries[12].is_archived and entries[12].archived_reason == "weg"
    assert report["mapping"] == {str(k): v.id for k, v in entries.items()}
    assert report["target_count"] == 3
    assert list((tmp_path / "snap").glob("denkarium_entries_*.db"))


def test_apply_is_idempotent(tmp_path: Path) -> None:
    src = make_source(tmp_path / "source.db", ROWS)
    target = tmp_path / "llm-note.db"
    migrate(src, target, apply=True, snapshot_dir=tmp_path / "snap")
    again = migrate(src, target, apply=True, snapshot_dir=tmp_path / "snap")
    assert again["imported"] == 0 and again["target_count"] == 3


def test_source_table_is_left_untouched(tmp_path: Path) -> None:
    src = make_source(tmp_path / "source.db", ROWS)
    migrate(src, tmp_path / "t.db", apply=True, snapshot_dir=tmp_path / "snap")
    conn = sqlite3.connect(src)
    assert conn.execute("SELECT COUNT(*) FROM denkarium_entries").fetchone()[0] == 3
    conn.close()


def test_unmappable_row_aborts_before_any_write(tmp_path: Path) -> None:
    bad = ROWS + [(13, "unbekannt", None, "x", "n", "user", None, None, None, "2026-01-01 00:00", None, 0, None, None)]
    src = make_source(tmp_path / "source.db", bad)
    target = tmp_path / "llm-note.db"
    with pytest.raises(MigrationError):
        migrate(src, target, apply=True, snapshot_dir=tmp_path / "snap")
    assert not target.exists()


def test_apply_requires_snapshot_dir(tmp_path: Path) -> None:
    src = make_source(tmp_path / "source.db", ROWS)
    with pytest.raises(MigrationError, match="snapshot"):
        migrate(src, tmp_path / "t.db", apply=True)
