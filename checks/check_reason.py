"""Isolation check 2/3 — the reasoning step produces a safe, plain summary.

Feeds a synthetic scammy fact-bundle through the FULL-config reasoner
(MiniCPM4.1-8B GGUF via llama.cpp) and through the safety layer.

Run:  GUARDIAN_CONFIG=full python checks/check_reason.py
(With lean config this script just demonstrates the safety-layer composition.)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from guardian import explain, pipeline, triage


def main() -> int:
    ex = triage.Extraction(
        document_type="suspected_scam",
        sender="'Tax Enforcement Bureau'",
        what_they_want="Immediate payment of a $500 'fine'",
        amount="$500",
        deadline="within 24 hours",
        requested_action="Buy Google Play gift cards and call 1-800-555-0199 with the codes",
    )
    ex.scam_signals = [
        triage.ScamSignal("gift_card_or_crypto", "pay with Google Play gift cards"),
        triage.ScamSignal("urgency", "within 24 hours"),
        triage.ScamSignal("threat_or_arrest", "threatens arrest"),
    ]
    ex.what_this_is = "This letter says it is from the tax office and demands a fine."
    ex.worry_reasons = ["It demands payment with gift cards.",
                       "It threatens arrest within 24 hours."]
    ex.what_to_do = ["Do not buy any gift cards.", "Show this letter to a family member."]

    ex = explain.refine(ex, "en")  # exercises llama.cpp in full config
    result = pipeline._compose(ex, "en")

    print(f"worry_level : {result.worry_level}")
    print(f"headline    : {result.worry_headline}")
    print(f"what_this_is: {result.what_this_is}")
    print("reasons     :", *[f"\n  - {r}" for r in result.worry_reasons])
    print("actions     :", *[f"\n  - {a}" for a in result.actions])

    problems = []
    if result.worry_level != "warning":
        problems.append("expected worry_level=warning")
    blob = " ".join([result.what_this_is, *result.worry_reasons, *result.actions]).lower()
    if "this is a scam" in blob:
        problems.append("definitive verdict leaked")
    if "555-0199" in blob or "1-800" in blob:
        problems.append("scammer contact details leaked into output")
    if problems:
        print("\nFAIL:", "; ".join(problems))
        return 1
    print("\nPASS: warning level, cautious wording, no leaked contact details")
    return 0


if __name__ == "__main__":
    sys.exit(main())
