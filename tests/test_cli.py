import subprocess
import sys
from pathlib import Path


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
