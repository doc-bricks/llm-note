"""One-off, idempotent migration of BACH ``denkarium_entries`` into llm-note.

Dry run is the default. ``--apply`` first snapshots the source table, then imports
via :meth:`NoteStore.import_entry` (keeps timestamps, remembers the old id as
``legacy_id``) and aborts on a count mismatch. The source table is only read.

    python -m llm_note.migrate_denkarium SOURCE_DB TARGET_DB [--apply --snapshot-dir DIR]
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from .store import ENTRY_TYPE_ALIASES, NoteStore

_TABLE = "denkarium_entries"
_VALID_TYPES = set(ENTRY_TYPE_ALIASES) | set(ENTRY_TYPE_ALIASES.values())


class MigrationError(RuntimeError):
    """Raised when the source cannot be mapped losslessly."""


def _read_source(source_db: Path) -> list[dict]:
    conn = sqlite3.connect(f"file:{source_db.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in conn.execute(f"SELECT * FROM {_TABLE} ORDER BY id")]
    finally:
        conn.close()


def _snapshot(source_db: Path, snapshot_dir: Path) -> Path:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    out = snapshot_dir / f"{_TABLE}_{datetime.now(timezone.utc):%Y%m%d-%H%M%S-%f}.db"
    src = sqlite3.connect(f"file:{source_db.as_posix()}?mode=ro", uri=True)
    dst = sqlite3.connect(out)
    try:
        rows = src.execute(f"SELECT * FROM {_TABLE}")
        cols = [d[0] for d in rows.description]
        dst.execute(f"CREATE TABLE {_TABLE} ({', '.join(cols)})")
        dst.executemany(
            f"INSERT INTO {_TABLE} VALUES ({', '.join('?' * len(cols))})", rows.fetchall()
        )
        dst.commit()
    finally:
        src.close()
        dst.close()
    return out


def _kwargs(row: dict) -> dict:
    if row.get("entry_type") not in _VALID_TYPES:
        raise MigrationError(f"id {row['id']}: unknown entry_type {row.get('entry_type')!r}")
    if not row.get("content"):
        raise MigrationError(f"id {row['id']}: empty content")
    mood = row.get("mood")
    return {
        "entry_type": row["entry_type"],
        "category": row.get("category") or "note",
        "title": row.get("title"),
        "mood": mood if isinstance(mood, int) and 1 <= mood <= 5 else None,  # 0 -> NULL
        "source": row.get("source") or "user",
        "tags": row.get("tags"),
        "promoted_to": row.get("promoted_to"),
        "promoted_id": row.get("promoted_id"),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "legacy_id": row["id"],
        "is_archived": bool(row.get("is_archived")),
        "archived_reason": row.get("archived_reason"),
        "archived_at": row.get("archived_at"),
    }


def migrate(
    source_db: str | Path,
    target_db: str | Path,
    *,
    apply: bool = False,
    snapshot_dir: str | Path | None = None,
) -> dict:
    source_db, target_db = Path(source_db), Path(target_db)
    rows = _read_source(source_db)
    prepared = [(r["content"], _kwargs(r)) for r in rows]  # preflight: all or nothing
    report: dict = {"dry_run": not apply, "source_count": len(rows), "imported": 0}
    if not apply:
        return report
    if snapshot_dir is None:
        raise MigrationError("apply requires a snapshot_dir (snapshot of the source first)")
    report["snapshot"] = str(_snapshot(source_db, Path(snapshot_dir)))

    store = NoteStore(target_db)
    # ponytail: list limit 1000 (MAX_QUERY_LIMIT); Denkarium has ~14 rows, add paging if ever larger
    known = {e.legacy_id for e in store.list_entries(include_archived=True, limit=1000)}
    mapping: dict[str, int] = {}
    for content, kw in prepared:
        entry = store.import_entry(content, **kw)
        mapping[str(kw["legacy_id"])] = entry.id
        report["imported"] += kw["legacy_id"] not in known
    mig_ids = {e.legacy_id for e in store.list_entries(include_archived=True, limit=1000)}
    report["mapping"] = mapping
    report["target_count"] = len(mig_ids & {r["id"] for r in rows})
    if report["target_count"] != len(rows):
        raise MigrationError(f"count mismatch: source {len(rows)} != target {report['target_count']}")
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("source_db")
    ap.add_argument("target_db")
    ap.add_argument("--apply", action="store_true", help="really write (default: dry run)")
    ap.add_argument("--snapshot-dir")
    args = ap.parse_args(argv)
    try:
        report = migrate(args.source_db, args.target_db, apply=args.apply, snapshot_dir=args.snapshot_dir)
    except MigrationError as exc:
        print(f"ABORT: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
