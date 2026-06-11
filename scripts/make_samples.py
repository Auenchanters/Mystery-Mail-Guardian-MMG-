"""Write assets/samples/{bill,scam}.png — the one-tap gr.Examples letters.

Run from the repo root:  .venv\\Scripts\\python.exe scripts\\make_samples.py
The PNGs are committed; this script only re-runs when the letters change.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from PIL import Image  # noqa: E402

from guardian.samples import NORMAL_BILL, SCAM_LETTER, render_letter  # noqa: E402


def photographed(page, angle: float):
    """Faint paper-grey table + slight rotation, like a casual phone photo."""
    rotated = page.rotate(angle, expand=True, fillcolor="#b9b4ab", resample=Image.BICUBIC)
    table = Image.new("RGB", (rotated.width + 60, rotated.height + 60), "#b9b4ab")
    table.paste(rotated, (30, 30))
    return table


def main() -> None:
    out_dir = os.path.join("assets", "samples")
    os.makedirs(out_dir, exist_ok=True)
    photographed(render_letter(NORMAL_BILL), 1.4).save(os.path.join(out_dir, "bill.png"))
    photographed(render_letter(SCAM_LETTER), -1.2).save(os.path.join(out_dir, "scam.png"))
    print(f"wrote {out_dir}\\bill.png and {out_dir}\\scam.png")


if __name__ == "__main__":
    main()
