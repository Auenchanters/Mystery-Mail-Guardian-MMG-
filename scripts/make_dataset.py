"""Generate a labeled synthetic-letter dataset (images + labels.jsonl).

Usage:  .venv\\Scripts\\python.exe scripts\\make_dataset.py [n] [out_dir] [seed]
Default: 48 letters into dataset/eval (gitignored; fully reproducible by seed).
Each labels.jsonl row carries gold fields + an SFT-ready target JSON.
"""

from __future__ import annotations

import json
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from guardian import letterforge  # noqa: E402


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 48
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join("dataset", "eval")
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 2026
    rng = random.Random(seed)
    os.makedirs(out_dir, exist_ok=True)

    rows = []
    for i in range(n):
        gold = letterforge.forge(rng)
        img, degradation = letterforge.render_gold(gold, rng)
        fname = f"letter_{i:04d}.png"
        img.save(os.path.join(out_dir, fname))
        rows.append({
            "file": fname,
            "name": gold.name,
            "degradation": degradation,
            "document_type": gold.document_type,
            "sender": gold.sender,
            "amount": gold.amount,
            "deadline": gold.deadline,
            "signal_ids": gold.signal_ids,
            "expected_level": gold.expected_level,
            "acceptable_levels": list(gold.acceptable_levels),
            "sft_target": letterforge.sft_target(gold),
        })

    with open(os.path.join(out_dir, "labels.jsonl"), "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    by_name: dict[str, int] = {}
    for row in rows:
        by_name[row["name"]] = by_name.get(row["name"], 0) + 1
    print(f"wrote {n} letters to {out_dir} (seed {seed}): {by_name}")


if __name__ == "__main__":
    main()
