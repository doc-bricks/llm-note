# Release Gate: llm-note

## Current gate: version 1.0.5

**Status: NOT CLEARED.** The package version remains frozen at 1.0.5. This document does not authorize a version change, tag, release, upload, or publication.

This gate describes evidence required for a future release from an exact, reviewed candidate commit. On 2026-10-12, the current care worktree passed its local tests, lint, compilation, wheel/sdist build, fresh wheel installation, and artifact-content check. That care-validation snapshot is not a selected release candidate and does not clear this gate.

| Check | Required evidence | Current state |
|---|---|---|
| Source and CI | Reviewed final diff and successful CI for the exact candidate commit | No release candidate selected; check the current source-CI workflow for a future candidate |
| Tests and lint | Full test suite, Ruff, compilation, and `git diff --check` on the final tree | Care worktree passed 38 tests and all listed checks on 2026-10-12; this does not approve a release candidate |
| Packaging | Build wheel and sdist from the final tree; record hashes; install the wheel in a fresh environment and verify the installed files | Care worktree wheel/sdist built and wheel fresh-installed on 2026-10-12; candidate-specific release review remains required |
| Documentation and metadata | English and translated docs agree on current behavior, dependencies, security response targets, and legal scope | In progress |
| Distribution review | Inspect the produced wheel and sdist contents and metadata; do not infer this from source-only checks | Care worktree artifacts inspected on 2026-10-12; independent review remains required for any future release candidate |

Local build artifacts are review evidence only. No release artifact is authorized for upload or publication by this gate.

## Historical gate record: version 1.0.1 (2026-07-15)

The following record is preserved as historical evidence for the 1.0.1 source at that time. Its UNLOCKED result and checks do not apply to version 1.0.5 or later source.

```text
+------------------------------------------+
|                                          |
|          HISTORICAL: UNLOCKED            |
|                                          |
+------------------------------------------+
```

> The 2026-07-15 record states that the public repository passed its then-documented local release gates. It is not a current release approval.

### Historical checklist

| # | Check | Recorded result | Historical note |
|---|-------|---|---|
| 1 | `.gitignore` with minimum entries | PASS | Present |
| 2 | `README.md` in English | PASS | Present |
| 3 | `LICENSE` (MIT) present | PASS | Present |
| 4 | No `.db` files tracked | PASS | `.gitignore` excluded local DB files |
| 5 | No `.env` files tracked | PASS | `.gitignore` excluded environment files |
| 6 | No secrets in tracked files | PASS | Scan recorded 2026-07-15 |
| 7 | No hardcoded personal paths | PASS | Scan recorded 2026-07-15 |
| 8 | PII patterns | PASS recorded | The old note “No email contacts” was incomplete; public repository files contain contact email addresses. This is not a comprehensive PII finding. |
| 9 | No BACH-internal documents | PASS | Provenance only |
| 10 | `TODO.md` with status table | PASS | Present |

### Historical gate execution

```text
Date:       2026-07-15
Script:     .AI/.MODULES/_scripts/final_gate_check.py
Command:    PYTHONIOENCODING=utf-8 python _scripts/final_gate_check.py --repo-path .TOOLS/llm-note
Exit Code:  0
Output:     10 PASS, 0 FAIL, 0 WARN
```

### Historical verification

| Check | Recorded result |
|---|---|
| Independent final review | 0×P0, 0×P1, 0×P2 |
| Pytest | 16 passed |
| Ruff | `llm_note` and `tests` clean |
| Bandit | Product package clean |
| Windows multi-process transfer probe | 12/12 rounds passed |
| Forced transfer failure windows | Target, partial multi-target, and final source retries passed |
| Package build | Wheel and sdist 1.0.1 built from the then-current source |
| Fresh wheel install | `pip check` clean; 11/11 package files source-identical |
| Module manifest | v2 schema valid; public Git source configured |

Historical artifact names:

```text
llm_note-1.0.1-py3-none-any.whl
llm_note-1.0.1.tar.gz
```

The historical record said final SHA-256 values were recorded in an external FABLE run log after the source documentation was frozen and artifacts rebuilt.

### Historical sign-off

| Field | Value |
|---|---|
| Responsible | Lukas Geiger (@lukisch) |
| Review date | 2026-07-15 |
| Decision | UNLOCKED after exit code 0 |
| Remarks | Patch 1.0.1 addressed transfer integrity, Unicode paths, SQLite lifecycle, query bounds, packaging, and CI. |
