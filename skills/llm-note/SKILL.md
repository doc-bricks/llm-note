---
name: llm-note
description: Use when an agent needs to capture, search, organize, or promote local notes, logbook entries, brainstorms, or plain-text notebooks during LLM work.
---

# llm-note

## Overview

Use `llm-note` as a local-first scratchpad for agent work. It combines a SQLite note log with plain-text notebooks and keeps user data outside git by default.

## Quick Start

```bash
llm-note write "Investigate release privacy checklist" --cat release
llm-note read --limit 5
llm-note search privacy
llm-note brainstorm "next release"
llm-note stats
```

Use `--db <path>` for a project-local database and `--locale de|en|es|zh-Hans|ja|ru` for localized CLI messages.

## When To Use Which Store

| Need | Use |
|---|---|
| Structured notes, categories, search, promotion markers | `NoteStore` / CLI |
| Portable inbox notes or topic notebooks | `FileNotebookStore` |
| Moving inbox notes into topic notebooks | `#NB: Target Notebook` plus `transfer_marked_entries()` |
| Host-system tasks/wiki/issues | `promote(entry_id, "task"|"wiki"|"issue")` as a marker, then let the host system act |

## Python Pattern

```python
from llm_note import FileNotebookStore, NoteStore

notes = NoteStore("data/notes.db")
entry = notes.write("Document the gate-check result", category="release")
notes.promote(entry.id, "task")

notebooks = FileNotebookStore("notebooks")
notebooks.write("Buy milk\n#NB: Shopping List")
notebooks.transfer_marked_entries()
```

## Safety Rules

- Keep `.db`, notebook folders, and `.env` files out of git.
- Do not store secrets or private user data in public repo fixtures.
- When adding user-facing messages, add the same key to all six locale JSON files.
- Run `python -m pytest -q` after code or locale changes.
