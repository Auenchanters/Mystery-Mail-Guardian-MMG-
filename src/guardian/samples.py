"""Synthetic sample letters — single source shared by modal_validate.py,
scripts/make_samples.py (gr.Examples PNGs), and any future checks.

Letters are fictional. The scam letter uses a reserved-for-fiction phone
number (555-0199) so no real number is ever shown or spoken.
"""

from __future__ import annotations

NORMAL_BILL = [
    "CITY POWER COMPANY",
    "Electricity bill — Account 4471-220",
    "Billing period: May 2026",
    "Amount due: $84.20",
    "Due date: June 28, 2026",
    "Pay online, by mail, or at any branch.",
    "Questions? See the number on your account card.",
]

SCAM_LETTER = [
    "TAX ENFORCEMENT BUREAU — FINAL NOTICE",
    "You owe a penalty of $500.",
    "You must pay WITHIN 24 HOURS or you will be",
    "ARRESTED. Pay ONLY with Google Play gift cards.",
    "Call 1-800-555-0199 immediately with the codes.",
    "Do not contact your bank or the tax office.",
]

LOTTERY_LETTER = [
    "INTERNATIONAL PRIZE COMMITTEE",
    "CONGRATULATIONS! You have WON $2,500,000",
    "in the Global Email Lottery you never entered.",
    "To claim your prize, send a processing fee of $250",
    "by wire transfer within 48 hours.",
    "Reply only to: claims@prize-winner-intl.example",
]

# Reconstruction of a real-world letter that exposed the prompt-echo bug
# (owner report, 2026-06-11) — kept as a permanent regression case.
LAND_LETTER = [
    "MAAS PLUS DESIGN ENGINEERING",
    "Plot 572 AA1 Extension New Layout Pasali Kuje FCT Abuja",
    "Attention: TO WHOM IT MAY CONCERN",
    "LETTER OF LAND AUTHENTICATION",
    "We write on behalf of our company who intend to liase with",
    "the buyer and the seller of a property with plot No:",
    "IJA/F06/3027, Kubuwa Abuja FCT, measuring approx 10.1 Ha.",
    "The said land is authentic and correct, as stipulated in",
    "the survey plan. The owner undertakes to sell the said plot",
    "of Land at the sum of N400,000,000.00 (Four Hundred",
    "Million Naira) only.",
    "We humbly crave that you will give details commitment to",
    "search and cooperate with our company for the acquisition",
    "of the said land in due time.",
    "Abiodun Andrew Sunday, CEO",
]


def _font(size: int):
    from PIL import ImageFont

    for name in ("arial.ttf", "DejaVuSans.ttf"):  # Windows dev box / Linux image
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_letter(lines: list[str], size: tuple[int, int] = (900, 1100),
                  font_size: int = 34):
    """Render text as a letter-like photo (white page, black print)."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(img)
    font = _font(font_size)
    y = 80
    for line in lines:
        draw.text((70, y), line, fill="black", font=font)
        y += 60
    return img
