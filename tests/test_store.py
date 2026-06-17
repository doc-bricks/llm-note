from pathlib import Path

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


def test_file_notebook_store_sanitizes_names_and_transfers(tmp_path: Path) -> None:
    notebooks = FileNotebookStore(tmp_path / "notebooks")

    notebooks.write("Buy milk\n#NB: Shopping List")
    notebooks.transfer_marked_entries()

    default_text = notebooks.read()
    shopping_text = notebooks.read("Shopping List")

    assert "#NB:" not in default_text
    assert "Buy milk" in shopping_text
    assert (tmp_path / "notebooks" / "Shopping_List.txt").exists()
