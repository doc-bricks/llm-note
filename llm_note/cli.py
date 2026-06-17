"""Command line interface for llm-note."""

from __future__ import annotations

import argparse

from .i18n import load_messages
from .store import NoteStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="llm-note", description="Local-first notes for LLM agents")
    parser.add_argument("--db", default="llm-note.db", help="SQLite database path")
    parser.add_argument("--locale", default="en", help="Message locale")
    sub = parser.add_subparsers(dest="command", required=True)

    write = sub.add_parser("write", help="Write a note")
    write.add_argument("content")
    write.add_argument("--type", default="note", dest="entry_type")
    write.add_argument("--cat", default="note", dest="category")
    write.add_argument("--title")
    write.add_argument("--mood", type=int)

    read = sub.add_parser("read", help="Read recent notes")
    read.add_argument("--type", dest="entry_type")
    read.add_argument("--cat", dest="category")
    read.add_argument("--limit", type=int, default=10)

    search = sub.add_parser("search", help="Search notes")
    search.add_argument("term")

    brainstorm = sub.add_parser("brainstorm", help="Create a brainstorm note")
    brainstorm.add_argument("topic")

    sub.add_parser("stats", help="Show statistics")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    msg = load_messages(args.locale)
    store = NoteStore(args.db)

    if args.command == "write":
        entry = store.write(
            args.content,
            entry_type=args.entry_type,
            category=args.category,
            title=args.title,
            mood=args.mood,
        )
        print(msg["saved"].format(id=entry.id, category=entry.category))
        return 0

    if args.command == "read":
        entries = store.list_entries(
            entry_type=args.entry_type,
            category=args.category,
            limit=args.limit,
        )
        if not entries:
            print(msg["no_results"])
            return 0
        for entry in entries:
            print(_format_entry(entry))
        return 0

    if args.command == "search":
        entries = store.search(args.term)
        if not entries:
            print(msg["no_results"])
            return 0
        for entry in entries:
            print(_format_entry(entry))
        return 0

    if args.command == "brainstorm":
        entry = store.brainstorm(args.topic)
        print(msg["brainstorm_saved"].format(id=entry.id))
        return 0

    if args.command == "stats":
        stats = store.stats()
        print(msg["stats_total"].format(total=stats["total"], promoted=stats["promoted"]))
        return 0

    parser.print_help()
    return 2


def _format_entry(entry) -> str:
    title = f" {entry.title}" if entry.title else ""
    return f"#{entry.id} [{entry.category}]{title}: {entry.content}"


if __name__ == "__main__":
    raise SystemExit(main())
