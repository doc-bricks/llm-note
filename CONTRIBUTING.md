# Contributing to llm-note

[English](#english) · [Deutsch](#deutsch)

---

<a id="english"></a>
## English

Thank you for contributing to `llm-note`. We aim to keep the local-first architecture, public documentation, and software quality accurate and consistent.

### 1. Architecture and documentation

- **Local-first core:** Do not introduce external telemetry or cloud clients into core runtime code. This is a development rule; it is not a claim that the operating system blocks all network egress.
- **Runtime dependencies:** The project currently declares no additional Python runtime packages and uses the Python standard library and SQLite. Build and development tools are separate from runtime dependencies.
- **Process permissions:** Do not require administrative or root elevation. The process inherits the permissions of the process that launches it; this statement is not a Windows execution certification.
- Keep security, privacy, and dependency statements tied to checked source or distribution evidence. Do not present tests or documentation strings as a security or compliance certification.

### 2. Local development workflow

- Work from a local Git checkout at the repository root.
- OneDrive locations may serve as gitless projections or mirrors for multi-device visibility.
- Do not initialize a Git repository inside a cloud-synchronization directory.

### 3. Version freeze discipline (T-20260920-167562623)

- Package versions are frozen unless an explicit version release ticket is assigned.
- Technical hygiene improvements, contract tests, and non-breaking refinements belong under `## [Unreleased]` in `CHANGELOG.md`.

### 4. Quality gates and local verification

Before opening a pull request, run the project verification suite:

```bash
# Editable install and local verification tools
python -m pip install -e . pytest ruff build

# Tests and lint
python -m pytest -ra -v
ruff check llm_note tests

# Bytecode compilation and local build check
python -m compileall -q .
python -m build
git diff --check
```

These commands validate the local checkout; they do not publish a release.

---

<a id="deutsch"></a>
## Deutsch

Vielen Dank für deinen Beitrag zu `llm-note`. Wir halten die lokal ausgerichtete Architektur, die öffentliche Dokumentation und die Qualitätsangaben sachlich und aufeinander abgestimmt.

### 1. Architektur und Dokumentation

- **Lokaler Kern:** Führe keine externen Telemetrie- oder Cloud-Clients in den Laufzeitkern ein. Das ist eine Entwicklungsregel und keine Aussage, dass das Betriebssystem jeden Netzwerkverkehr blockiert.
- **Laufzeitabhängigkeiten:** Das Projekt deklariert derzeit keine zusätzlichen Python-Laufzeitpakete und verwendet die Python-Standardbibliothek sowie SQLite. Build- und Entwicklungswerkzeuge sind davon getrennt.
- **Prozessrechte:** Fordere keine Administrator- oder Root-Erhöhung an. Der Prozess übernimmt die Berechtigungen des aufrufenden Prozesses; das ist keine Windows-Ausführungszertifizierung.
- Sicherheits-, Datenschutz- und Abhängigkeitsaussagen müssen sich auf geprüften Quellcode oder konkrete Distributionsbelege stützen. Tests und Dokumentationstexte sind keine Sicherheits- oder Compliance-Zertifizierung.

### 2. Lokaler Entwicklungsworkflow

- Entwickle in einem lokalen Git-Klon im Repository-Stammverzeichnis.
- OneDrive-Pfade können gitlose Projektionen oder Spiegel für die Verfügbarkeit auf mehreren Geräten sein.
- Initialisiere kein Git-Repository in einem Cloud-Synchronisationsordner.

### 3. Versions-Einfrier-Disziplin (T-20260920-167562623)

- Paketversionen bleiben eingefroren, sofern kein ausdrückliches Versionierungs-Ticket vorliegt.
- Technische Pflege, Vertragstests und nicht rückwärtsbrechende Verbesserungen gehören unter `## [Unreleased]` in `CHANGELOG.md`.

### 4. Qualitätsprüfungen und lokale Verifikation

Führe vor einem Pull Request die Projektprüfungen aus:

```bash
python -m pip install -e . pytest ruff build
python -m pytest -ra -v
ruff check llm_note tests
python -m compileall -q .
python -m build
git diff --check
```

Diese Befehle prüfen den lokalen Klon; sie veröffentlichen kein Release.
