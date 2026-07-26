import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

import llm_note.store as store_module
from llm_note import FileNotebookStore, NoteStore


def test_note_store_writes_and_searches_entries(tmp_path: Path) -> None:
    store = NoteStore(tmp_path / "notes.db")

    entry = store.write(
        "Keep the note engine local-first.",
        entry_type="logbook",
        category="idea",
        title="Architecture",
        mood=5,
    )

    assert entry.id == 1
    assert entry.entry_type == "logbook"

    matches = store.search("local-first")
    assert len(matches) == 1
    assert matches[0].title == "Architecture"
    assert matches[0].mood == 5


def test_note_store_brainstorm_and_promote_marks_entry(tmp_path: Path) -> None:
    store = NoteStore(tmp_path / "notes.db")

    entry = store.brainstorm("release checklist")
    promoted = store.promote(entry.id, "task")

    assert promoted.promoted_to == "task"
    assert "release checklist" in promoted.content
    assert store.stats()["total"] == 1
    assert store.stats()["promoted"] == 1


def test_note_store_treats_like_wildcards_as_literals_and_validates_limits(
    tmp_path: Path,
) -> None:
    store = NoteStore(tmp_path / "notes.db")
    store.write("100% literal_under")
    store.write("unrelated")

    assert [entry.content for entry in store.search("%")] == ["100% literal_under"]
    assert [entry.content for entry in store.search("_")] == ["100% literal_under"]
    with pytest.raises(ValueError, match="between 0 and 1000"):
        store.list_entries(limit=-1)
    with pytest.raises(ValueError, match="between 0 and 1000"):
        store.search("note", limit=1001)


def test_note_store_closes_connections_after_context(tmp_path: Path) -> None:
    store = NoteStore(tmp_path / "notes.db")

    with store._connect() as connection:
        connection.execute("SELECT 1").fetchone()

    with pytest.raises(sqlite3.ProgrammingError, match="closed database"):
        connection.execute("SELECT 1")


def test_file_notebook_store_sanitizes_names_and_transfers(tmp_path: Path) -> None:
    notebooks = FileNotebookStore(tmp_path / "notebooks")

    notebooks.write("Buy milk\n#NB: Shopping List")
    notebooks.transfer_marked_entries()

    default_text = notebooks.read()
    shopping_text = notebooks.read("Shopping List")

    assert "#NB:" not in default_text
    assert "Buy milk" in shopping_text
    assert (tmp_path / "notebooks" / "Shopping_List.txt").exists()


def test_file_notebook_store_keeps_self_referential_transfer(tmp_path: Path) -> None:
    notebooks = FileNotebookStore(tmp_path / "notebooks")

    notebooks.write("Keep this in the default inbox\n#NB: Notizblock")
    source_path = notebooks.notebook_path()
    before = source_path.read_bytes()
    transferred = notebooks.transfer_marked_entries()

    default_text = notebooks.read()
    assert transferred == 0
    assert source_path.read_bytes() == before
    assert "Keep this in the default inbox" in default_text
    assert "#NB: Notizblock" in default_text


def test_file_notebook_store_noop_transfer_preserves_bytes(tmp_path: Path) -> None:
    notebooks = FileNotebookStore(tmp_path / "notebooks")
    source_path = notebooks.notebook_path()
    original = (
        b"preamble  \r\n---\r\n[2026-07-15 06:00]\r\nKeep trailing spaces  \r\n\r\n"
    )
    source_path.write_bytes(original)

    assert notebooks.transfer_marked_entries() == 0
    assert source_path.read_bytes() == original


def test_file_notebook_store_preserves_kept_blocks_during_transfer(
    tmp_path: Path,
) -> None:
    notebooks = FileNotebookStore(tmp_path / "notebooks")
    source_path = notebooks.notebook_path()
    kept = b"preamble  \r\n---\r\n[2026-07-15 06:00]\r\nKeep trailing spaces  \r\n\r\n"
    moved = b"---\r\n[2026-07-15 06:01]\r\nMove this\r\n#NB: Target\r\n\r\n"
    source_path.write_bytes(kept + moved)

    assert notebooks.transfer_marked_entries() == 1
    assert source_path.read_bytes() == kept
    assert "Move this" in notebooks.read("Target")


def test_file_notebook_store_serializes_concurrent_transfers(tmp_path: Path) -> None:
    root = tmp_path / "notebooks"
    FileNotebookStore(root).write("Transfer exactly once\n#NB: Target")
    stores = [FileNotebookStore(root), FileNotebookStore(root)]

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(lambda store: store.transfer_marked_entries(), stores)
        )

    target = FileNotebookStore(root).read("Target")
    assert sorted(results) == [0, 1]
    assert target.count("Transfer exactly once") == 1


def test_file_notebook_store_retry_after_source_replace_failure_is_idempotent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    notebooks = FileNotebookStore(tmp_path / "notebooks")
    source_path = notebooks.notebook_path()
    transfer_id = "12345678-1234-4234-8234-123456789abc"
    source_path.write_text(
        "---\n[2026-07-15 06:01]\nTransfer once\n"
        f"#LLM-NOTE-ID: {transfer_id}\n#NB: Target\n\n",
        encoding="utf-8",
    )
    real_atomic_write = store_module._atomic_write_text
    calls = 0

    def fail_source_replace(path: Path, content: str) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("forced source replace failure")
        real_atomic_write(path, content)

    monkeypatch.setattr(store_module, "_atomic_write_text", fail_source_replace)
    with pytest.raises(OSError, match="forced source replace failure"):
        notebooks.transfer_marked_entries()

    assert notebooks.read("Target").count("Transfer once") == 1
    assert "#NB: Target" in notebooks.read()

    monkeypatch.setattr(store_module, "_atomic_write_text", real_atomic_write)
    assert notebooks.transfer_marked_entries() == 1
    assert notebooks.read("Target").count("Transfer once") == 1
    assert "#NB: Target" not in notebooks.read()


def test_file_notebook_store_replaces_duplicate_transfer_ids(tmp_path: Path) -> None:
    notebooks = FileNotebookStore(tmp_path / "notebooks")
    source_path = notebooks.notebook_path()
    duplicate_id = "12345678-1234-4234-8234-123456789abc"
    source_path.write_text(
        "---\n[2026-07-15 06:01]\nFirst\n"
        f"#LLM-NOTE-ID: {duplicate_id}\n#NB: Target\n\n"
        "---\n[2026-07-15 06:02]\nSecond\n"
        f"#LLM-NOTE-ID: {duplicate_id}\n#NB: Target\n\n",
        encoding="utf-8",
    )

    assert notebooks.transfer_marked_entries() == 2
    target = notebooks.read("Target")
    ids = [match.group(1) for match in store_module._TRANSFER_ID_RE.finditer(target)]
    assert "First" in target
    assert "Second" in target
    assert len(ids) == len(set(ids)) == 2


def test_file_notebook_store_keeps_unicode_names_distinct(tmp_path: Path) -> None:
    notebooks = FileNotebookStore(tmp_path / "notebooks")

    japanese = notebooks.write("日本語の内容", "日本語")
    chinese = notebooks.write("中文内容", "中文")
    russian = notebooks.write("Русский текст", "русский")

    assert len({japanese, chinese, russian}) == 3
    assert japanese.name == "日本語.txt"
    assert chinese.name == "中文.txt"
    assert russian.name == "русский.txt"
    assert "中文内容" not in notebooks.read("日本語")


def test_file_notebook_store_prefixes_windows_reserved_names(tmp_path: Path) -> None:
    notebooks = FileNotebookStore(tmp_path / "notebooks")

    assert notebooks.notebook_path("NUL").name == "_NUL.txt"
    assert notebooks.notebook_path("con.txt").name == "_con.txt"
