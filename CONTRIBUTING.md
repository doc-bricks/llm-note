# Contributing to llm-note

[English](#english) · [Deutsch](#deutsch)

---

<a id="english"></a>
## English

Thank you for contributing to `llm-note`. We follow strict standards for local-first architecture, privacy guarantees, and software quality.

### 1. Architectural Mandates & Invariants
- **100% Local-First & Zero Egress**: Never introduce network calls, remote analytics, or telemetry.
- **Zero External Runtime Dependencies**: Runtime code must strictly rely only on Python's standard library and SQLite. Build tools (`hatchling`, `pytest`, `ruff`) remain dev-only.
- **Unprivileged Execution (`RunAsInvoker`)**: Never require administrative or root privileges.
- **System Invariants**: Respect `INV-LOCAL-01` through `INV-SLA-10` defined in `THIRD_PARTY_LICENSES.md`.

### 2. Plan D Local Development Workflow
- Development takes place in canonical Git clone (`C:\_Local_DEV\repos\llm-note`).
- OneDrive locations serve purely as gitless projections/mirrors for multi-device visibility.
- Never initialize `.git` inside cloud synchronization directories.

### 3. Version Freeze Discipline (T-20260920-167562623)
- Package versions are frozen unless an explicit version release ticket is assigned.
- All technical hygiene improvements, contract tests, and non-breaking refinements are documented under `## [Unreleased]` in `CHANGELOG.md`.

### 4. Quality Gates & Local Verification
Before opening a pull request, run the complete verification suite:
```bash
# Editable install
pip install -e .

# Testing & Linting
python -m pytest -ra -v
ruff check llm_note tests

# Bytecode compilation & build check
python -m compileall -q .
python -m build
git diff --check
```

---

<a id="deutsch"></a>
## Deutsch

Vielen Dank für dein Interesse an `llm-note`. Wir verfolgen kompromisslose Standards für Offline-Autarkie, Datenschutz und Softwarequalität.

### 1. Architektur-Vorgaben & Invarianten
- **100% Lokal-Zuerst & Zero Egress**: Keine externen Netzwerkaufrufe, keine Telemetrie, kein Tracking.
- **Null externe Laufzeit-Abhängigkeiten**: Der Produktionscode nutzt ausschließlich die Python-Standardbibliothek und SQLite.
- **Unprivilegierte Ausführung (`RunAsInvoker`)**: Keinerlei Admin- oder Root-Rechte erforderlich.
- **System-Invarianten**: Einhaltung von `INV-LOCAL-01` bis `INV-SLA-10` gemäß `THIRD_PARTY_LICENSES.md`.

### 2. Plan-D-Entwicklungsworkflow
- Kanonischer Arbeitsort ist der lokale Git-Klon (`C:\_Local_DEV\repos\llm-note`).
- OneDrive ist lediglich ein gitloser Projektionsspiegel zur geräteübergreifenden Verfügbarkeit.

### 3. Versions-Einfrier-Disziplin (T-20260920-167562623)
- Versionen bleiben stabil eingefroren; Neuerungen werden unter `## [Unreleased]` in `CHANGELOG.md` eingetragen.

### 4. Quality Gates
```bash
python -m pytest -ra -v
ruff check llm_note tests
python -m compileall -q .
git diff --check
```
