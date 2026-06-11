"""Localization completeness: every key in every language, every label localized."""

from guardian import triage, ui_text

LANGS = ("en", "hi", "es", "ja")


def test_all_required_languages_present():
    for lang in LANGS:
        assert lang in ui_text.STRINGS, f"missing language dict: {lang}"


def test_all_languages_have_all_keys():
    english_keys = set(ui_text.STRINGS["en"])
    for lang, strings in ui_text.STRINGS.items():
        assert set(strings) == english_keys, f"{lang} keys mismatch"


def test_every_signal_id_labeled_in_every_language():
    for signal_id in triage.SIGNAL_IDS:
        assert signal_id in ui_text.SIGNAL_LABELS, f"missing labels for {signal_id}"
        for lang in LANGS:
            assert ui_text.SIGNAL_LABELS[signal_id][lang].strip()


def test_every_doc_type_labeled_in_every_language():
    for doc_type in triage.DOC_TYPES:
        assert doc_type in ui_text.DOC_TYPE_LABELS, f"missing labels for {doc_type}"
        for lang in LANGS:
            assert ui_text.DOC_TYPE_LABELS[doc_type][lang].strip()


def test_no_empty_strings():
    for lang, strings in ui_text.STRINGS.items():
        for key, value in strings.items():
            assert value.strip(), f"{lang}.{key} is empty"


def test_fallback_to_english():
    assert ui_text.get("fr", "privacy") == ui_text.STRINGS["en"]["privacy"]
    assert ui_text.signal_label("urgency", "fr") == ui_text.SIGNAL_LABELS["urgency"]["en"]


def test_worry_headlines_cautious_no_verdicts():
    banned = ("is a scam", "is safe", "100%", "definitely")
    for lang in ui_text.STRINGS:
        for key in ("worry_low", "worry_caution", "worry_warning"):
            text = ui_text.get(lang, key).lower()
            assert not any(b in text for b in banned), f"{lang}.{key} sounds like a verdict"
