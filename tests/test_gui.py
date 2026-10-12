import json
import threading
from pathlib import Path
from urllib.request import Request, urlopen

import llm_note.gui as gui_module
from llm_note.gui import create_server
from llm_note.i18n import STANDARD_LOCALES, load_messages


def test_gui_serves_page_and_reads_and_writes_notes(tmp_path: Path) -> None:
    server = create_server(tmp_path / "notes.db", port=0, locale="de")
    server.store.write("Diese Notiz erscheint in der GUI.", category="beleg")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"

    try:
        with urlopen(f"{base_url}/", timeout=5) as response:
            page = response.read().decode("utf-8")
            assert response.status == 200
            assert "Denkarium" in page
            assert "Einträge" in page
            assert "fonts.googleapis.com" not in page

        with urlopen(f"{base_url}/api/entries", timeout=5) as response:
            data = json.load(response)
            assert data["entries"][0]["content"] == (
                "Diese Notiz erscheint in der GUI."
            )

        payload = json.dumps(
            {
                "content": "Über HTTP gespeichert.",
                "entry_type": "logbook",
                "category": "test",
                "mood": 4,
            }
        ).encode("utf-8")
        request = Request(
            f"{base_url}/api/entries",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=5) as response:
            created = json.load(response)["entry"]
            assert response.status == 201
            assert created["content"] == "Über HTTP gespeichert."
            assert created["entry_type"] == "logbook"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def test_gui_embeds_all_locale_catalogs_and_initial_language_over_http(
    tmp_path: Path,
) -> None:
    for locale in STANDARD_LOCALES:
        server = create_server(tmp_path / f"{locale}.db", port=0, locale=locale)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with urlopen(f"http://127.0.0.1:{server.server_port}/", timeout=5) as response:
                page = response.read().decode("utf-8")
            assert f'<html lang="{locale}">' in page
            assert 'id="locale" aria-labelledby="language-label"' in page
            assert load_messages(locale)["gui_save_error"] in page
            assert "__GUI_CONFIG_JSON__" not in page
            assert "__GUI_COPY_JSON__" not in page
            assert "简体中文" in page
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()


def test_gui_without_explicit_locale_leaves_choice_to_client_without_server_state(
    tmp_path: Path,
) -> None:
    server = create_server(tmp_path / "browser-choice.db", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/", timeout=5) as response:
            page = response.read().decode("utf-8")
        assert '<html lang="en">' in page
        assert '"initialLocale": null' in page
        assert server.locale is None
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def test_gui_server_messages_use_locale_and_close_on_keyboard_interrupt(
    monkeypatch,
    capsys,
) -> None:
    class InterruptingServer:
        server_port = 43210

        def __init__(self) -> None:
            self.closed = False

        def serve_forever(self) -> None:
            raise KeyboardInterrupt

        def server_close(self) -> None:
            self.closed = True

    url = "http://127.0.0.1:43210/"
    for locale in (None, *STANDARD_LOCALES):
        server = InterruptingServer()
        monkeypatch.setattr(
            gui_module,
            "create_server",
            lambda *_args, _server=server, **_kwargs: _server,
        )

        gui_module.run_server(locale=locale, open_browser=False)

        messages = load_messages(locale)
        assert capsys.readouterr().out.splitlines() == [
            messages["cli_gui_started"].format(url=url),
            messages["cli_gui_stop"],
        ]
        assert server.closed


def test_gui_search_combines_text_and_type_filters(tmp_path: Path) -> None:
    server = create_server(tmp_path / "notes.db", port=0)
    server.store.write("shared phrase", entry_type="note")
    server.store.write("shared phrase", entry_type="logbook")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        url = (
            f"http://127.0.0.1:{server.server_port}/api/entries"
            "?search=shared&entry_type=logbook"
        )
        with urlopen(url, timeout=5) as response:
            data = json.load(response)
        assert data["count"] == 1
        assert data["entries"][0]["entry_type"] == "logbook"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
