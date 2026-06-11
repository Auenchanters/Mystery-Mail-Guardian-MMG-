"""Render an AnalysisResult into the three HTML result cards.

All model-derived text is HTML-escaped here — the model can never inject
markup into the page. Styling hooks (classes) are defined in app.py's CSS.
"""

from __future__ import annotations

import html

from . import ui_text
from .pipeline import AnalysisResult


def _card(css_class: str, heading: str, body_html: str, prefix: str = "") -> str:
    return (
        f'<div class="guardian-card {css_class}">{prefix}'
        f"<h2>{html.escape(heading)}</h2>{body_html}</div>"
    )


# Postage-stamp verdict icons — inline SVG, hand-drawn feel, no external assets.
_STAMP_ICONS = {
    "low": (  # check inside a postmark ring
        '<svg viewBox="0 0 48 48" aria-hidden="true" focusable="false" fill="none">'
        '<circle cx="24" cy="24" r="19" stroke="currentColor" stroke-width="3"/>'
        '<path d="M15 24.5l6.2 6L33 18" stroke="currentColor" stroke-width="4"'
        ' stroke-linecap="round" stroke-linejoin="round"/></svg>'
    ),
    "caution": (  # gently tilted warning triangle
        '<svg viewBox="0 0 48 48" aria-hidden="true" focusable="false" fill="none">'
        '<g transform="rotate(-4 24 24)">'
        '<path d="M24 7L43 40H5z" stroke="currentColor" stroke-width="3"'
        ' stroke-linejoin="round"/>'
        '<path d="M24 19v9" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>'
        '<circle cx="24" cy="34" r="2.4" fill="currentColor"/></g></svg>'
    ),
    "warning": (  # exclamation octagon
        '<svg viewBox="0 0 48 48" aria-hidden="true" focusable="false" fill="none">'
        '<path d="M16 5h16l11 11v16L32 43H16L5 32V16z" stroke="currentColor"'
        ' stroke-width="3" stroke-linejoin="round"/>'
        '<path d="M24 14v12" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>'
        '<circle cx="24" cy="33" r="2.6" fill="currentColor"/></svg>'
    ),
}


def _stamp(level: str) -> str:
    icon = _STAMP_ICONS.get(level, _STAMP_ICONS["low"])
    return f'<div class="stamp stamp-{level}" aria-hidden="true">{icon}</div>'


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
        prefix=_stamp(result.worry_level),
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
