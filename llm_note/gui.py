"""Local web interface for the SQLite note store."""

from __future__ import annotations

import json
import threading
import webbrowser
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

from .i18n import STANDARD_LOCALES
from .store import MAX_QUERY_LIMIT, NoteStore

MAX_REQUEST_BYTES = 1_000_000

_GUI_COPY = {
    "en": {
        "document_title": "llm-note Denkarium",
        "heading": "Denkarium",
        "subtitle": "Notes · logbook · ideas",
        "compose_placeholder": "What is on your mind?",
        "note": "Note",
        "notes": "Notes",
        "logbook": "Logbook",
        "category": "Category",
        "optional_title": "Title (optional)",
        "mood": "Mood",
        "save": "Save",
        "search": "Search notes …",
        "all": "All",
        "entries": "entries",
        "empty_title": "Empty pages",
        "empty_body": "Write your first note.",
        "loading": "Loading …",
        "load_error": "Could not load notes.",
        "save_error": "Could not save the note.",
    },
    "de": {
        "document_title": "llm-note Denkarium",
        "heading": "Denkarium",
        "subtitle": "Notizen · Logbuch · Ideen",
        "compose_placeholder": "Was bewegt dich gerade?",
        "note": "Notiz",
        "notes": "Notizen",
        "logbook": "Logbuch",
        "category": "Kategorie",
        "optional_title": "Titel (optional)",
        "mood": "Stimmung",
        "save": "Speichern",
        "search": "Notizen durchsuchen …",
        "all": "Alle",
        "entries": "Einträge",
        "empty_title": "Leere Seiten",
        "empty_body": "Schreibe deine erste Notiz.",
        "loading": "Lädt …",
        "load_error": "Notizen konnten nicht geladen werden.",
        "save_error": "Notiz konnte nicht gespeichert werden.",
    },
}


class NoteHTTPServer(ThreadingHTTPServer):
    """Threaded loopback server carrying a shared NoteStore."""

    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        server_address: tuple[str, int],
        store: NoteStore,
        locale: str,
    ) -> None:
        self.store = store
        self.locale = locale if locale in STANDARD_LOCALES else "en"
        super().__init__(server_address, NoteRequestHandler)


class NoteRequestHandler(BaseHTTPRequestHandler):
    """Serve the bundled interface and a small JSON API."""

    server: NoteHTTPServer

    def do_HEAD(self) -> None:  # noqa: N802 - stdlib handler API
        path = urlsplit(self.path).path
        if path in {"/", "/index.html"}:
            self._send_bytes(
                HTTPStatus.OK,
                self._render_page().encode("utf-8"),
                "text/html; charset=utf-8",
                include_body=False,
            )
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"}, False)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        parsed = urlsplit(self.path)
        if parsed.path in {"/", "/index.html"}:
            self._send_bytes(
                HTTPStatus.OK,
                self._render_page().encode("utf-8"),
                "text/html; charset=utf-8",
            )
            return
        if parsed.path == "/api/entries":
            try:
                payload = self._list_entries(parse_qs(parsed.query))
            except ValueError as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                return
            self._send_json(HTTPStatus.OK, payload)
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        if urlsplit(self.path).path != "/api/entries":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})
            return
        if not self._same_origin_request():
            self._send_json(HTTPStatus.FORBIDDEN, {"error": "origin not allowed"})
            return

        try:
            data = self._read_json_body()
            entry = self._create_entry(data)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            return
        self._send_json(HTTPStatus.CREATED, {"entry": asdict(entry)})

    def _list_entries(self, query: dict[str, list[str]]) -> dict[str, Any]:
        limit_text = query.get("limit", ["50"])[0]
        try:
            limit = int(limit_text)
        except ValueError as exc:
            raise ValueError("limit must be an integer") from exc
        if not 0 <= limit <= MAX_QUERY_LIMIT:
            raise ValueError(f"limit must be between 0 and {MAX_QUERY_LIMIT}")

        entry_type = query.get("entry_type", [""])[0].strip() or None
        category = query.get("category", [""])[0].strip() or None
        search = query.get("search", [""])[0].strip()
        if search:
            entries = self.server.store.search(
                search,
                entry_type=entry_type,
                category=category,
                limit=limit,
            )
        else:
            entries = self.server.store.list_entries(
                entry_type=entry_type,
                category=category,
                limit=limit,
            )

        stats = self.server.store.stats()
        return {
            "entries": [asdict(entry) for entry in entries],
            "count": len(entries),
            "stats": {
                **stats,
                "notes": max(0, stats["total"] - stats["logbook"]),
            },
        }

    def _read_json_body(self) -> dict[str, Any]:
        content_type = self.headers.get_content_type()
        if content_type != "application/json":
            raise ValueError("Content-Type must be application/json")
        length_text = self.headers.get("Content-Length")
        if length_text is None:
            raise ValueError("Content-Length is required")
        try:
            length = int(length_text)
        except ValueError as exc:
            raise ValueError("invalid Content-Length") from exc
        if not 0 <= length <= MAX_REQUEST_BYTES:
            raise ValueError("request body is too large")
        data = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(data, dict):
            raise TypeError("JSON body must be an object")
        return data

    def _create_entry(self, data: dict[str, Any]):
        content = data.get("content", "")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("content must not be empty")

        entry_type = data.get("entry_type", "note")
        if entry_type not in {"note", "logbook"}:
            raise ValueError("entry_type must be note or logbook")

        category = data.get("category", "note")
        if not isinstance(category, str):
            raise TypeError("category must be a string")
        category = category.strip() or "note"
        if len(category) > 100:
            raise ValueError("category must be at most 100 characters")

        title = data.get("title")
        if title is not None:
            if not isinstance(title, str):
                raise TypeError("title must be a string or null")
            title = title.strip() or None
            if title is not None and len(title) > 200:
                raise ValueError("title must be at most 200 characters")

        mood = data.get("mood")
        if mood is not None:
            if isinstance(mood, bool) or not isinstance(mood, int):
                raise TypeError("mood must be an integer or null")
            if not 1 <= mood <= 5:
                raise ValueError("mood must be between 1 and 5")

        return self.server.store.write(
            content.strip(),
            entry_type=entry_type,
            category=category,
            title=title,
            mood=mood,
            source="web",
        )

    def _same_origin_request(self) -> bool:
        origin = self.headers.get("Origin")
        if not origin:
            return True
        parsed = urlsplit(origin)
        return parsed.scheme == "http" and parsed.netloc == self.headers.get("Host")

    def _render_page(self) -> str:
        template = (
            resources.files("llm_note")
            .joinpath("templates", "denkarium.html")
            .read_text(encoding="utf-8")
        )
        locale = self.server.locale if self.server.locale in _GUI_COPY else "en"
        copy_json = json.dumps(_GUI_COPY[locale], ensure_ascii=False).replace(
            "</", "<\\/"
        )
        return template.replace("__GUI_LANG__", locale).replace(
            "__GUI_COPY_JSON__", copy_json
        )

    def _send_json(
        self,
        status: HTTPStatus,
        payload: dict[str, Any],
        include_body: bool = True,
    ) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send_bytes(
            status,
            body,
            "application/json; charset=utf-8",
            include_body=include_body,
        )

    def _send_bytes(
        self,
        status: HTTPStatus,
        body: bytes,
        content_type: str,
        *,
        include_body: bool = True,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; img-src 'none'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if include_body:
            self.wfile.write(body)


def create_server(
    db_path: str | Path = "llm-note.db",
    *,
    port: int = 8000,
    locale: str = "en",
) -> NoteHTTPServer:
    """Create a loopback-only GUI server without starting its event loop."""

    return NoteHTTPServer(("127.0.0.1", port), NoteStore(db_path), locale)


def run_server(
    db_path: str | Path = "llm-note.db",
    *,
    port: int = 8000,
    locale: str = "en",
    open_browser: bool = True,
) -> None:
    """Run the local GUI until interrupted."""

    server = create_server(db_path, port=port, locale=locale)
    url = f"http://127.0.0.1:{server.server_port}/"
    print(f"llm-note GUI: {url}")
    print("Press Ctrl+C to stop.")
    if open_browser:
        threading.Timer(0.2, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


__all__ = ["NoteHTTPServer", "create_server", "run_server"]
