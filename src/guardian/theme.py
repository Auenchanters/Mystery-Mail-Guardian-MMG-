"""Design tokens + Gradio theme for the "Kitchen-Table Post Office" look.

DARK-FIRST (owner decision 2026-06-11): the dark palette is the default and is
applied to BOTH the base and `_dark` Gradio theme slots, so the app renders the
same warm "midnight study desk" look regardless of the visitor's system theme.
The light palette is kept (and contrast-tested) for a possible future toggle.

Every fg/bg pair is enforced against WCAG AA by tests/test_theme.py.
"""

from __future__ import annotations

TOKENS = {
    "dark": {  # DEFAULT — midnight study desk
        "paper": "#1E1B16",       # page background
        "sheet": "#2A2620",       # letter-sheet cards
        "ink": "#EDE6D6",         # body text
        "ink_soft": "#B8AE9C",    # secondary text
        "postal_red": "#E07A5F",  # primary actions, stamp accents
        "postal_blue": "#8EB1D9", # links, secondary accents, postmarks
        "seal_green": "#7BC88A",  # privacy seal, low-worry stamp
        "amber": "#E8B339",       # caution stamp
        "alert_red": "#F08A80",   # warning stamp
        "line": "#3E382E",        # borders, deckle edges
    },
    "light": {  # kept for a future light toggle; equally AA-tested
        "paper": "#FAF4E8",
        "sheet": "#FFFDF7",
        "ink": "#2B2A33",
        "ink_soft": "#5A5550",
        "postal_red": "#C84B31",
        "postal_blue": "#3D5A80",
        "seal_green": "#3A7D44",
        "amber": "#B97700",
        "alert_red": "#B3362B",
        "line": "#E4D9C3",
    },
}


def _luminance(hex_color: str) -> float:
    rgb = [int(hex_color.lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast_ratio(fg: str, bg: str) -> float:
    """WCAG 2.x contrast ratio between two #RRGGBB colors."""
    l1, l2 = sorted((_luminance(fg), _luminance(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def css_variables() -> str:
    """The :root block injected ahead of guardian.css (single source of truth)."""
    t = TOKENS["dark"]
    pairs = "".join(f"--{k.replace('_', '-')}:{v};" for k, v in t.items())
    return ":root{" + pairs + "}"


def build_theme():
    """Gradio theme with the postal palette forced dark in both theme slots."""
    import gradio as gr

    t = TOKENS["dark"]
    theme = gr.themes.Base(
        primary_hue=gr.themes.Color(  # postal-red ramp, c500 = light token
            c50="#FBEDE8", c100="#F6D8CE", c200="#EEB3A2", c300="#E38D75",
            c400="#D66A50", c500="#C84B31", c600="#B04129", c700="#933622",
            c800="#752B1B", c900="#582014", c950="#3A150D",
        ),
        neutral_hue=gr.themes.Color(  # warm paper-brown neutrals
            c50="#FAF4E8", c100="#F0E7D4", c200="#DDD1B8", c300="#C4B69A",
            c400="#A6967B", c500="#857762", c600="#675C4B", c700="#4C4438",
            c800="#352F27", c900="#26211B", c950="#1E1B16",
        ),
        font=[
            '"Atkinson Hyperlegible"', '"Noto Sans Devanagari"',
            '"Hiragino Sans"', '"Yu Gothic UI"', '"Meiryo"',
            "system-ui", "sans-serif",
        ],
        text_size=gr.themes.sizes.text_lg,
        radius_size=gr.themes.sizes.radius_md,
    )
    forced = {
        "body_background_fill": t["paper"],
        "block_background_fill": t["sheet"],
        "block_border_color": t["line"],
        "body_text_color": t["ink"],
        "body_text_color_subdued": t["ink_soft"],
        "input_background_fill": t["paper"],
        "button_primary_background_fill": t["postal_red"],
        "button_primary_text_color": "#1E1B16",
        "button_secondary_background_fill": t["sheet"],
        "button_secondary_text_color": t["postal_blue"],
        "button_large_text_size": "22px",
        "button_large_padding": "18px 24px",
        "block_shadow": "0 2px 8px rgba(0,0,0,.25)",
    }
    # Force dark: assign the same values to base AND `_dark` slots (only color
    # properties have `_dark` variants; sizes/paddings do not).
    both = dict(forced)
    for key, value in forced.items():
        if hasattr(theme, f"{key}_dark"):
            both[f"{key}_dark"] = value
    return theme.set(**both)
