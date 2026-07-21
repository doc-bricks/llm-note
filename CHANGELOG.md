# Changelog

## 1.0.2 - 2026-07-22

- Added `pythonpath = .` to `pytest.ini` to support direct `pytest` invocation without manual `PYTHONPATH` configuration.
- Synchronized `llms.txt` Last-checked header and `TODO.md` audit timestamp to 2026-07-22.
- Verified test suite execution (16/16 tests passing) and `ruff` linting.

## 1.0.1 - 2026-07-15

- Improved README and German README positioning for local-first agent notes, private AI notebooks, and SQLite logbook use cases.
- Added current `llms.txt` search phrases, audience notes, and disambiguation for LLM and GitHub discoverability.
- Expanded package keywords for agent-memory, notebook, privacy-first, and CLI discovery.
- Preserved self-referential transfer markers and byte-identical no-op transfers.
- Serialized file-notebook operations across processes, added stable transfer IDs, and atomically replaced sources and targets for crash-safe retries.
- Preserved Unicode notebook names while keeping paths inside the configured notebook root.
- Closed SQLite connections deterministically, treated search wildcards literally, and bounded query limits.
- Added a portable catalog manifest and hardened CI with pinned actions, Windows/Linux coverage, linting, builds, and Dependabot updates.

## 1.0.0 - 2026-06-18

- Initial public release.
- Extracted the BACH Notizblock/Denkarium pattern into a standalone Python package.
- Added SQLite note store, plain-text notebooks, CLI, six locales, tests, skill metadata, and release gate documentation.
