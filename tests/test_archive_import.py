"""PB-11: archive, import with foreign timestamps and legacy migration."""

import sqlite3
from pathlib import Path

import pytest

from llm_note import NoteStore

OLD_SCHEMA = """
CREATE TABLE note_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_type TEXT NOT NULL DEFAULT 'note',
    title TEXT, content TEXT NOT NULL, category TEXT DEFAULT 'note',
    tags TEXT, source TEXT DEFAULT 'user', mood INTEGER,
    promoted_to TEXT, promoted_id INTEGER,
    created_at TEXT DEFAULT (datetime('now', 'localtime')), updated_at TEXT
)
"""


def test_archive_hides_entry_and_unarchive_restores(tmp_path: Path) -> None:
    store = NoteStore(tmp_path / "n.db")
    keep = store.write("keep")
    gone = store.write("gone")

    archived = store.archive(gone.id, "stale")

    assert archived.is_archived is True
    assert archived.archived_reason == "stale"
    assert archived.archived_at
    assert [e.id for e in store.list_entries()] == [keep.id]
    assert {e.id for e in store.list_entries(include_archived=True)} == {keep.id, gone.id}
    assert store.search("gone") == []
    assert [e.id for e in store.search("gone", include_archived=True)] == [gone.id]
    assert store.stats()["archived"] == 1

    restored = store.unarchive(gone.id)
    assert restored.is_archived is False
    assert restored.archived_reason is None
    assert {e.id for e in store.list_entries()} == {keep.id, gone.id}


def test_delete_removes_entry_and_unknown_id_raises(tmp_path: Path) -> None:
    store = NoteStore(tmp_path / "n.db")
    entry = store.write("x")
    store.delete(entry.id)
    with pytest.raises(KeyError):
        store.get(entry.id)
    with pytest.raises(KeyError):
        store.delete(entry.id)
    with pytest.raises(KeyError):
        store.archive(999)


def test_import_entry_keeps_foreign_timestamps_and_legacy_id(tmp_path: Path) -> None:
    store = NoteStore(tmp_path / "n.db")
    entry = store.import_entry(
        "old thought",
        entry_type="denkarium",
        category="notiz",
        created_at="2026-02-19 08:15",
        updated_at="2026-02-20 09:00",
        legacy_id=58,
        tags="a,b",
    )
    assert entry.entry_type == "note"  # alias denkarium -> note
    assert entry.created_at == "2026-02-19 08:15"
    assert entry.updated_at == "2026-02-20 09:00"
    assert entry.legacy_id == 58
    assert entry.tags == "a,b"


def test_import_entry_is_idempotent_per_legacy_id(tmp_path: Path) -> None:
    store = NoteStore(tmp_path / "n.db")
    first = store.import_entry("a", legacy_id=7, created_at="2026-01-01 00:00")
    again = store.import_entry("a", legacy_id=7, created_at="2026-01-01 00:00")
    assert again.id == first.id
    assert store.stats()["total"] == 1


def test_import_entry_can_import_archived_state(tmp_path: Path) -> None:
    store = NoteStore(tmp_path / "n.db")
    entry = store.import_entry(
        "z", legacy_id=1, is_archived=True, archived_reason="r", archived_at="2026-03-01 10:00"
    )
    assert entry.is_archived and entry.archived_at == "2026-03-01 10:00"
    assert store.list_entries() == []


def test_type_aliases_in_write_list_and_search(tmp_path: Path) -> None:
    store = NoteStore(tmp_path / "n.db")
    store.write("alpha", entry_type="logbuch")
    store.write("beta", entry_type="denkarium")
    assert [e.content for e in store.list_entries(entry_type="logbuch")] == ["alpha"]
    assert [e.content for e in store.list_entries(entry_type="denkarium")] == ["beta"]
    assert [e.content for e in store.search("alpha", entry_type="logbuch")] == ["alpha"]
    assert store.get(1).entry_type == "logbook"


def test_old_database_without_new_columns_is_migrated_on_open(tmp_path: Path) -> None:
    db = tmp_path / "old.db"
    conn = sqlite3.connect(db)
    conn.execute(OLD_SCHEMA)
    conn.execute(
        "INSERT INTO note_entries (entry_type, content, created_at) VALUES ('note', 'legacy row', '2026-01-02 03:04')"
    )
    conn.commit()
    conn.close()

    store = NoteStore(db)

    rows = store.list_entries()
    assert [e.content for e in rows] == ["legacy row"]
    assert rows[0].is_archived is False
    assert rows[0].created_at == "2026-01-02 03:04"
    store.archive(rows[0].id)
    assert store.list_entries() == []
    NoteStore(db)  # second open must not fail (idempotent migration)
