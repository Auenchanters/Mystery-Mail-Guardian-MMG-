"""Isolation check 1/3 — MiniCPM-V 4.6 reads a real photographed letter.

Run on a GPU machine (or the Space) with requirements.txt installed:
    python checks/check_extract.py path/to/letter_photo.jpg [language]

PASS = the printed JSON has is_document=true, a sensible document_type/sender,
and a plain-language explanation in the requested language.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from PIL import Image

from guardian import extract, prompts, triage


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    image = Image.open(sys.argv[1]).convert("RGB")
    lang = sys.argv[2] if len(sys.argv) > 2 else "en"

    t0 = time.time()
    raw = extract.run_vision(image, prompts.analysis_prompt(lang))
    elapsed = time.time() - t0

    print(f"--- raw output ({elapsed:.1f}s) ---\n{raw}\n")
    data = triage.parse_model_json(raw)
    if data is None:
        print("FAIL: output is not parseable JSON")
        return 1
    ex = triage.validate_extraction(data)
    print("--- validated extraction ---")
    print(json.dumps(
        {"is_document": ex.is_document, "readable": ex.readable,
         "document_type": ex.document_type, "sender": ex.sender,
         "amount": ex.amount, "deadline": ex.deadline,
         "signals": [s.id for s in ex.scam_signals],
         "what_this_is": ex.what_this_is, "what_to_do": ex.what_to_do},
        indent=2, ensure_ascii=False))
    print(f"\nPASS (inspect quality above; {elapsed:.1f}s/pass vs 120s GPU budget)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
