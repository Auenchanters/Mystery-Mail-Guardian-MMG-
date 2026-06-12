"""Robustness eval v2 on Modal: where does honest behavior break?

Scores every graded degradation (scripts/make_robust_set.py) through the
full triage path. Scoring is OUTCOME-based, not accuracy-based:
  - scam letter  -> caution/warning OR an honest refusal = PASS; "low" = FAIL
  - bill letter  -> low OR an honest refusal = PASS; caution/warning = FAIL
The breaking point per degradation becomes the photo-guidance numbers in
the README/Field Notes.

Run:  .venv\\Scripts\\modal.exe run modal_robust.py
"""

from __future__ import annotations

import json
import os
import sys

import modal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = modal.App("mystery-mail-guardian-robust")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "transformers[torch]>=5.7.0", "torchvision", "av", "accelerate",
        "soundfile", "numpy", "Pillow", "json-repair",
    )
    .add_local_dir("src", "/root/src")
    .add_local_dir(os.path.join("dataset", "robust"), "/root/dataset")
)


@app.function(gpu="A10G", image=image, timeout=3600,
              secrets=[modal.Secret.from_name("huggingface")])
def run() -> list[dict]:
    import sys

    sys.path.insert(0, "/root/src")

    from PIL import Image

    from guardian import extract, prompts, triage

    extract.load()
    with open("/root/dataset/labels.jsonl", encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]

    prompt = prompts.analysis_prompt("en")
    out = []
    for row in rows:
        img = Image.open(f"/root/dataset/{row['file']}").convert("RGB")
        raw = extract.run_vision(img, prompt)
        data = triage.parse_model_json(raw)
        if data is None:
            outcome, level = "refusal", None
        else:
            ex = triage.validate_extraction(data)
            if not ex.is_document or not ex.readable:
                outcome, level = "refusal", None
            else:
                text = " | ".join(filter(None, [
                    ex.sender, ex.what_they_want, ex.requested_action,
                    ex.what_this_is, *ex.key_facts, *ex.worry_reasons,
                    *[s.evidence for s in ex.scam_signals]]))
                signals = triage.merge_signals(
                    ex.scam_signals, triage.run_heuristics(text))
                level = triage.worry_level(ex.document_type, signals)
                outcome = "analyzed"
        is_scam = bool(row["signal_ids"])
        if outcome == "refusal":
            ok = True  # honest refusal is always acceptable
        elif is_scam:
            ok = level in ("caution", "warning")
        else:
            ok = level == "low"
        out.append({**{k: row[k] for k in ("file", "tag", "kind", "level")},
                    "outcome": outcome, "worry_level": level, "ok": ok})
    return out


@app.local_entrypoint()
def main():
    results = run.remote()
    os.makedirs("modal_artifacts", exist_ok=True)
    with open(os.path.join("modal_artifacts", "robust_report.json"), "w",
              encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"{'case':<24}{'outcome':<10}{'level':<10}{'ok'}")
    fails = 0
    for r in results:
        mark = "PASS" if r["ok"] else "FAIL"
        fails += 0 if r["ok"] else 1
        print(f"{r['tag']}_{r['kind']}_{r['level']:<10}{r['outcome']:<10}"
              f"{str(r['worry_level']):<10}{mark}")
    print(f"\n{len(results) - fails}/{len(results)} honest outcomes "
          "(report: modal_artifacts/robust_report.json)")
