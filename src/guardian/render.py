"""Render an AnalysisResult into the three HTML result cards.

All model-derived text is HTML-escaped here — the model can never inject
markup into the page. Styling hooks (classes) are defined in app.py's CSS.
"""

from __future__ import annotations

import html

from . import ui_text
from .pipeline import AnalysisResult


def _card(css_class: str, heading: str, body_html: str) -> str:
    return (
        f'<div class="guardian-card {css_class}">'
        f"<h2>{html.escape(heading)}</h2>{body_html}</div>"
    )


def _bullets(items: list[str]) -> str:
    if not items:
        return ""
    lis = "".join(f"<li>{html.escape(i)}</li>" for i in items)
    return f"<ul>{lis}</ul>"


def render_result(result: AnalysisResult) -> tuple[str, str, str]:
    """-> (what_html, worry_html, todo_html)."""
    lang = result.lang
    if not result.ok:
        message = f"<p>{html.escape(result.error)}</p>"
        return (
            _card("card-neutral", ui_text.get(lang, "section_what"), message),
            "",
            "",
        )

    what_html = _card(
        "card-neutral",
        ui_text.get(lang, "section_what"),
        f"<p>{html.escape(result.what_this_is)}</p>{_bullets(result.key_facts)}",
    )
    worry_class = {
        "low": "card-low",
        "caution": "card-caution",
        "warning": "card-warning",
    }[result.worry_level]
    worry_html = _card(
        worry_class,
        ui_text.get(lang, "section_worry"),
        f"<p><strong>{html.escape(result.worry_headline)}</strong></p>"
        + _bullets(result.worry_reasons),
    )
    todo_html = _card(
        "card-todo",
        ui_text.get(lang, "section_todo"),
        _bullets(result.actions),
    )
    return what_html, worry_html, todo_html


def render_placeholder(lang: str) -> tuple[str, str, str]:
    return (
        _card("card-neutral", ui_text.get(lang, "section_what"),
              f"<p>{html.escape(ui_text.get(lang, 'waiting'))}</p>"),
        "",
        "",
    )
