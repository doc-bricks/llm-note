# Changelog

## [Unreleased]

- Hardened CI workflow (`.github/workflows/ci.yml`) with concurrency cancellation (`cancel-in-progress: true`) and Python matrix testing across versions 3.10 through 3.13.
- Standardized PEP 621 metadata in `pyproject.toml` with contributor and plain-text dependency-note URLs, and configured `norecursedirs` under `[tool.pytest.ini_options]`.
- Reworked `THIRD_PARTY_LICENSES.md` and `THIRD_PARTY_LICENSES.txt` as scoped notes about declared runtime requirements and direct build/development tools; they no longer present a complete SBOM or license-compliance certification.
- Updated all six README files and `SECURITY.md` to describe local storage, loopback binding, inherited process permissions, maintainer response targets, and the limits of the available evidence.
- Replaced comparative claims about other products' network behavior, process permissions, and security response with “not assessed” entries.
- Removed dated test-count, zero-egress, RunAsInvoker, and response-SLA badges; the existing CI badge remains the live status indicator.
- Revised the § 521 BGB note to leave application and consequences to the specific circumstances; the repository license remains unchanged.
- Revised `CONTRIBUTING.md` with a local checkout workflow and reproducible editable-install, test, lint, and build commands in English and German.
- Updated `llms.txt` with a 2026-10-12 review date and current implementation boundaries.
- Added a dated editorial supersession notice to `MARKETING-LOG.txt`; prior marketing text remains as historical material.
- Reworked `RELEASE_GATE.md` to keep version 1.0.5 frozen, distinguish the historical 1.0.1 record, and state that the current release gate is not cleared.
- Kept useful metadata, version, navigation, anchor, asset, runtime-import, CI, contributor-command, and host-sync tests; removed literal tests of old marketing, legal, and security claims.
- Preserved package version 1.0.5 and made no release or upload.

## [1.0.5] - 2026-10-04

- Fixed packaging metadata: removed the OSI license classifier that conflicts with the PEP 639 `license=` expression (#6).
- Combined nested `if` statements to satisfy Ruff SIM102 (#7).
- Added an installation section to `README.md` and `README_de.md`.
- Completed the full translations of the README in Spanish, Chinese (Simplified), Japanese and Russian.
- Version `1.0.4` was never tagged; its changes below are released together with `1.0.5`.

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
