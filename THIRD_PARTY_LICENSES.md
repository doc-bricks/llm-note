# Third-Party License Audit & Transparency Notice

<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 2026 Lukas Geiger -->

## 1. Executive Summary & Zero External Runtime Dependencies

`llm-note` is engineered with an uncompromising **zero external runtime dependencies** architectural mandate. The package relies exclusively on the Python standard library for all runtime features: SQLite thought persistence, plain-text file notebook coordination, the CLI, the multi-locale translation engine, and the loopback-only web GUI (Denkarium).

```text
===============================================================================
                    llm-note RUNTIME DEPENDENCY AUDIT
===============================================================================
Runtime Dependencies:       0 (Zero)
External Network Egress:    0 (Zero / Air-Gapped)
Elevated Privileges Needed: 0 (RunAsInvoker unprivileged user space)
License Architecture:       100% Permissive (MIT / Python Software Foundation)
Copyleft Obligations:       None (Zero GPL, LGPL, AGPL, SSPL)
===============================================================================
```

---

## 2. Software Bill of Materials (SBOM)

### 2.1 Core Runtime Components (Python Standard Library)

All core modules are governed by the official [Python Software Foundation License](https://docs.python.org/3/license.html), which is OSI-approved and fully compatible with the permissive MIT License.

| Standard Library Module | Purpose in `llm-note` | Upstream Governance | SPDX License ID |
| :--- | :--- | :--- | :--- |
| `sqlite3` | Local ACID thought log & metadata storage | Python Software Foundation | `PSF-2.0` |
| `http.server` | Local loopback GUI server (`127.0.0.1`) | Python Software Foundation | `PSF-2.0` |
| `urllib.parse` | Query string & URL parsing for GUI endpoints | Python Software Foundation | `PSF-2.0` |
| `argparse` | Command-line interface parsing (`llm-note`) | Python Software Foundation | `PSF-2.0` |
| `json` | Structured API serialization & locale file parsing | Python Software Foundation | `PSF-2.0` |
| `pathlib` | Cross-platform filesystem path abstraction | Python Software Foundation | `PSF-2.0` |
| `threading` | GUI loopback server process control | Python Software Foundation | `PSF-2.0` |
| `dataclasses` | Strongly typed entry structures | Python Software Foundation | `PSF-2.0` |
| `datetime` | ISO-8601 UTC timestamp generation | Python Software Foundation | `PSF-2.0` |
| `hashlib` | Idempotent transfer marker identification | Python Software Foundation | `PSF-2.0` |
| `os`, `sys`, `re` | Path safety, encoding, regex literal searches | Python Software Foundation | `PSF-2.0` |

### 2.2 Development, Testing & Build-Time Tooling (Not Distributed at Runtime)

The following tools are utilized exclusively during development, linting, packaging, and CI testing. They are **not** bundled into the distribution wheel and are **not** required for running `llm-note`.

| Tool | Purpose | License | SPDX License ID | Copyleft? |
| :--- | :--- | :--- | :--- | :---: |
| `hatchling` | PEP 517/621 build backend | MIT License | `MIT` | No |
| `pytest` | Test execution framework | MIT License | `MIT` | No |
| `ruff` | Fast Python linter & code formatter | MIT / Apache-2.0 | `MIT OR Apache-2.0` | No |

---

## 3. Governance & System Invariants

The implementation of `llm-note` complies strictly with the following 10 architectural invariants:

| Invariant ID | Name | Architectural Contract & Guarantee |
| :--- | :--- | :--- |
| `INV-LOCAL-01` | **100% Local-First & Zero Egress** | Never initiates outbound network connections. No telemetry, no remote analytics, no API pingbacks. |
| `INV-LOCAL-02` | **SQLite Single-File Storage** | All structured agent notes are stored in a standard SQLite file (`data/notes.db`) with full transactional integrity. |
| `INV-LOCAL-03` | **Plain-Text Notebook Inboxes** | Plain-text scratchpad files (`notebooks/*.txt`) enable effortless Git tracking and human-in-the-loop editing. |
| `INV-LOCAL-04` | **Standard Library Only** | Zero third-party runtime dependencies. Installs cleanly anywhere Python 3.10+ is available without wheel downloads. |
| `INV-LOCAL-05` | **Crash-Safe Atomic Transfers** | Safe cross-process coordination via `.llm-note.lock` and `#LLM-NOTE-ID` idempotency markers preventing note duplication. |
| `INV-LOCAL-06` | **Loopback-Bound Web GUI** | Optional Denkarium GUI strictly binds to loopback (`127.0.0.1`), with support for custom ports and `--no-browser`. |
| `INV-LOCAL-07` | **Multi-Locale I18N** | Native message bundling across 6 languages: English, German, Spanish, Simplified Chinese, Japanese, and Russian. |
| `INV-LOCAL-08` | **RunAsInvoker Execution** | Fully operational in unprivileged user space. Zero administrative elevation, no kernel hooks, no driver installation. |
| `INV-LOCAL-09` | **Agent Skill Packaging** | Ships an agent-ready skill definition (`skills/llm-note/SKILL.md`) for seamless LLM workflow tool integration. |
| `INV-LOCAL-10` | **48-Hour Security SLA** | Formal vulnerability handling commitments documented in `SECURITY.md` (48h triage, 5d response). |

---

## 4. Zero-Copyleft & IP Affirmation

1. **No Copyleft Taint**: No code from GNU General Public License (GPL v2/v3), GNU Affero General Public License (AGPL), or Server Side Public License (SSPL) is included, linked, or vendored within `llm-note`.
2. **Commercial & Private Use**: The permissive MIT License grants users the unrestricted right to inspect, modify, distribute, embed, and utilize `llm-note` in private, commercial, and enterprise software ecosystems without royalty obligations.
3. **BACH Extraction Provenance**: The package was cleanly decoupled from the BACH desktop assistant codebase (specifically Notizblock and Denkarium). All historical ties and proprietary abstractions were refactored into pure standard-library interfaces.

---

## 5. Security & Privilege Notice (`RunAsInvoker`)

`llm-note` requires no administrator rights, root privileges, or Windows UAC elevation. Running `llm-note` under elevated privileges is neither recommended nor supported.

- **Filesystem Boundaries**: All database writes and notebook file operations are strictly confined to the directory paths provided by the user or configuration. Path traversal attempts (e.g. `../`) are rejected during path resolution.
- **Process Isolation**: The loopback HTTP server runs in the calling process thread, handles requests synchronously, and terminates cleanly upon receiving `SIGINT` or `Ctrl+C`.
