"""Smoke test: the Gradio app builds in mock mode (no model weights)."""

import importlib
import os
import sys


def test_app_builds_in_mock_mode():
    os.environ["GUARDIAN_MOCK"] = "1"
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root)
    app = importlib.import_module("app")
    assert app.demo is not None
    assert app.config.MOCK is True


def test_analyze_callback_roundtrip():
    import app

    what_html, worry_html, todo_html, speak_text, audio, audio_group = app.on_analyze(
        object(), "English"
    )
    assert "electricity bill" in what_html
    assert "card-low" in worry_html
    assert "never use the contact details" in todo_html
    assert speak_text and audio is None
    assert audio_group.constructor_args["visible"] is False


def test_speak_callback_returns_audio():
    import app

    (sr, wav), audio_group = app.on_speak("Hello, this is a test.", "English")
    assert sr > 0 and len(wav) > 0
    assert audio_group.constructor_args["visible"] is True


def test_language_control_is_segmented_radio():
    import app
    import gradio as gr

    assert isinstance(app.language, gr.Radio)
    assert app.language.elem_id == "language-seg"
    assert len(app.language.choices) == 4


def test_language_change_localizes_ui():
    import app

    updates = app.on_language_change("हिन्दी (Hindi)")
    header_html = updates[0]
    assert "चिट्ठी" in header_html  # tagline localized
    assert len(updates) == 11  # + hidden audio group


def test_language_change_japanese_roundtrip():
    import app

    updates = app.on_language_change("日本語 (Japanese)")
    assert "手紙" in updates[0]  # tagline localized
    what_html, worry_html, todo_html, speak_text, audio, audio_group = app.on_analyze(
        object(), "日本語 (Japanese)"
    )
    assert "電気料金" in what_html
    assert "card-low" in worry_html
    assert "連絡先は使わないで" in todo_html
