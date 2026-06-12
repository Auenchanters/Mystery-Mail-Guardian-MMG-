"""Letter forge: parameterized synthetic letters WITH gold labels.

Dev/training tooling (never imported by the runtime app). One forge feeds:
  - scripts/make_dataset.py  -> eval/SFT datasets (images + labels.jsonl)
  - modal_eval.py            -> extraction-accuracy + token-efficiency eval
Gold worry levels are derived through guardian.triage itself, so the labels
can never drift from the product's own rules.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from . import triage

COMPANIES = ["City Power Company", "Metro Water Works", "SunGrid Energy",
             "Northside Gas Co-op", "Lakeland Electric"]
BANKS = ["First Harbor Bank", "Union Crest Bank", "Meridian Savings"]
CHARITIES = ["Helping Hands Fund", "River Valley Food Bank", "Bright Futures Trust"]
CLINICS = ["Oakwood Family Clinic", "Dr. Patel's Office", "Hillside Dental"]
SCAM_BUREAUS = ["TAX ENFORCEMENT BUREAU", "FEDERAL PENALTY OFFICE",
                "NATIONAL DEBT RECOVERY UNIT"]
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


@dataclass
class GoldLetter:
    name: str                      # factory name, for per-type metrics
    lines: list[str]
    document_type: str
    sender: str
    amount: str | None = None
    deadline: str | None = None
    signal_ids: list[str] = field(default_factory=list)
    expected_level: str = "low"    # derived in __post_init__
    acceptable_levels: tuple[str, ...] = ()
    font_names: tuple[str, ...] = ()  # script-capable fonts for non-Latin text
    font_size: int = 34               # CJK needs smaller to fit the page width

    def __post_init__(self):
        signals = [triage.ScamSignal(id=s) for s in self.signal_ids]
        self.expected_level = triage.worry_level(self.document_type, signals)
        if not self.acceptable_levels:
            self.acceptable_levels = (self.expected_level,)


def _amount(rng: random.Random, lo: int = 20, hi: int = 600) -> str:
    return f"${rng.randint(lo, hi)}.{rng.randint(0, 99):02d}"


def _date(rng: random.Random) -> str:
    return f"{rng.choice(MONTHS)} {rng.randint(1, 28)}, 2026"


def _acct(rng: random.Random) -> str:
    return f"{rng.randint(1000, 9999)}-{rng.randint(100, 999)}"


# --- Factories (each returns a GoldLetter) ----------------------------------
def utility_bill(rng: random.Random) -> GoldLetter:
    co, amt, due = rng.choice(COMPANIES), _amount(rng), _date(rng)
    return GoldLetter(
        name="utility_bill", document_type="utility_bill", sender=co,
        amount=amt, deadline=due,
        lines=[co.upper(), f"Bill for account {_acct(rng)}",
               f"Amount due: {amt}", f"Due date: {due}",
               "Pay online, by mail, or at any branch.",
               "Questions? See the number on your account card."],
    )


def bank_notice(rng: random.Random) -> GoldLetter:
    bank = rng.choice(BANKS)
    return GoldLetter(
        name="bank_notice", document_type="bank", sender=bank,
        lines=[bank.upper(), "Your quarterly statement is ready.",
               f"Account ending {rng.randint(1000, 9999)}.",
               "View it in your usual online banking,",
               "or visit your local branch.",
               "No action is required."],
    )


def medical_reminder(rng: random.Random) -> GoldLetter:
    clinic, when = rng.choice(CLINICS), _date(rng)
    return GoldLetter(
        name="medical_reminder", document_type="medical", sender=clinic,
        deadline=when,
        lines=[clinic.upper(), "Appointment reminder.",
               f"You are scheduled on {when} at {rng.randint(8, 16)}:00.",
               "Please bring your insurance card.",
               "Call the number on your appointment card to reschedule."],
    )


def charity_request(rng: random.Random) -> GoldLetter:
    org = rng.choice(CHARITIES)
    return GoldLetter(
        name="charity_request", document_type="charity", sender=org,
        lines=[org.upper(), "Our winter appeal is here.",
               "Any gift helps a neighbor in need.",
               "Donations are voluntary and tax-deductible.",
               "Thank you for your past support."],
    )


def gift_card_scam(rng: random.Random) -> GoldLetter:
    bureau, amt = rng.choice(SCAM_BUREAUS), _amount(rng, 300, 900)
    return GoldLetter(
        name="gift_card_scam", document_type="suspected_scam", sender=bureau,
        amount=amt,
        signal_ids=["urgency", "gift_card_or_crypto", "threat_or_arrest"],
        lines=[f"{bureau} — FINAL NOTICE",
               f"You owe a penalty of {amt}.",
               f"Pay WITHIN {rng.choice([24, 48])} HOURS or you will be ARRESTED.",
               f"Pay ONLY with {rng.choice(['Google Play', 'iTunes', 'Steam'])} gift cards.",
               "Call 1-800-555-0199 immediately with the codes.",
               "Do not contact your bank or the tax office."],
    )


def lottery_scam(rng: random.Random) -> GoldLetter:
    prize = f"${rng.randint(1, 9)},{rng.randint(100, 999)},000"
    return GoldLetter(
        name="lottery_scam", document_type="suspected_scam",
        sender="International Prize Committee", amount=prize,
        signal_ids=["prize_too_good", "wire_transfer", "urgency"],
        lines=["INTERNATIONAL PRIZE COMMITTEE",
               f"CONGRATULATIONS! You have WON {prize}",
               "in a lottery you never entered.",
               f"Send a processing fee of {_amount(rng, 100, 400)}",
               f"by wire transfer within {rng.choice([24, 48])} hours.",
               "Reply only to: claims@prize-winner-intl.example"],
    )


def phishing_account(rng: random.Random) -> GoldLetter:
    bank = rng.choice(BANKS)
    return GoldLetter(
        name="phishing_account", document_type="suspected_scam", sender=bank,
        signal_ids=["credentials_request", "threat_or_arrest", "urgency"],
        lines=[f"{bank.upper()} SECURITY ALERT",
               "Your account will be SUSPENDED today.",
               "To keep access you must verify your password",
               "and one-time passcode immediately at",
               "www.account-verify-secure.example",
               "Do not visit a branch — online verification only."],
    )


def lookalike_ad(rng: random.Random) -> GoldLetter:
    amt = _amount(rng, 80, 300)
    return GoldLetter(
        name="lookalike_ad", document_type="marketing",
        sender="Home Warranty Center", amount=amt,
        signal_ids=["lookalike_bill"],
        acceptable_levels=("caution", "warning"),
        lines=["HOME WARRANTY CENTER — FINAL NOTICE*",
               f"Your home warranty 'invoice': {amt}",
               "This looks like a bill but is a SOLICITATION.",
               "*Not affiliated with your mortgage lender.",
               f"Respond by {_date(rng)} to lock your rate."],
    )


# --- Non-Latin letter text (OCR coverage; rendered with Windows system fonts)
_HI_FONTS = ("Nirmala.ttc", "mangal.ttf", "NotoSansDevanagari-Regular.ttf")
_JA_FONTS = ("YuGothM.ttc", "YuGothR.ttc", "msgothic.ttc", "meiryo.ttc")


def hi_utility_bill(rng: random.Random) -> GoldLetter:
    due = f"{rng.randint(1, 28)} जून 2026"
    amt = f"₹{rng.randint(800, 4000)}"
    return GoldLetter(
        name="hi_utility_bill", document_type="utility_bill",
        sender="सिटी पावर कंपनी", amount=amt, deadline=due, font_names=_HI_FONTS,
        lines=["सिटी पावर कंपनी", f"बिजली का बिल — खाता {_acct(rng)}",
               f"देय राशि: {amt}", f"आख़िरी तारीख़: {due}",
               "ऑनलाइन या किसी भी शाखा में भुगतान करें।"],
    )


def hi_gift_card_scam(rng: random.Random) -> GoldLetter:
    amt = f"₹{rng.randint(20, 90)},000"
    return GoldLetter(
        name="hi_gift_card_scam", document_type="suspected_scam",
        sender="कर प्रवर्तन ब्यूरो", amount=amt, font_names=_HI_FONTS,
        signal_ids=["urgency", "gift_card_or_crypto", "threat_or_arrest"],
        lines=["कर प्रवर्तन ब्यूरो — अंतिम चेतावनी",
               f"आप पर {amt} का जुर्माना बकाया है।",
               "24 घंटे के भीतर भुगतान करें वरना गिरफ़्तारी होगी।",
               "केवल गिफ्ट कार्ड से भुगतान करें।",
               "तुरंत 1-800-555-0199 पर कोड बताएं।",
               "अपने बैंक से संपर्क न करें।"],
    )


def ja_utility_bill(rng: random.Random) -> GoldLetter:
    amt = f"{rng.randint(4, 12)},{rng.randint(100, 999)}円"
    due = f"2026年6月{rng.randint(1, 28)}日"
    return GoldLetter(
        name="ja_utility_bill", document_type="utility_bill",
        sender="シティ電力株式会社", amount=amt, deadline=due,
        font_names=_JA_FONTS, font_size=28,
        lines=["シティ電力株式会社", f"電気料金のご請求 — お客様番号 {_acct(rng)}",
               f"ご請求額: {amt}", f"お支払い期限: {due}",
               "コンビニ、銀行、またはオンラインでお支払いください。"],
    )


def ja_gift_card_scam(rng: random.Random) -> GoldLetter:
    amt = f"{rng.randint(2, 9)}0,000円"
    return GoldLetter(
        name="ja_gift_card_scam", document_type="suspected_scam",
        sender="税務執行局", amount=amt, font_names=_JA_FONTS, font_size=28,
        signal_ids=["urgency", "gift_card_or_crypto", "threat_or_arrest"],
        lines=["税務執行局 — 最終通告",
               f"罰金 {amt}が未納です。",
               "24時間以内に支払わなければ逮捕されます。",
               "支払いはギフトカードのみ。",
               "至急 1-800-555-0199 に電話してコードを伝えてください。",
               "銀行や税務署には連絡しないでください。"],
    )


FACTORIES = [utility_bill, bank_notice, medical_reminder, charity_request,
             gift_card_scam, lottery_scam, phishing_account, lookalike_ad,
             hi_utility_bill, hi_gift_card_scam, ja_utility_bill, ja_gift_card_scam]

DEGRADATIONS = ("clean", "clean", "clean", "blur", "dim", "rotate")  # 50/50-ish weighting


def forge(rng: random.Random) -> GoldLetter:
    return rng.choice(FACTORIES)(rng)


def render_gold(gold: GoldLetter, rng: random.Random, degrade: bool = True):
    """Letter image, optionally degraded like a casual elder phone photo."""
    from PIL import ImageEnhance, ImageFilter

    from .samples import _DEFAULT_FONTS, render_letter

    img = render_letter(gold.lines, font_size=gold.font_size,
                        font_names=gold.font_names or _DEFAULT_FONTS)
    kind = rng.choice(DEGRADATIONS) if degrade else "clean"
    if kind == "blur":
        img = img.filter(ImageFilter.GaussianBlur(rng.uniform(1.0, 2.2)))
    elif kind == "dim":
        img = ImageEnhance.Brightness(img).enhance(rng.uniform(0.4, 0.7))
    elif kind == "rotate":
        img = img.rotate(rng.uniform(-6, 6), expand=True, fillcolor="white")
    return img, kind


# --- Graded degradations (robustness eval v2: find the honest breaking point)
def degrade_graded(img, kind: str, level: int):
    """Apply degradation `kind` at intensity level 1..3 (3 = harshest)."""
    import random as _random

    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

    if kind == "blur":
        return img.filter(ImageFilter.GaussianBlur((1.5, 3.0, 4.5)[level - 1]))
    if kind == "dim":
        return ImageEnhance.Brightness(img).enhance((0.5, 0.3, 0.15)[level - 1])
    if kind == "rotate":
        return img.rotate((10, 20, 35)[level - 1], expand=True, fillcolor="white")
    if kind == "perspective":  # phone held at an angle
        w, h = img.size
        j = (0.04, 0.09, 0.16)[level - 1]
        rng = _random.Random(level)
        quad = [rng.uniform(0, j) * w, rng.uniform(0, j) * h,
                rng.uniform(0, j) * w, h - rng.uniform(0, j) * h,
                w - rng.uniform(0, j) * w, h - rng.uniform(0, j) * h,
                w - rng.uniform(0, j) * w, rng.uniform(0, j) * h]
        return img.transform((w, h), Image.QUAD, quad, fillcolor="white")
    if kind == "shadow":  # hard shadow band across the page
        overlay = Image.new("L", img.size, 255)
        draw = ImageDraw.Draw(overlay)
        w, h = img.size
        band = (h // 4, h // 3, h // 2)[level - 1]
        opacity = (190, 150, 110)[level - 1]
        draw.rectangle([0, h // 3, w, h // 3 + band], fill=opacity)
        return Image.composite(img, Image.new("RGB", img.size, "black"),
                               overlay.point(lambda p: p))
    if kind == "noise":  # sensor grain / crumple texture
        import numpy as np

        arr = np.asarray(img).astype("int16")
        sigma = (12, 28, 48)[level - 1]
        rng = np.random.default_rng(level)
        noisy = arr + rng.normal(0, sigma, arr.shape)
        return Image.fromarray(noisy.clip(0, 255).astype("uint8"))
    raise ValueError(kind)


def sft_target(gold: GoldLetter) -> dict:
    """Gold JSON in the exact schema the analysis prompt demands — usable as
    the assistant target for supervised fine-tuning (English explanations,
    deterministic, production-shaped)."""
    from . import ui_text

    signals = [{"id": s, "evidence": ""} for s in gold.signal_ids]
    facts = [f"From: {gold.sender}"]
    if gold.amount:
        facts.append(f"Amount: {gold.amount}")
    if gold.deadline:
        facts.append(f"Deadline: {gold.deadline}")
    label = ui_text.doc_type_label(gold.document_type, "en")
    reasons = [ui_text.signal_label(s, "en") for s in gold.signal_ids]
    steps = (["Do not pay or reply using anything printed in this letter.",
              "Show this letter to someone you trust."]
             if gold.signal_ids else
             ["Check that the name on the letter is yours.",
              "If you need to act, use the contact you already know and trust."])
    return {
        "is_document": True, "readable": True,
        "document_type": gold.document_type,
        "sender": gold.sender,
        "what_they_want": None,
        "amount": gold.amount, "deadline": gold.deadline,
        "requested_action": None,
        "scam_signals": signals,
        "explanation": {
            "what_this_is": f"This looks like {label}.",
            "key_facts": facts,
            "worry_reasons": reasons,
            "what_to_do": steps,
        },
    }
