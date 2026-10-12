from string import Formatter

from llm_note.i18n import STANDARD_LOCALES, load_messages, normalize_locale


def _format_fields(value: str) -> set[str]:
    return {
        field_name
        for _, field_name, _, _ in Formatter().parse(value)
        if field_name is not None
    }


def test_standard_locales_are_complete() -> None:
    messages = {locale: load_messages(locale) for locale in STANDARD_LOCALES}
    expected_keys = set(messages["en"].keys())

    assert STANDARD_LOCALES == ("de", "en", "es", "zh-Hans", "ja", "ru")
    assert expected_keys
    for locale, locale_messages in messages.items():
        assert set(locale_messages.keys()) == expected_keys, locale
        for key, value in locale_messages.items():
            assert isinstance(value, str), f"{locale}:{key}"
            assert _format_fields(value) == _format_fields(messages["en"][key]), (
                locale,
                key,
            )


def test_locale_tags_normalize_to_bundled_catalogs() -> None:
    assert normalize_locale("de-CH") == "de"
    assert normalize_locale("es_MX") == "es"
    assert normalize_locale("ja-JP") == "ja"
    assert normalize_locale("zh-CN") == "zh-Hans"
    assert normalize_locale("ZH-hans") == "zh-Hans"
    assert normalize_locale("unknown") == "en"
    assert normalize_locale(None) == "en"
