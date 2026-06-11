"""The palette is test-driven: every text/background pair must clear WCAG AA.
If a pretty color fails here, the color changes — not the test."""

from guardian.theme import TOKENS, contrast_ratio

AA_PAIRS = [  # (foreground, background, minimum ratio)
    ("ink", "paper", 4.5),
    ("ink", "sheet", 4.5),
    ("ink_soft", "sheet", 4.5),
    ("postal_red", "paper", 3.0),   # large text / UI components
    ("postal_blue", "paper", 3.0),
    ("seal_green", "sheet", 3.0),
    ("amber", "sheet", 3.0),
    ("alert_red", "sheet", 3.0),
]


def test_dark_palette_meets_wcag_aa():  # dark is the DEFAULT palette
    for fg, bg, minimum in AA_PAIRS:
        ratio = contrast_ratio(TOKENS["dark"][fg], TOKENS["dark"][bg])
        assert ratio >= minimum, f"dark {fg} on {bg}: {ratio:.2f} < {minimum}"


def test_light_palette_meets_wcag_aa():
    for fg, bg, minimum in AA_PAIRS:
        ratio = contrast_ratio(TOKENS["light"][fg], TOKENS["light"][bg])
        assert ratio >= minimum, f"light {fg} on {bg}: {ratio:.2f} < {minimum}"


def test_contrast_math_sanity():
    assert abs(contrast_ratio("#FFFFFF", "#000000") - 21.0) < 0.01
    assert abs(contrast_ratio("#777777", "#777777") - 1.0) < 0.01


def test_both_palettes_have_same_token_names():
    assert set(TOKENS["dark"]) == set(TOKENS["light"])
