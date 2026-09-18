# Changelog

## [1.0.4] - 2026-09-18

- Added a standalone, loopback-only Denkarium web interface (`llm-note gui`) based on Python's
  standard-library `http.server` and the existing `NoteStore`, featuring custom port, locale,
  and `--no-browser` flags with zero external runtime dependencies.
- Added comprehensive Pfad B discoverability overhaul with 18-point bilingual quick navigation
  parity across `README.md` and `README_de.md` featuring synchronized reciprocal HTML anchor aliases.
- Added dual Mermaid architecture diagrams (System Topography Flowchart and Thought & Transfer
  Lifecycle Sequence Diagram with `autonumber`) adhering strictly to `HOOK-BANNER-ASSET-01` quoting.
- Created `THIRD_PARTY_LICENSES.md` documenting the formal SBOM (0 external runtime dependencies,
  100% Python standard library, PSF-2.0 upstream licenses, zero-copyleft certification, and
  unprivileged `RunAsInvoker` execution invariants `INV-LOCAL-01` to `INV-SLA-10`).
- Created `MARKETING-LOG.txt` outlining value proposition, 4 target personas (`[PERSONA-01]` to
  `[PERSONA-04]`), bilingual high-intent search queries, 10-dimension comparative matrix vs.
  4 alternatives (Obsidian, SQLite CLI, Joplin, Cloud Notes), and sibling ecosystem integration.
- Added automated contract test suite in `tests/test_metadata.py` verifying PEP 621 compliance,
  version alignment across all manifests, SPDX invariants, § 521 BGB disclaimer, and Mermaid syntax.
- Updated PEP 621 metadata in `pyproject.toml` with expanded URLs and `[tool.pytest.ini_options]`.
- Updated `llms.txt` context index to version 1.0.4 (Last-checked: 2026-09-18).

## 1.0.3 - 2026-07-27

- Aligned package, plugin, and portable module metadata with the documented 1.0.3 release line.
- Enhanced `README_de.md` with top banner image, full multi-language navigation bar, Ecosystem & Umbrella badges (`doc-bricks` / `open-bricks`), and verified test status.
- Added Ecosystem (`doc-bricks`) and Umbrella (`open-bricks`) badges to `README.md`.
- Synchronized `llms.txt` Last-checked header to 2026-07-27.
- Verified 100% test suite execution (16/16 tests passing in 4.86s).

## 1.0.2 - 2026-07-26

- Enhanced README.md and README_de.md with Shields.io badges, GFM LLM note callouts (`> [!NOTE]`), and Mermaid system architecture data-flow diagrams.
- Synchronized `llms.txt` Last-checked header and `TODO.md` audit timestamp to 2026-07-26.
- Added `pythonpath = .` to `pytest.ini` to support direct `pytest` invocation without manual `PYTHONPATH` configuration.
- Verified complete test suite execution (16/16 tests passing in 6.16s).

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
