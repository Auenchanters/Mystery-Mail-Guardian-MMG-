"""Raw-output probe: what does MiniCPM-V actually return for non-Latin letters?

The 06-12 multilingual eval showed hi/ja gift-card scams rated "low" with no
signals. This dumps the model's raw JSON for every hi_/ja_ dataset letter so
we can see whether it reads the script at all, answers in English, or returns
empty fields — and choose the right mitigation with evidence.

Run:  .venv\\Scripts\\modal.exe run modal_probe.py
Dump lands in modal_artifacts/ml_probe.json.
"""

from __future__ import annotations

import json
import os
import sys

import modal

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

app = modal.App("mystery-mail-guardian-probe")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "transformers[torch]>=5.7.0", "torchvision", "av", "accelerate",
        "soundfile", "numpy", "Pillow", "json-repair",
    )
    .add_local_dir("src", "/root/src")
    .add_local_dir(os.path.join("dataset", "eval"), "/root/dataset")
)


@app.function(gpu="A10G", image=image, timeout=1800,
              secrets=[modal.Secret.from_name("huggingface")])
def probe() -> list[dict]:
    import sys

    sys.path.insert(0, "/root/src")

    from PIL import Image

    from guardian import extract, prompts

    extract.load()
    with open("/root/dataset/labels.jsonl", encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    rows = [r for r in rows if r["name"].startswith(("hi_", "ja_"))]

    prompt = prompts.analysis_prompt("en")
    out = []
    for row in rows:
        img = Image.open(f"/root/dataset/{row['file']}").convert("RGB")
        raw = extract.run_vision(img, prompt)
        out.append({"file": row["file"], "name": row["name"],
                    "degradation": row["degradation"], "raw": raw})
    return out


@app.local_entrypoint()
def main():
    dump = probe.remote()
    os.makedirs("modal_artifacts", exist_ok=True)
    with open(os.path.join("modal_artifacts", "ml_probe.json"), "w",
              encoding="utf-8") as f:
        json.dump(dump, f, indent=2, ensure_ascii=False)
    for d in dump:
        print(f"--- {d['name']} ({d['degradation']}) ---")
        print(d["raw"][:400].replace("\n", " "))
    print(f"\nsaved {len(dump)} probes to modal_artifacts/ml_probe.json")
