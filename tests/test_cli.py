import os
import subprocess
import sys
from pathlib import Path

import pytest

import llm_note.cli as cli_module
import llm_note.gui as gui_module
from llm_note.i18n import STANDARD_LOCALES, load_messages
from llm_note.store import NoteStore


def run_cli(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
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
        env=environment,
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


def test_cli_localizes_help_and_validation_for_every_locale(capsys) -> None:
    for locale in STANDARD_LOCALES:
        messages = load_messages(locale)
        with pytest.raises(SystemExit) as help_exit:
            cli_module.main(["--locale", locale, "--help"])
        assert help_exit.value.code == 0
        help_output = capsys.readouterr().out
        assert f"{messages['cli_usage_label']}:" in help_output
        assert f"{messages['cli_options_label']}:" in help_output
        assert messages["cli_description"] in help_output
        assert messages["cli_help_action"] in help_output
        assert f"{messages['cli_help_action']}:" not in help_output

        with pytest.raises(SystemExit) as subcommand_help_exit:
            cli_module.main(["--locale", locale, "read", "--help"])
        assert subcommand_help_exit.value.code == 0
        subcommand_help = capsys.readouterr().out
        assert messages["cli_read_help"] in subcommand_help
        assert f"{messages['cli_options_label']}:" in subcommand_help

        with pytest.raises(SystemExit) as limit_exit:
            cli_module.main(["--locale", locale, "read", "--limit", "-1"])
        assert limit_exit.value.code == 2
        limit_error = capsys.readouterr().err
        assert messages["cli_argument_error"].format(
            argument="--limit",
            message=messages["cli_limit_range"].format(max=1000),
        ) in limit_error
        assert "Traceback" not in limit_error

        with pytest.raises(SystemExit) as port_exit:
            cli_module.main(["--locale", locale, "gui", "--port", "65536"])
        assert port_exit.value.code == 2
        port_error = capsys.readouterr().err
        assert messages["cli_argument_error"].format(
            argument="--port",
            message=messages["cli_port_range"],
        ) in port_error

        with pytest.raises(SystemExit) as mood_exit:
            cli_module.main(["--locale", locale, "write", "test", "--mood", "bad"])
        assert mood_exit.value.code == 2
        mood_error = capsys.readouterr().err
        assert messages["cli_argument_error"].format(
            argument="--mood",
            message=messages["cli_mood_integer"],
        ) in mood_error


def test_cli_localized_write_and_stats_format_every_catalog(
    tmp_path: Path,
    capsys,
) -> None:
    for locale in STANDARD_LOCALES:
        database = tmp_path / f"{locale}.db"
        assert cli_module.main(
            [
                "--db",
                str(database),
                "--locale",
                locale,
                "write",
                f"note in {locale}",
            ]
        ) == 0
        write_output = capsys.readouterr().out.strip()
        messages = load_messages(locale)
        assert write_output == messages["saved"].format(id=1, category="note")

        assert cli_module.main(
            [
                "--db",
                str(database),
                "--locale",
                locale,
                "stats",
            ]
        ) == 0
        stats_output = capsys.readouterr().out.strip()
        assert stats_output == messages["stats_total"].format(total=1, promoted=0)


def test_cli_does_not_read_locale_from_note_content_after_delimiter(
    tmp_path: Path,
    capsys,
) -> None:
    database = tmp_path / "literal-locale.db"
    assert cli_module.main(
        [
            "--db",
            str(database),
            "write",
            "--",
            "--locale=de",
        ]
    ) == 0
    assert capsys.readouterr().out.strip() == "saved note #1 (note)"
    assert NoteStore(database).list_entries()[0].content == "--locale=de"


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


def test_cli_gui_without_locale_leaves_browser_preference_available(monkeypatch) -> None:
    captured = {}

    def fake_run_server(db_path, *, port, locale, open_browser):
        captured.update(
            db_path=db_path,
            port=port,
            locale=locale,
            open_browser=open_browser,
        )

    monkeypatch.setattr(gui_module, "run_server", fake_run_server)

    assert cli_module.main(["gui", "--no-browser"]) == 0
    assert captured["locale"] is None
