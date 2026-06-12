"""Simulate final worry levels from modal_artifacts/ml_probe.json raw dumps
(dev tooling — runs the same triage path as the pipeline, no GPU needed)."""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from guardian import triage  # noqa: E402


def main() -> None:
    with open("modal_artifacts/ml_probe.json", encoding="utf-8") as f:
        data = json.load(f)
    for p in data:
        parsed = triage.parse_model_json(p["raw"])
        if parsed is None:
            print(f"{p['name']} ({p['degradation']}): PARSE FAIL")
            continue
        ex = triage.validate_extraction(parsed)
        text = " | ".join(filter(None, [
            ex.sender, ex.what_they_want, ex.requested_action, ex.what_this_is,
            *ex.key_facts, *ex.worry_reasons,
            *[s.evidence for s in ex.scam_signals]]))
        signals = triage.merge_signals(ex.scam_signals, triage.run_heuristics(text))
        level = triage.worry_level(ex.document_type, signals)
        print(f"{p['name']} ({p['degradation']}): level={level} "
              f"signals={[s.id for s in signals]}")


if __name__ == "__main__":
    main()
