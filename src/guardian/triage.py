"""Triage: validate the model's JSON, run an independent heuristic scam-signal
scan, and compute the worry level. Pure Python — fully unit-testable offline."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

# Canonical scam-signal taxonomy (PROJECT.md §5 step 3). Localized labels live
# in ui_text.SIGNAL_LABELS under the same ids.
SIGNAL_IDS = [
    "urgency",
    "gift_card_or_crypto",
    "wire_transfer",
    "credentials_request",
    "prize_too_good",
    "threat_or_arrest",
    "sender_mismatch",
    "unofficial_contact",
    "pressure_to_act",
    "lookalike_bill",
]

DOC_TYPES = [
    "utility_bill", "bank", "government_tax", "medical", "insurance",
    "subscription", "charity", "marketing", "suspected_scam", "personal", "other",
]


@dataclass
class ScamSignal:
    id: str
    evidence: str = ""


@dataclass
class Extraction:
    """Validated result of the vision pass."""
    is_document: bool = True
    readable: bool = True
    document_type: str = "other"
    sender: str | None = None
    what_they_want: str | None = None
    amount: str | None = None
    deadline: str | None = None
    requested_action: str | None = None
    scam_signals: list[ScamSignal] = field(default_factory=list)
    what_this_is: str = ""
    key_facts: list[str] = field(default_factory=list)
    worry_reasons: list[str] = field(default_factory=list)
    what_to_do: list[str] = field(default_factory=list)

    def facts_json(self) -> str:
        """Compact fact bundle for the optional 'full' config refinement pass."""
        return json.dumps(
            {
                "document_type": self.document_type,
                "sender": self.sender,
                "what_they_want": self.what_they_want,
                "amount": self.amount,
                "deadline": self.deadline,
                "requested_action": self.requested_action,
                "scam_signals": [
                    {"id": s.id, "evidence": s.evidence} for s in self.scam_signals
                ],
            },
            ensure_ascii=False,
        )


# --- Robust JSON parsing ------------------------------------------------------
_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.S)


def _first_json_object(text: str) -> str | None:
    """Return the first balanced {...} block, tolerating prose around it.

    If generation was cut off mid-object (small models do this), salvage by
    closing the open string and any unclosed brackets — partial facts beat an
    error card."""
    start = text.find("{")
    if start == -1:
        return None
    closers: list[str] = []
    in_string = False
    escaped = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        elif ch == '"':
            in_string = True
        elif ch == "{":
            closers.append("}")
        elif ch == "[":
            closers.append("]")
        elif ch in "}]":
            if closers and closers[-1] == ch:
                closers.pop()
            if not closers:
                return text[start : i + 1]
    salvaged = text[start:].rstrip()
    if in_string:
        salvaged += '"'
    salvaged = re.sub(r"[,:]\s*$", "", salvaged)
    return salvaged + "".join(reversed(closers))


def parse_model_json(raw: str) -> dict | None:
    """Parse model output into a dict; tolerate code fences and surrounding prose."""
    if not raw:
        return None
    fenced = _FENCE_RE.search(raw)
    if fenced:
        raw = fenced.group(1)
    block = _first_json_object(raw)
    if block is None:
        return None
    try:
        data = json.loads(block)
    except json.JSONDecodeError:
        # Common small-model slips: trailing commas, invalid escapes like \'
        repaired = re.sub(r",\s*([}\]])", r"\1", block)
        repaired = re.sub(r'\\([^"\\/bfnrtu])', r"\1", repaired)
        try:
            data = json.loads(repaired)
        except json.JSONDecodeError:
            # Last resort: json_repair fixes the long tail of LLM JSON slips
            # (stray punctuation between fields, missing commas, etc.).
            try:
                from json_repair import repair_json

                data = json.loads(repair_json(block))
            except Exception:
                return None
    return data if isinstance(data, dict) else None


# Small models sometimes parrot the prompt schema's field descriptions back
# as "facts" (seen live 2026-06-11: "who sent it", "money mentioned", …).
# Normalized full-string matches only — real letter facts never look like this.
_PROMPT_ECHOES = {
    "who sent it", "what they want", "what they want from you", "sender",
    "amount", "deadline", "money mentioned", "any money amount mentioned",
    "any date or deadline mentioned", "what to do", "key facts",
    "one short sentence", "what the letter asks the reader to do",
    "short quote or fact from the document", "up to 4 very short facts",
    "what this is", "worry reasons", "scam signals", "requested action",
}


def _is_prompt_echo(text: str) -> bool:
    return re.sub(r"[^\w\s]", "", text).strip().lower() in _PROMPT_ECHOES


def _as_str_list(value, limit: int) -> list[str]:
    if not isinstance(value, list):
        return []
    items = [str(v).strip() for v in value if str(v).strip()]
    return [v for v in items if not _is_prompt_echo(v)][:limit]


def validate_extraction(data: dict) -> Extraction:
    """Coerce the model's dict into a well-typed Extraction, dropping junk."""
    ex = Extraction()
    ex.is_document = bool(data.get("is_document", True))
    ex.readable = bool(data.get("readable", True))
    doc_type = str(data.get("document_type", "other") or "other").strip().lower()
    ex.document_type = doc_type if doc_type in DOC_TYPES else "other"
    for attr in ("sender", "what_they_want", "amount", "deadline", "requested_action"):
        value = data.get(attr)
        if value is not None and str(value).strip().lower() not in ("", "null", "none"):
            setattr(ex, attr, str(value).strip())
    for sig in data.get("scam_signals") or []:
        if isinstance(sig, dict) and sig.get("id") in SIGNAL_IDS:
            ex.scam_signals.append(
                ScamSignal(id=sig["id"], evidence=str(sig.get("evidence", "")).strip())
            )
    explanation = data.get("explanation") or {}
    if isinstance(explanation, str):
        # Model collapsed the explanation object into prose — keep what we can.
        ex.what_this_is = explanation.strip()
    elif isinstance(explanation, dict):
        ex.what_this_is = str(explanation.get("what_this_is", "") or "").strip()
        ex.key_facts = _as_str_list(explanation.get("key_facts"), 4)
        ex.worry_reasons = _as_str_list(explanation.get("worry_reasons"), 6)
        ex.what_to_do = _as_str_list(explanation.get("what_to_do"), 4)
    return ex


# --- Independent heuristic scan -----------------------------------------------
# Runs over everything the model extracted (sender, requested action, evidence
# quotes). A second pair of eyes that does not trust the model's own judgment.
_HEURISTICS: dict[str, re.Pattern[str]] = {
    "gift_card_or_crypto": re.compile(
        r"gift\s*card|itunes\s*card|google\s*play\s*card|steam\s*card|bitcoin|crypto|"
        r"\bbtc\b|\busdt\b|प्रीपेड\s*कार्ड|गिफ्ट\s*कार्ड|tarjeta\s+de\s+regalo|"
        r"ギフトカード|プリペイドカード", re.I),
    "wire_transfer": re.compile(
        r"wire\s+transfer|western\s*union|moneygram|money\s+transfer|untraceable|"
        r"transferencia\s+inmediata", re.I),
    "credentials_request": re.compile(
        r"\botp\b|one[- ]?time\s+pass(?:word|code)|password|\bpin\b|\bcvv\b|\bssn\b|"
        r"social\s+security|aadhaar|pan\s+number|contraseñ|पासवर्ड|"
        r"パスワード|暗証番号|ワンタイム", re.I),
    "urgency": re.compile(
        r"\burgent(?:ly)?\b|immediately|act\s+now|within\s+24\s+hours|final\s+notice|"
        r"last\s+chance|expires?\s+today|right\s+now|तुरंत|अंतिम\s+चेतावनी|"
        r"urgente|inmediatamente|último\s+aviso|"
        r"至急|直ちに|時間以内|最終通告", re.I),
    "threat_or_arrest": re.compile(
        r"\barrest(?:ed)?\b|lawsuit|legal\s+action|\bwarrant\b|prosecut|"
        r"account\s+(?:will\s+be\s+)?(?:closed|blocked|suspended|terminated)|"
        r"गिरफ़्तार|क़ानूनी\s+कार्रवाई|demanda\s+legal|arresto|"
        r"逮捕|口座.{0,4}(?:停止|凍結)|訴訟", re.I),
    "prize_too_good": re.compile(
        r"congratulations|you\s+(?:have\s+)?won|\bwinner\b|lottery|claim\s+your\s+prize|"
        r"free\s+gift|cash\s+prize|बधाई\s+हो|लॉटरी|इनाम|premio|lotería|ha\s+ganado", re.I),
}


def run_heuristics(text: str) -> list[ScamSignal]:
    signals = []
    for signal_id, pattern in _HEURISTICS.items():
        match = pattern.search(text)
        if match:
            signals.append(ScamSignal(id=signal_id, evidence=match.group(0)))
    return signals


def merge_signals(
    model_signals: list[ScamSignal], heuristic_signals: list[ScamSignal]
) -> list[ScamSignal]:
    """Union by signal id; the model's evidence (richer) wins on overlap."""
    merged: dict[str, ScamSignal] = {s.id: s for s in heuristic_signals}
    merged.update({s.id: s for s in model_signals})
    return [merged[sid] for sid in SIGNAL_IDS if sid in merged]


def worry_level(document_type: str, signals: list[ScamSignal]) -> str:
    """Map evidence to a worry level. NOTE: 'low' is still phrased as
    'looks normal, but verify' — there is no 'safe' level by design (§7)."""
    if document_type == "suspected_scam" or len(signals) >= 2:
        return "warning"
    if len(signals) == 1:
        return "caution"
    return "low"
