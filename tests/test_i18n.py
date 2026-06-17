from llm_note.i18n import STANDARD_LOCALES, load_messages


def test_standard_locales_are_complete() -> None:
    messages = {locale: load_messages(locale) for locale in STANDARD_LOCALES}
    expected_keys = set(messages["en"].keys())

    assert STANDARD_LOCALES == ("de", "en", "es", "zh-Hans", "ja", "ru")
    assert expected_keys
    for locale, locale_messages in messages.items():
        assert set(locale_messages.keys()) == expected_keys, locale
