"""Regression check for the 2026-06-11 user report: a real-world 'Letter of
Land Authentication' produced prompt-echo garbage facts and a 'low' verdict.
Re-runs a reconstruction of that letter against the LIVE Space.

Run:  python checks/check_land_letter.py [space_id]
"""

from __future__ import annotations

import os
import re
import sys
import tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from gradio_client import Client, handle_file  # noqa: E402

from guardian.samples import render_letter  # noqa: E402

SPACE = sys.argv[1] if len(sys.argv) > 1 else "build-small-hackathon/Mystery_Mail_Guardian"

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

ECHOES = ("who sent it", "what they want", "money mentioned", "what to do",
          "key facts", "amount", "deadline")


def _token() -> str | None:
    path = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "token")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read().strip()
    return os.environ.get("HF_TOKEN")


def main() -> int:
    img = render_letter(LAND_LETTER, font_size=28)
    path = os.path.join(tempfile.gettempdir(), "mmg_land.png")
    img.save(path)

    client = Client(SPACE, token=_token())
    what, worry, todo, *_ = client.predict(
        image=handle_file(path), lang_label="English", api_name="/on_analyze"
    )
    level = (re.search(r"stamp stamp-(\w+)", worry) or [None, "none"])[1]
    facts = re.findall(r"<li>(.*?)</li>", what)
    print("stamp:", level)
    print("what:", re.sub(r"<[^>]+>", " ", what).split("What this is")[-1].strip()[:200])
    print("facts:", facts)
    print("worry reasons:", re.findall(r"<li>(.*?)</li>", worry))

    problems = []
    for f in facts:
        if f.strip().rstrip(":").lower() in ECHOES:
            problems.append(f"prompt echo survived as a fact: {f!r}")
    blob = (what + worry + todo).lower()
    if "maasplusdesign" in blob.replace(" ", "") and "@" in blob:
        problems.append("letter email leaked")
    if "never use the contact details" not in todo.lower():
        problems.append("verification advice missing")

    if problems:
        print("\nFAIL:", "; ".join(problems))
        return 1
    print(f"\nPASS: no prompt echoes; worry level = {level} "
          "(classification quality is model-dependent, but output is honest)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
