"""Small locale loader for CLI/user-facing strings."""

from __future__ import annotations

from importlib import resources
import json

STANDARD_LOCALES = ("de", "en", "es", "zh-Hans", "ja", "ru")


def load_messages(locale: str = "en") -> dict[str, str]:
    if locale not in STANDARD_LOCALES:
        locale = "en"
    with resources.files("llm_note.locales").joinpath(f"{locale}.json").open(
        "r", encoding="utf-8"
    ) as handle:
        return json.load(handle)
