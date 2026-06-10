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

    what_html, worry_html, todo_html, speak_text, audio = app.on_analyze(object(), "English")
    assert "electricity bill" in what_html
    assert "card-low" in worry_html
    assert "never use the contact details" in todo_html
    assert speak_text and audio is None


def test_speak_callback_returns_audio():
    import app

    sr, wav = app.on_speak("Hello, this is a test.", "English")
    assert sr > 0 and len(wav) > 0


def test_language_change_localizes_ui():
    import app

    updates = app.on_language_change("हिन्दी (Hindi)")
    header_html = updates[0]
    assert "चिट्ठी" in header_html  # tagline localized
    assert len(updates) == 10
