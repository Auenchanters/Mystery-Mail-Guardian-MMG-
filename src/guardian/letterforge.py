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


FACTORIES = [utility_bill, bank_notice, medical_reminder, charity_request,
             gift_card_scam, lottery_scam, phishing_account, lookalike_ad]

DEGRADATIONS = ("clean", "clean", "clean", "blur", "dim", "rotate")  # 50/50-ish weighting


def forge(rng: random.Random) -> GoldLetter:
    return rng.choice(FACTORIES)(rng)


def render_gold(gold: GoldLetter, rng: random.Random, degrade: bool = True):
    """Letter image, optionally degraded like a casual elder phone photo."""
    from PIL import ImageEnhance, ImageFilter

    from .samples import render_letter

    img = render_letter(gold.lines)
    kind = rng.choice(DEGRADATIONS) if degrade else "clean"
    if kind == "blur":
        img = img.filter(ImageFilter.GaussianBlur(rng.uniform(1.0, 2.2)))
    elif kind == "dim":
        img = ImageEnhance.Brightness(img).enhance(rng.uniform(0.4, 0.7))
    elif kind == "rotate":
        img = img.rotate(rng.uniform(-6, 6), expand=True, fillcolor="white")
    return img, kind


def sft_target(gold: GoldLetter) -> dict:
    """Gold JSON in the exact schema the analysis prompt demands — usable as
    the assistant target for supervised fine-tuning."""
    signals = [{"id": s, "evidence": ""} for s in gold.signal_ids]
    return {
        "is_document": True, "readable": True,
        "document_type": gold.document_type,
        "sender": gold.sender,
        "what_they_want": None,
        "amount": gold.amount, "deadline": gold.deadline,
        "requested_action": None,
        "scam_signals": signals,
        "explanation": {
            "what_this_is": "", "key_facts": [],
            "worry_reasons": [], "what_to_do": [],
        },
    }
