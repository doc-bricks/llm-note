import json
import threading
from pathlib import Path
from urllib.request import Request, urlopen

from llm_note.gui import create_server


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
