"""Small locale loader for CLI/user-facing strings."""

from __future__ import annotations

import json
from importlib import resources

STANDARD_LOCALES = ("de", "en", "es", "zh-Hans", "ja", "ru")


def normalize_locale(locale: str | None = None) -> str:
    """Return a supported catalog for a language or regional locale tag."""
    if not isinstance(locale, str) or not locale.strip():
        return "en"

    tag = locale.strip().replace("_", "-")
    for supported in STANDARD_LOCALES:
        if tag.casefold() == supported.casefold():
            return supported

    language = tag.split("-", maxsplit=1)[0].casefold()
    if language == "zh":
        return "zh-Hans"
    for supported in STANDARD_LOCALES:
        if language == supported.casefold():
            return supported
    return "en"


def load_messages(locale: str | None = "en") -> dict[str, str]:
    locale = normalize_locale(locale)
    with resources.files("llm_note.locales").joinpath(f"{locale}.json").open(
        "r", encoding="utf-8"
    ) as handle:
        return json.load(handle)
