# Provenance

llm-note was extracted from two BACH-local patterns:

- `notizblock`: a file-based note inbox and topic notebook service.
- `denkarium`: a SQLite thought log with categories, logbook mode, brainstorm entries, and promotion markers.

The raw BACH export is preserved in `references/bach-export/notizblock/`. Source snapshots used during extraction are preserved in `references/bach-source/`.

## Web interface

The browser interface added on 2026-08-03 is adapted from BACH's public MIT
sources:

- `system/gui/templates/denkarium.html` supplied the calm, paper-like single
  column layout and the write/filter/search interaction pattern.
- The Denkarium routes in `system/gui/server.py` supplied the page plus JSON
  read/write boundary.
- `system/hub/gui.py` supplied the `gui` CLI-start convention.

The standalone implementation was rewritten around `llm_note.store.NoteStore`
and Python's standard-library `http.server`. It does not open or query a BACH
database.

The following BACH-specific parts were deliberately not transferred:

- FastAPI, Uvicorn, BACH handler/registry wiring, and dashboard navigation.
- BACH's `BACH_DB`/`USER_DB` schema and all private user data.
- Task- and wiki-promotion that writes into BACH tables.
- Authentication, Telegram/chat, partner, agent, and system integrations.
- Remote Google Fonts and other outbound browser dependencies.

The public package is standalone. It does not depend on BACH runtime modules,
BACH databases, user data, or private configuration.
