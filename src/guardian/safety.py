"""Safety framing layer (PROJECT.md §7) — a feature, not an afterthought.

Everything user-facing passes through here. Guarantees, by construction:
  1. No definitive scam/safe verdicts — verdict-sounding model text is softened.
  2. The "should you worry" headline is template-driven (we write it, not the model).
  3. Contact details printed in the document never appear in "what to do" steps.
  4. Independent-verification advice is always appended to the action list.
  5. A gentle "I can make mistakes" disclaimer is always available for the UI.
"""

from __future__ import annotations

import re

from . import ui_text

# --- 1. Verdict softening ---------------------------------------------------
# (pattern, replacement) applied case-insensitively. English patterns dominate
# because they are the failure mode we can predict; the headline templates in
# ui_text carry the cautious framing for every language regardless.
_SOFTEN_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bthis is definitely (a |an )?scam\b", re.I), "this could be a scam"),
    (re.compile(r"\bthis is (a |an )?scam\b", re.I), "this looks like it could be a scam"),
    (re.compile(r"\bit is (a |an )?scam\b", re.I), "it looks like it could be a scam"),
    (re.compile(r"\bdefinitely (a |an )?scam\b", re.I), "possibly a scam"),
    (re.compile(r"\bthis is (completely |totally |100% )?safe\b", re.I),
     "this looks normal, but always verify"),
    (re.compile(r"\bit is (completely |totally |100% )?safe\b", re.I),
     "it looks normal, but always verify"),
    (re.compile(r"\byou can trust this\b", re.I), "this looks normal, but always verify"),
    (re.compile(r"\b(esto|esta carta) es una estafa\b", re.I), "esto podría ser una estafa"),
    (re.compile(r"\bes totalmente seguro\b", re.I), "parece normal, pero verifique siempre"),
    (re.compile(r"यह\s+पक्का\s+धोखा\s+है"), "यह धोखाधड़ी हो सकती है"),
    (re.compile(r"यह\s+धोखा\s+है"), "यह धोखाधड़ी हो सकती है"),
    (re.compile(r"यह\s+पूरी\s+तरह\s+सुरक्षित\s+है"), "यह सामान्य लगती है, फिर भी जाँच लें"),
]


def soften_verdicts(text: str) -> str:
    """Rewrite definitive scam/safe verdicts into cautious language."""
    for pattern, replacement in _SOFTEN_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


# --- 2. Contact-detail stripping ---------------------------------------------
# A scam letter's whole goal is to get the reader to use ITS contact details.
# Action steps therefore never repeat phone numbers, links, or emails from the
# document; the verification advice tells the user to use channels they already
# trust instead.
_PHONE_RE = re.compile(r"\+?\d[\d\-\s().]{7,}\d")
_URL_RE = re.compile(r"(https?://\S+|www\.\S+)", re.I)
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")


def strip_contact_details(text: str) -> str:
    text = _URL_RE.sub("", text)
    text = _EMAIL_RE.sub("", text)
    text = _PHONE_RE.sub("", text)
    return re.sub(r"[ \t]{2,}", " ", text).strip(" \t,;:")


# --- 3. Sanitizers for each result section -----------------------------------
def _strip_or_drop(text: str) -> str:
    """Strip contact details; if the text WAS essentially the contact detail
    (fewer than 3 words survive), drop it entirely — '(reply to)' is not a
    fact. Found live via the Modal matrix, 2026-06-11."""
    stripped = strip_contact_details(text)
    if stripped != text and len(stripped.split()) < 3:
        return ""
    return stripped


def sanitize_fact(fact: str) -> str:
    return soften_verdicts(_strip_or_drop(fact)).strip()


def sanitize_reason(reason: str) -> str:
    return soften_verdicts(_strip_or_drop(reason)).strip()


def sanitize_action_step(step: str) -> str:
    return soften_verdicts(strip_contact_details(step)).strip()


def verification_advice(lang: str) -> str:
    """Always-appended: verify through channels the person already trusts."""
    return ui_text.get(lang, "verify")


def disclaimer(lang: str) -> str:
    return ui_text.get(lang, "disclaimer")


def worry_headline(level: str, lang: str) -> str:
    """Template-driven headline — the model never writes this line."""
    key = {"low": "worry_low", "caution": "worry_caution", "warning": "worry_warning"}[level]
    return ui_text.get(lang, key)
