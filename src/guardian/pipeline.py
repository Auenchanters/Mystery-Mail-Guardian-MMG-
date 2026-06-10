"""Pipeline orchestration: extract -> triage -> explain -> (speak on demand).

Returns an AnalysisResult whose every text field has already passed through the
safety layer. The UI only renders; it never composes safety-relevant wording.
"""

from __future__ import annotations

import traceback
from dataclasses import dataclass, field

from . import config, explain, extract, prompts, safety, triage, ui_text


@dataclass
class AnalysisResult:
    ok: bool = False
    error: str = ""                      # localized, user-friendly
    lang: str = "en"
    document_type: str = "other"
    what_this_is: str = ""
    key_facts: list[str] = field(default_factory=list)
    worry_level: str = "low"             # low | caution | warning
    worry_headline: str = ""
    worry_reasons: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    speak_text: str = ""


def _error(lang: str, key: str) -> AnalysisResult:
    return AnalysisResult(ok=False, lang=lang, error=ui_text.get(lang, key))


def _ensure_explanation(ex: triage.Extraction, lang: str) -> None:
    """If the model's explanation is missing or collapsed, synthesize a plain
    one deterministically from the extracted facts — never show an empty card."""
    if not ex.what_this_is:
        label = ui_text.doc_type_label(ex.document_type, lang)
        ex.what_this_is = ui_text.get(lang, "fallback_what").format(label=label)
    if not ex.key_facts:
        facts = []
        for attr, key in (("sender", "fact_from"), ("what_they_want", "fact_want"),
                          ("amount", "fact_amount"), ("deadline", "fact_deadline")):
            value = getattr(ex, attr)
            if value:
                facts.append(f"{ui_text.get(lang, key)} {value}")
        ex.key_facts = facts
    if not ex.what_to_do:
        ex.what_to_do = [ui_text.get(lang, "fallback_step")]


def _compose(ex: triage.Extraction, lang: str) -> AnalysisResult:
    """Apply the safety layer and assemble the final result."""
    _ensure_explanation(ex, lang)
    heuristic_text = " | ".join(
        filter(None, [ex.sender, ex.what_they_want, ex.requested_action,
                      *[s.evidence for s in ex.scam_signals]])
    )
    signals = triage.merge_signals(ex.scam_signals, triage.run_heuristics(heuristic_text))
    level = triage.worry_level(ex.document_type, signals)

    # Reasons: model's localized sentences (softened); any heuristic-only
    # signals the model missed get their localized taxonomy label appended.
    reasons = [safety.sanitize_reason(r) for r in ex.worry_reasons if r.strip()]
    model_ids = {s.id for s in ex.scam_signals}
    reasons += [
        ui_text.signal_label(s.id, lang) for s in signals if s.id not in model_ids
    ]

    actions = [a for a in (safety.sanitize_action_step(s) for s in ex.what_to_do) if a]
    actions.append(safety.verification_advice(lang))

    what_this_is = safety.soften_verdicts(ex.what_this_is).strip()
    key_facts = [safety.soften_verdicts(f).strip() for f in ex.key_facts]
    headline = safety.worry_headline(level, lang)

    speak_parts = [what_this_is, headline, *reasons[:2], *actions[:2]]
    speak_text = " ".join(p for p in speak_parts if p)[: config.TTS_MAX_CHARS]

    return AnalysisResult(
        ok=True,
        lang=lang,
        document_type=ex.document_type,
        what_this_is=what_this_is,
        key_facts=key_facts,
        worry_level=level,
        worry_headline=headline,
        worry_reasons=reasons,
        actions=actions,
        speak_text=speak_text,
    )


def analyze(image, lang: str) -> AnalysisResult:
    """Full request-driven analysis of one photographed document."""
    if image is None:
        return _error(lang, "err_no_image")
    if config.MOCK:
        return _compose(_mock_extraction(lang), lang)
    try:
        raw = extract.run_vision(image, prompts.analysis_prompt(lang))
    except Exception:
        traceback.print_exc()
        return _error(lang, "err_model")
    data = triage.parse_model_json(raw)
    if data is None:
        print(f"[guardian] unparseable model output: {raw[:500]!r}")
        return _error(lang, "err_model")
    ex = triage.validate_extraction(data)
    if not ex.is_document:
        return _error(lang, "err_not_document")
    if not ex.readable:
        return _error(lang, "err_unreadable")
    ex = explain.refine(ex, lang)  # no-op in lean config
    return _compose(ex, lang)


# --- Mock data (GUARDIAN_MOCK=1): UI development & tests without weights ----
_MOCK = {
    "en": {
        "what": "This is an electricity bill from City Power Company.",
        "facts": ["From: City Power Company", "Amount: $84.20", "Due: June 28, 2026",
                  "They want you to pay your monthly bill."],
        "steps": ["Check that the account name on the bill is yours.",
                  "Pay the way you normally pay your electricity bill."],
    },
    "hi": {
        "what": "यह City Power Company का बिजली का बिल है।",
        "facts": ["किसने भेजा: City Power Company", "रक़म: $84.20",
                  "आख़िरी तारीख़: 28 जून 2026", "वे चाहते हैं कि आप महीने का बिल भरें।"],
        "steps": ["देख लें कि बिल पर नाम आपका ही है।",
                  "बिल वैसे ही भरें जैसे आप हर महीने भरते हैं।"],
    },
    "es": {
        "what": "Esta es una factura de electricidad de City Power Company.",
        "facts": ["De: City Power Company", "Monto: $84.20",
                  "Vence: 28 de junio de 2026", "Quieren que pague su factura mensual."],
        "steps": ["Revise que el nombre en la factura sea el suyo.",
                  "Pague como paga normalmente su factura de electricidad."],
    },
}


def _mock_extraction(lang: str) -> triage.Extraction:
    m = _MOCK.get(lang, _MOCK["en"])
    ex = triage.Extraction(document_type="utility_bill", sender="City Power Company",
                           amount="$84.20", deadline="2026-06-28")
    ex.what_this_is = m["what"]
    ex.key_facts = list(m["facts"])
    ex.what_to_do = list(m["steps"])
    return ex
