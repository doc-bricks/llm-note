# Third-party dependency and license notes

<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 2026 Lukas Geiger -->

Reviewed: 2026-10-12

This document summarizes direct Python dependencies declared or used by this repository. It is a scoped dependency note, not a complete software bill of materials, a transitive dependency audit, a license-compliance opinion, or a security certification. The MIT license for this repository is in [LICENSE](LICENSE).

## Runtime

The `[project]` metadata in `pyproject.toml` declares no Python runtime package dependencies. The application uses modules from the Python standard library, including `sqlite3`, `http.server`, and `argparse`. SQLite and other native components are supplied by the Python and operating-system environment.

This statement describes the project metadata and direct runtime package requirements. It does not inventory every component in a user's Python distribution or make a claim about all possible distribution contents.

## Build, test, and lint tools

| Tool | Repository use | Declared or invoked by | Upstream license information |
| :--- | :--- | :--- | :--- |
| `hatchling>=1.25` | PEP 517 build backend | `pyproject.toml` `[build-system]` | MIT; [PyPA Hatch source](https://github.com/pypa/hatch/blob/master/LICENSE.txt) |
| `pytest` | Test runner | CI workflow and contributor checks | MIT; [pytest source](https://github.com/pytest-dev/pytest/blob/main/LICENSE) |
| `ruff` | Linter | CI workflow and contributor checks | MIT; [Ruff source](https://github.com/astral-sh/ruff/blob/main/LICENSE) |
| `build` | Local wheel and source-distribution builder | CI workflow and contributor checks | MIT; [PyPA build source](https://github.com/pypa/build/blob/main/LICENSE) |

These are build or development tools, not application runtime dependencies. Their versions and transitive dependencies are managed by the environment that installs them and are not exhaustively inventoried here. License links point to the respective upstream projects; this note does not certify the complete licensing status of their dependency trees.

## Standard library reference

The Python standard library's licensing information is maintained by the [Python Software Foundation](https://docs.python.org/3/license.html). This repository does not vendor a separate copy of the Python runtime.

## Implementation facts

- Notes are stored in local SQLite and plain-text notebook files.
- The optional web interface binds to loopback at `127.0.0.1`.
- The process does not request administrative elevation and inherits the permissions of the process that launches it.
- These implementation facts do not establish an operating-system egress block, sandbox, complete software inventory, or independent security certification.
