"""Live probe: a credentials-phishing letter against the deployed Space.

Added after the 06-12 Modal eval showed phishing letters were the only
under-flagged class (caution instead of warning) before the worry_reasons
heuristic boost. One ZeroGPU call; run after deploys.

Run:  python checks/check_live_phishing.py [space_id]
"""

from __future__ import annotations

import os
import re
import sys
import tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import random  # noqa: E402

from gradio_client import Client, handle_file  # noqa: E402

from guardian.letterforge import phishing_account  # noqa: E402
from guardian.samples import render_letter  # noqa: E402

SPACE = sys.argv[1] if len(sys.argv) > 1 else "build-small-hackathon/Mystery_Mail_Guardian"


def _token() -> str | None:
    path = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "token")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read().strip()
    return os.environ.get("HF_TOKEN")


def main() -> int:
    gold = phishing_account(random.Random(7))
    img = render_letter(gold.lines)
    path = os.path.join(tempfile.gettempdir(), "mmg_phish.png")
    img.save(path)

    client = Client(SPACE, token=_token())
    what, worry, todo, *_ = client.predict(
        image=handle_file(path), lang_label="English", api_name="/on_analyze"
    )
    level = (re.search(r"stamp stamp-(\w+)", worry) or [None, "none"])[1]
    print("stamp:", level)
    print("reasons:", re.findall(r"<li>(.*?)</li>", worry))

    problems = []
    if level not in ("caution", "warning"):
        problems.append(f"phishing letter rated {level}")
    blob = (what + worry + todo).lower()
    if "account-verify-secure" in blob.replace(" ", ""):
        problems.append("phishing link leaked into output")
    if "never use the contact details" not in todo.lower():
        problems.append("verification advice missing")

    if problems:
        print("\nFAIL:", "; ".join(problems))
        return 1
    print(f"\nPASS: live phishing probe rated {level}, no link leak")
    return 0


if __name__ == "__main__":
    sys.exit(main())
