"""Contract tests for doc-bricks/llm-note metadata, discoverability, and governance."""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_version_consistency():
    """Verify that version 1.0.4 is synchronized across all manifests."""
    pyproject_text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    version_match = re.search(r'version\s*=\s*"([^"]+)"', pyproject_text)
    assert version_match, "Could not find version in pyproject.toml"
    version = version_match.group(1)
    assert version == "1.0.4", f"Expected version 1.0.4 in pyproject.toml, got {version}"

    # Check __version__ in package __init__.py
    import llm_note

    assert getattr(llm_note, "__version__", None) == "1.0.4"

    # Check ellmos-module.v2.json
    module_data = json.loads((REPO_ROOT / "ellmos-module.v2.json").read_text(encoding="utf-8"))
    assert module_data.get("version") == "1.0.4"

    # Check plugin/plugin.json
    plugin_data = json.loads((REPO_ROOT / "plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert plugin_data.get("version") == "1.0.4"

    # Check CHANGELOG.md entry
    changelog_text = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [1.0.4] - 2026-09-18" in changelog_text


def test_pep621_compliance_and_urls():
    """Verify PEP 621 compliance, URLs, classifiers, and test settings in pyproject.toml."""
    pyproject_text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert 'name = "llm-note"' in pyproject_text
    assert 'requires-python = ">=3.10"' in pyproject_text

    required_urls = [
        "Homepage",
        "Documentation",
        "Repository",
        "Issues",
        "Changelog",
        "Security",
        "Third-Party Licenses",
        "Marketing Log",
        "Parent Organization",
        "Umbrella Ecosystem",
        "LLM Ready",
    ]
    for url_key in required_urls:
        assert f'"{url_key}"' in pyproject_text or f"{url_key} =" in pyproject_text, (
            f"Missing required URL key: {url_key}"
        )

    # Classifiers
    assert "Operating System :: OS Independent" in pyproject_text
    assert "License :: OSI Approved :: MIT License" in pyproject_text
    assert "Programming Language :: Python :: 3.10" in pyproject_text
    assert "Programming Language :: Python :: 3.13" in pyproject_text

    # Pytest configuration
    assert "[tool.pytest.ini_options]" in pyproject_text
    assert 'addopts = "-ra -v"' in pyproject_text


def test_third_party_licenses_audit():
    """Verify THIRD_PARTY_LICENSES.md SBOM and the 10 system invariants."""
    licenses_file = REPO_ROOT / "THIRD_PARTY_LICENSES.md"
    assert licenses_file.exists(), "THIRD_PARTY_LICENSES.md must exist"
    text = licenses_file.read_text(encoding="utf-8")

    assert "PSF-2.0" in text
    assert "MIT" in text
    assert "Zero (Zero)" in text or "Runtime Dependencies:       0" in text
    assert "RunAsInvoker" in text

    for i in range(1, 11):
        inv_id = f"INV-LOCAL-{i:02d}"
        assert inv_id in text, f"Missing system invariant {inv_id} in THIRD_PARTY_LICENSES.md"


def test_marketing_log_audit():
    """Verify MARKETING-LOG.txt personas, comparative matrix, and audit record."""
    marketing_file = REPO_ROOT / "MARKETING-LOG.txt"
    assert marketing_file.exists(), "MARKETING-LOG.txt must exist"
    text = marketing_file.read_text(encoding="utf-8")

    for p in range(1, 5):
        persona_tag = f"[PERSONA-{p:02d}]"
        assert persona_tag in text, f"Missing persona {persona_tag} in MARKETING-LOG.txt"

    assert "10-DIMENSION COMPARATIVE MATRIX" in text
    assert "Obsidian" in text
    assert "Joplin" in text
    assert "2026-09-18" in text


def test_llms_txt_integrity():
    """Verify llms.txt AI context index."""
    llms_file = REPO_ROOT / "llms.txt"
    assert llms_file.exists(), "llms.txt must exist"
    text = llms_file.read_text(encoding="utf-8")

    assert "Version: 1.0.4" in text
    assert "Last-checked: 2026-09-18" in text
    assert "doc-bricks" in text
    assert "open-bricks" in text


def test_security_policy_slas():
    """Verify SECURITY.md SLAs and zero-egress commitments."""
    security_file = REPO_ROOT / "SECURITY.md"
    assert security_file.exists(), "SECURITY.md must exist"
    text = security_file.read_text(encoding="utf-8")

    assert "48" in text, "Expected 48h response SLA in SECURITY.md"
    assert "Zero Egress" in text or "zero-egress" in text.lower()


def test_readme_bilingual_navigation_and_anchor_parity():
    """Verify 18-point navigation parity and reciprocal HTML anchors in README.md & README_de.md."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    for i in range(1, 19):
        heading_prefix = f"## {i}."
        assert heading_prefix in readme_en, f"Missing section {heading_prefix} in README.md"
        assert heading_prefix in readme_de, f"Missing section {heading_prefix} in README_de.md"

    # Check key reciprocal anchor tags
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


def test_german_statutory_disclaimer():
    """Verify German statutory disclaimer (§ 521 BGB) in README_de.md."""
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
    assert "§ 521 BGB" in readme_de
    assert "Gefälligkeitsrecht" in readme_de or "Gefaelligkeitsrecht" in readme_de
    assert "Vorsatz und grobe Fahrlässigkeit" in readme_de or "grobe Fahrlaessigkeit" in readme_de


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
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    root_mod = node.module.split(".")[0]
                    if root_mod != "llm_note" and root_mod not in stdlib:
                        external_imports.add(f"{root_mod} in {f.name}")

    assert not external_imports, f"Discovered external runtime imports: {external_imports}"


def test_mermaid_diagrams_in_readmes():
    """Verify that Mermaid diagrams in README.md and README_de.md adhere to syntax guardrails."""
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
