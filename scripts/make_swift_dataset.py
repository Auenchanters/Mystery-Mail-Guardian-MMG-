"""Convert a make_dataset.py split into ms-swift SFT format (messages+images).

Usage: .venv\\Scripts\\python.exe scripts\\make_swift_dataset.py [in_dir] [out.jsonl]
Default: dataset/train -> dataset/train/swift.jsonl. Image paths are written
relative ("./letter_XXXX.png"); modal_finetune.py rewrites them to container
paths at run time.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from guardian import prompts  # noqa: E402


def main() -> None:
    in_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join("dataset", "train")
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(in_dir, "swift.jsonl")
    prompt = prompts.analysis_prompt("en")

    rows = []
    with open(os.path.join(in_dir, "labels.jsonl"), encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            rows.append({
                "messages": [
                    {"role": "user", "content": f"<image>\n{prompt}"},
                    {"role": "assistant",
                     "content": json.dumps(r["sft_target"], ensure_ascii=False)},
                ],
                "images": [f"./{r['file']}"],
            })

    with open(out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} SFT samples to {out}")


if __name__ == "__main__":
    main()
