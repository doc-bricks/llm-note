"""Command line interface for llm-note."""

from __future__ import annotations

import argparse
import re
import sys
from functools import partial

from .i18n import load_messages, normalize_locale
from .store import MAX_QUERY_LIMIT, NoteStore


class LocalizedArgumentParser(argparse.ArgumentParser):
    """Argument parser whose generated help and errors use one locale."""

    def __init__(self, *args, messages: dict[str, str], **kwargs) -> None:
        self.messages = messages
        kwargs["add_help"] = False
        super().__init__(*args, **kwargs)
        self.add_argument(
            "-h",
            "--help",
            action="help",
            help=self.messages["cli_help_action"],
        )

    def format_usage(self) -> str:
        return self._localize_help(super().format_usage())

    def format_help(self) -> str:
        return self._localize_help(super().format_help())

    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        translated = self._localize_error(message)
        self.exit(
            2,
            f"{self.prog}: {self.messages['cli_error_label']}: {translated}\n",
        )

    def _localize_help(self, text: str) -> str:
        for source, key in (
            ("usage:", "cli_usage_label"),
            ("positional arguments:", "cli_positional_label"),
            ("options:", "cli_options_label"),
        ):
            text = text.replace(source, f"{self.messages[key]}:")
        text = text.replace(
            "show this help message and exit",
            self.messages["cli_help_action"],
        )
        return text

    def _localize_error(self, message: str) -> str:
        required = "the following arguments are required: "
        if message.startswith(required):
            arguments = message[len(required) :]
            return self.messages["cli_required_arguments"].format(
                arguments=arguments
            )

        unrecognized = "unrecognized arguments: "
        if message.startswith(unrecognized):
            arguments = message[len(unrecognized) :]
            return self.messages["cli_unrecognized_arguments"].format(
                arguments=arguments
            )

        if message.startswith("argument ") and ": " in message:
            argument, detail = message[len("argument ") :].split(": ", maxsplit=1)
            detail = self._localize_error_detail(detail)
            return self.messages["cli_argument_error"].format(
                argument=argument,
                message=detail,
            )
        return self._localize_error_detail(message)

    def _localize_error_detail(self, message: str) -> str:
        if message == "expected one argument":
            return self.messages["cli_expected_one_argument"]

        invalid_integer = "invalid int value: "
        if message.startswith(invalid_integer):
            value = message[len(invalid_integer) :]
            return self.messages["cli_invalid_integer"].format(value=value)

        match = re.fullmatch(r"invalid choice: (.+?) \(choose from (.+)\)", message)
        if match:
            return self.messages["cli_invalid_choice"].format(
                value=match.group(1),
                choices=match.group(2),
            )
        return message


def _query_limit(value: str, messages: dict[str, str]) -> int:
    try:
        limit = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(messages["cli_limit_integer"]) from exc
    if not 0 <= limit <= MAX_QUERY_LIMIT:
        raise argparse.ArgumentTypeError(
            messages["cli_limit_range"].format(max=MAX_QUERY_LIMIT)
        )
    return limit


def _port(value: str, messages: dict[str, str]) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(messages["cli_port_integer"]) from exc
    if not 0 <= port <= 65535:
        raise argparse.ArgumentTypeError(messages["cli_port_range"])
    return port


def _mood(value: str, messages: dict[str, str]) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(messages["cli_mood_integer"]) from exc


def build_parser(locale: str | None = "en") -> argparse.ArgumentParser:
    messages = load_messages(locale)

    def parser_factory(**kwargs):
        return LocalizedArgumentParser(messages=messages, **kwargs)

    parser = LocalizedArgumentParser(
        prog="llm-note",
        description=messages["cli_description"],
        messages=messages,
    )
    parser.add_argument("--db", default="llm-note.db", help=messages["cli_db_help"])
    parser.add_argument(
        "--locale",
        default=None,
        metavar="LOCALE",
        help=messages["cli_locale_help"],
    )
    sub = parser.add_subparsers(
        dest="command",
        required=True,
        parser_class=parser_factory,
    )

    write = sub.add_parser(
        "write",
        help=messages["cli_write_help"],
        description=messages["cli_write_help"],
    )
    write.add_argument("content", help=messages["cli_content_help"])
    write.add_argument(
        "--type",
        default="note",
        dest="entry_type",
        help=messages["cli_type_help"],
    )
    write.add_argument(
        "--cat",
        default="note",
        dest="category",
        help=messages["cli_category_help"],
    )
    write.add_argument("--title", help=messages["cli_title_help"])
    write.add_argument(
        "--mood",
        type=partial(_mood, messages=messages),
        help=messages["cli_mood_help"],
    )

    read = sub.add_parser(
        "read",
        help=messages["cli_read_help"],
        description=messages["cli_read_help"],
    )
    read.add_argument(
        "--type",
        dest="entry_type",
        help=messages["cli_type_help"],
    )
    read.add_argument(
        "--cat",
        dest="category",
        help=messages["cli_category_help"],
    )
    read.add_argument(
        "--limit",
        type=partial(_query_limit, messages=messages),
        default=10,
        help=messages["cli_limit_help"],
    )

    search = sub.add_parser(
        "search",
        help=messages["cli_search_help"],
        description=messages["cli_search_help"],
    )
    search.add_argument("term", help=messages["cli_term_help"])

    brainstorm = sub.add_parser(
        "brainstorm",
        help=messages["cli_brainstorm_help"],
        description=messages["cli_brainstorm_help"],
    )
    brainstorm.add_argument("topic", help=messages["cli_topic_help"])

    sub.add_parser(
        "stats",
        help=messages["cli_stats_help"],
        description=messages["cli_stats_help"],
    )

    gui = sub.add_parser(
        "gui",
        help=messages["cli_gui_help"],
        description=messages["cli_gui_help"],
    )
    gui.add_argument(
        "--port",
        type=partial(_port, messages=messages),
        default=8000,
        help=messages["cli_port_help"],
    )
    gui.add_argument(
        "--no-browser",
        action="store_true",
        help=messages["cli_no_browser_help"],
    )
    return parser


def _requested_locale(argv: list[str]) -> str | None:
    locale: str | None = None
    commands = {"write", "read", "search", "brainstorm", "stats", "gui"}
    index = 0
    while index < len(argv):
        argument = argv[index]
        if argument == "--":
            break
        if argument in commands:
            break
        if argument == "--db":
            index += 2
            continue
        if argument.startswith("--db="):
            index += 1
            continue
        if argument.startswith("--locale="):
            locale = argument.split("=", maxsplit=1)[1]
            index += 1
            continue
        if argument == "--locale" and index + 1 < len(argv):
            locale = argv[index + 1]
            index += 2
            continue
        index += 1
    return locale


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    messages_locale = normalize_locale(_requested_locale(arguments))
    parser = build_parser(messages_locale)
    args = parser.parse_args(arguments)

    if args.command == "gui":
        from .gui import run_server

        run_server(
            args.db,
            port=args.port,
            locale=args.locale,
            open_browser=not args.no_browser,
        )
        return 0

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
        print(
            msg["stats_total"].format(total=stats["total"], promoted=stats["promoted"])
        )
        return 0

    parser.print_help()
    return 2


def _format_entry(entry) -> str:
    title = f" {entry.title}" if entry.title else ""
    return f"#{entry.id} [{entry.category}]{title}: {entry.content}"


if __name__ == "__main__":
    raise SystemExit(main())
