"""Contract tests for doc-bricks/llm-note metadata, discoverability, and governance."""

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10: tomllib arrived in 3.11
    tomllib = None

REPO_ROOT = Path(__file__).resolve().parent.parent

def test_version_consistency():
    """Verify that version 1.0.5 is synchronized across all manifests."""
    pyproject_text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    version_match = re.search(r'version\s*=\s*"([^"]+)"', pyproject_text)
    assert version_match, "Could not find version in pyproject.toml"
    version = version_match.group(1)
    assert version == "1.0.5", f"Expected version 1.0.5 in pyproject.toml, got {version}"

    # Check __version__ in package __init__.py
    import llm_note

    assert getattr(llm_note, "__version__", None) == "1.0.5"

    # Check ellmos-module.v2.json
    module_data = json.loads((REPO_ROOT / "ellmos-module.v2.json").read_text(encoding="utf-8"))
    assert module_data.get("version") == "1.0.5"

    # Check plugin/plugin.json
    plugin_data = json.loads((REPO_ROOT / "plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert plugin_data.get("version") == "1.0.5"

    # Check CHANGELOG.md entry
    changelog_text = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [1.0.5] - 2026-10-04" in changelog_text

def test_pep621_compliance_and_urls():
    """Verify PEP 621/639 compliance, URLs, classifiers, and test settings in pyproject.toml."""
    pyproject_text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    toml = tomllib or pytest.importorskip("tomli")
    data = toml.loads(pyproject_text)
    project = data["project"]

    assert project["name"] == "llm-note"
    assert project["requires-python"] == ">=3.10"
    assert project["license"] == "MIT"
    assert project["dependencies"] == []
    assert "dev" in project.get("optional-dependencies", {})

    required_urls = [
        "Homepage",
        "Documentation",
        "Repository",
        "Issues",
        "Changelog",
        "Security",
        "Third-Party Licenses",
        "Third-Party Licenses Text",
        "Plain-Text License",
        "Contributing",
        "Code of Conduct",
        "Parent Organization",
        "Umbrella Ecosystem",
        "LLM Ready",
    ]
    urls = project.get("urls", {})
    for url_key in required_urls:
        assert url_key in urls, f"Missing required URL key: {url_key}"
    assert "Marketing Log" not in urls

    # PEP 639: SPDX license expression must not coexist with OSI license classifiers.
    classifiers = project.get("classifiers", [])
    assert not any(c.startswith("License :: OSI Approved ::") for c in classifiers)
    assert "Operating System :: OS Independent" in classifiers
    assert "Programming Language :: Python :: 3.10" in classifiers
    assert "Programming Language :: Python :: 3.13" in classifiers

    # Pytest configuration is consolidated in pyproject.toml (no duplicate pytest.ini).
    assert not (REPO_ROOT / "pytest.ini").exists(), "Duplicate pytest.ini must not override pyproject.toml"
    pytest_opts = data["tool"]["pytest"]["ini_options"]
    assert pytest_opts["addopts"] == "-ra -v"
    assert pytest_opts["pythonpath"] == ["."]
    assert pytest_opts["xfail_strict"] is True
    assert "references" in pytest_opts["norecursedirs"]


def test_marketing_log_is_untracked_and_gitignored():
    """Verify *MARKETING-LOG.txt is gitignored and never tracked in git (T-20260926-455218633)."""
    gitignore_text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "*MARKETING-LOG.txt" in gitignore_text

    pyproject_text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "MARKETING-LOG.txt" not in pyproject_text

    if (REPO_ROOT / ".git").exists():
        tracked = subprocess.run(
            ["git", "ls-files", "*MARKETING-LOG.txt", "MARKETING-LOG.txt"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert tracked.stdout.strip() == "", f"Tracked marketing log found: {tracked.stdout}"


def test_llms_txt_integrity():
    """Verify llms.txt context metadata, compatibility pointer llm.txt, and review date."""
    llms_file = REPO_ROOT / "llms.txt"
    assert llms_file.exists(), "llms.txt must exist"
    text = llms_file.read_text(encoding="utf-8")

    assert "Version: 1.0.5" in text
    assert "Last-checked: 2026-11-14" in text
    assert "doc-bricks" in text
    assert "open-bricks" in text
    assert "MARKETING-LOG.txt" not in text

    llm_compat = REPO_ROOT / "llm.txt"
    assert llm_compat.exists(), "llm.txt compatibility pointer must exist"
    assert "llms.txt" in llm_compat.read_text(encoding="utf-8")

def test_readme_navigation_and_anchor_parity():
    """Verify section navigation across locales and stable EN/DE anchor aliases."""
    filenames = [
        "README.md",
        "README_de.md",
        "README_es.md",
        "README_zh-Hans.md",
        "README_ja.md",
        "README_ru.md",
    ]
    contents = {name: (REPO_ROOT / name).read_text(encoding="utf-8") for name in filenames}

    for filename, text in contents.items():
        for i in range(1, 19):
            heading_prefix = f"## {i}."
            assert heading_prefix in text, f"Missing section {heading_prefix} in {filename}"
            sec_anchor = f'<a id="sec-{i:02d}"></a>'
            assert sec_anchor in text, f"Missing anchor {sec_anchor} in {filename}"
        assert "[![Tests:" not in text, f"Static test-count badge found in {filename}"

    # Check key reciprocal anchor tags retained in the full EN/DE versions.
    readme_en = contents["README.md"]
    readme_de = contents["README_de.md"]
    key_anchors = [
        "1-overview--why-this-exists",
        "1-ueberblick--warum-dieses-projekt-existiert",
        "4-note--transfer-lifecycle-sequence",
        "4-sequenzdiagramm-notiz--und-transfer-lebenszyklus",
        "6-comparative-matrix-vs-alternatives",
        "6-vergleichsmatrix-gegenueber-alternativen",
        "17-german-statutory-notice--521-bgb",
        "17-gesetzlicher-haftungshinweis--521-bgb",
    ]
    for anchor in key_anchors:
        assert f'id="{anchor}"' in readme_en, f"Missing anchor {anchor} in README.md"
        assert f'id="{anchor}"' in readme_de, f"Missing anchor {anchor} in README_de.md"

def test_zero_external_runtime_dependencies():
    """Verify via AST parsing that llm_note has 0 external runtime dependencies."""
    import ast

    pkg_dir = REPO_ROOT / "llm_note"
    py_files = list(pkg_dir.rglob("*.py"))
    assert py_files, "Expected to find python source files in llm_note"

    stdlib = sys.stdlib_module_names
    external_imports = set()

    for f in py_files:
        tree = ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_mod = alias.name.split(".")[0]
                    if root_mod != "llm_note" and root_mod not in stdlib:
                        external_imports.add(f"{root_mod} in {f.name}")
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                root_mod = node.module.split(".")[0]
                if root_mod != "llm_note" and root_mod not in stdlib:
                    external_imports.add(f"{root_mod} in {f.name}")

    assert not external_imports, f"Discovered external runtime imports: {external_imports}"

def test_mermaid_diagram_markers_and_message_guardrails():
    """Check diagram markers and project-specific message rules; this does not parse Mermaid syntax."""
    for filename in ["README.md", "README_de.md"]:
        text = (REPO_ROOT / filename).read_text(encoding="utf-8")
        blocks = re.findall(r"```mermaid\n(.*?)\n```", text, flags=re.DOTALL)
        assert len(blocks) >= 2, f"Expected at least 2 Mermaid blocks in {filename}, found {len(blocks)}"

        # Check flowchart and sequence diagram presence
        has_flowchart = any("graph TD" in b or "flowchart TD" in b for b in blocks)
        has_sequence = any("sequenceDiagram" in b for b in blocks)
        assert has_flowchart, f"Missing flowchart in {filename}"
        assert has_sequence, f"Missing sequence diagram in {filename}"

        # HOOK-BANNER-ASSET-01: sequenceDiagram messages must not have semicolons
        for b in blocks:
            if "sequenceDiagram" in b:
                assert "autonumber" in b, f"Expected autonumber in sequence diagram of {filename}"
                for line in b.splitlines():
                    if "->>" in line or "-->>" in line:
                        msg_part = line.split(":", 1)[-1] if ":" in line else ""
                        assert ";" not in msg_part, f"Semicolon found in sequence message: {line} in {filename}"

def test_banner_asset_guardrails():
    """Verify HOOK-BANNER-ASSET-01: banner assets exist and are referenced in documentation."""
    png_banner = REPO_ROOT / "assets" / "banner.png"
    svg_banner = REPO_ROOT / "assets" / "banner.svg"

    assert png_banner.exists(), "assets/banner.png must exist"
    assert svg_banner.exists(), "assets/banner.svg must exist"

    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert 'src="assets/banner.png"' in readme_en or 'src="assets/banner.svg"' in readme_en
    assert 'src="assets/banner.png"' in readme_de or 'src="assets/banner.svg"' in readme_de

def test_github_workflows_and_labels_hygiene():
    """Verify CI, auto-assign, label-sync, labels.yml, and issue templates."""
    workflows_dir = REPO_ROOT / ".github" / "workflows"
    assert (workflows_dir / "ci.yml").exists(), "ci.yml must exist"
    assert (workflows_dir / "auto-assign.yml").exists(), "auto-assign.yml must exist"
    assert (workflows_dir / "label-sync.yml").exists(), "label-sync.yml must exist"

    ci_text = (workflows_dir / "ci.yml").read_text(encoding="utf-8")
    assert "concurrency:" in ci_text
    assert "cancel-in-progress: true" in ci_text
    assert "workflow_dispatch:" in ci_text
    assert "python -m compileall -q llm_note tests" in ci_text
    assert "git diff --check" in ci_text
    assert "python -m pip check" in ci_text

    auto_assign_text = (workflows_dir / "auto-assign.yml").read_text(encoding="utf-8")
    assert "pull_request_target" in auto_assign_text
    assert "pull-requests: write" in auto_assign_text
    assert "github.event.pull_request.user.type != 'Bot'" in auto_assign_text

    label_sync_text = (workflows_dir / "label-sync.yml").read_text(encoding="utf-8")
    assert "EndBug/label-sync" in label_sync_text

    labels_file = REPO_ROOT / ".github" / "labels.yml"
    assert labels_file.exists(), ".github/labels.yml must exist"
    labels_text = labels_file.read_text(encoding="utf-8")
    assert "bug" in labels_text
    assert "enhancement" in labels_text

    issue_tpl_dir = REPO_ROOT / ".github" / "ISSUE_TEMPLATE"
    assert (issue_tpl_dir / "bug_report.md").exists()
    assert (issue_tpl_dir / "feature_request.md").exists()

def test_contributing_guide_bilingual_parity():
    """Verify bilingual contributor instructions keep local verification reproducible."""
    contrib_file = REPO_ROOT / "CONTRIBUTING.md"
    assert contrib_file.exists(), "CONTRIBUTING.md must exist"
    text = contrib_file.read_text(encoding="utf-8")

    assert "## English" in text
    assert "## Deutsch" in text
    for command in [
        "python -m pip install -e . pytest ruff build",
        "python -m pytest -ra -v",
        "ruff check llm_note tests",
        "python -m compileall -q .",
        "python -m build",
        "git diff --check",
    ]:
        assert text.count(command) == 2, (
            f"Expected the command in both language sections: {command}"
        )

def test_gitignore_cloud_and_lock_defense():
    """Verify .gitignore multi-host sync and lock protection patterns."""
    gitignore_file = REPO_ROOT / ".gitignore"
    assert gitignore_file.exists(), ".gitignore must exist"
    text = gitignore_file.read_text(encoding="utf-8")

    assert "*-IDEAPAD*" in text
    assert "*_WORKSTATION*" in text
    assert "LOCK.dev.*" in text
    assert "LOCK.antigravity.*" in text
    assert "LOCK.orchestrator.*" in text
    assert "LOCK-CACHE.*" in text
    assert ".gemini/" in text
    assert "Desktop.ini" in text
    assert "*conflicted copy*" in text


def test_code_of_conduct_and_module_manifest_parity():
    """Verify bilingual Code of Conduct and ellmos-module.v2.json boundaries."""
    coc_text = (REPO_ROOT / "CODE_OF_CONDUCT.md").read_text(encoding="utf-8")
    assert "## English" in coc_text
    assert "## Deutsch" in coc_text

    module_data = json.loads((REPO_ROOT / "ellmos-module.v2.json").read_text(encoding="utf-8"))
    assert module_data["schema"] == "ellmos.module.v2"
    assert module_data["id"] == "llm-note"
    assert module_data["version"] == "1.0.5"
    assert module_data["boundaries"]["network"] == "none"
    assert module_data["source_of_truth"]["repository"] == "https://github.com/doc-bricks/llm-note.git"


def test_ascii_four_view_architectural_topology_parity():
    """Verify ASCII Four-View Architectural Topology presence and invariant projection."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    # Check anchor presence
    assert 'id="four-view-architectural-topology-projection"' in readme_en
    assert 'id="vier-sichten-architekturtopologie-projektion"' in readme_de

    # Check English Views
    for view_id in ["VIEW 1:", "VIEW 2:", "VIEW 3:", "VIEW 4:"]:
        assert view_id in readme_en, f"Missing {view_id} in README.md"

    # Check German Sichten
    for sicht_id in ["SICHT 1:", "SICHT 2:", "SICHT 3:", "SICHT 4:"]:
        assert sicht_id in readme_de, f"Missing {sicht_id} in README_de.md"

    # Check all 10 invariants projected in both
    for i in range(1, 11):
        inv = f"INV-LOCAL-{i:02d}"
        assert inv in readme_en, f"Missing {inv} in README.md topology"
        assert inv in readme_de, f"Missing {inv} in README_de.md topology"
