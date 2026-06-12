"""Generate the graded-degradation robustness set (dataset/robust).

One scam + one bill, 6 degradation kinds x 3 intensity levels + 2 clean
baselines = 38 images. Run:
    .venv\\Scripts\\python.exe scripts\\make_robust_set.py
"""

from __future__ import annotations

import json
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from guardian import letterforge  # noqa: E402

KINDS = ("blur", "dim", "rotate", "perspective", "shadow", "noise")


def main() -> None:
    out_dir = os.path.join("dataset", "robust")
    os.makedirs(out_dir, exist_ok=True)
    rng = random.Random(2026)
    cases = [("scam", letterforge.gift_card_scam(rng)),
             ("bill", letterforge.utility_bill(rng))]

    rows = []
    for tag, gold in cases:
        base, _ = letterforge.render_gold(gold, rng, degrade=False)
        variants = [("clean", 0, base)]
        variants += [(k, lvl, letterforge.degrade_graded(base, k, lvl))
                     for k in KINDS for lvl in (1, 2, 3)]
        for kind, level, img in variants:
            fname = f"{tag}_{kind}_{level}.png"
            img.convert("RGB").save(os.path.join(out_dir, fname))
            rows.append({"file": fname, "tag": tag, "kind": kind, "level": level,
                         "signal_ids": gold.signal_ids,
                         "acceptable_levels": list(gold.acceptable_levels)})

    with open(os.path.join(out_dir, "labels.jsonl"), "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} images to {out_dir}")


if __name__ == "__main__":
    main()
