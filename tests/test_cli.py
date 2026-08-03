import subprocess
import sys
from pathlib import Path

import llm_note.cli as cli_module
import llm_note.gui as gui_module


def run_cli(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "llm_note.cli",
            "--db",
            str(tmp_path / "notes.db"),
            *args,
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def test_cli_write_and_search(tmp_path: Path) -> None:
    write = run_cli(tmp_path, "write", "A portable note for agents", "--cat", "idea")
    assert write.returncode == 0
    assert "saved" in write.stdout

    search = run_cli(tmp_path, "search", "portable")
    assert search.returncode == 0
    assert "portable note" in search.stdout


def test_cli_rejects_negative_read_limit(tmp_path: Path) -> None:
    result = run_cli(tmp_path, "read", "--limit", "-1")

    assert result.returncode == 2
    assert "limit must be between 0 and 1000" in result.stderr
    assert "Traceback" not in result.stderr


def test_cli_gui_entrypoint_uses_database_locale_and_port(
    tmp_path: Path,
    monkeypatch,
) -> None:
    captured = {}

    def fake_run_server(db_path, *, port, locale, open_browser):
        captured.update(
            db_path=db_path,
            port=port,
            locale=locale,
            open_browser=open_browser,
        )

    monkeypatch.setattr(gui_module, "run_server", fake_run_server)
    db_path = tmp_path / "gui.db"

    result = cli_module.main(
        [
            "--db",
            str(db_path),
            "--locale",
            "de",
            "gui",
            "--port",
            "8765",
            "--no-browser",
        ]
    )

    assert result == 0
    assert captured == {
        "db_path": str(db_path),
        "port": 8765,
        "locale": "de",
        "open_browser": False,
    }
