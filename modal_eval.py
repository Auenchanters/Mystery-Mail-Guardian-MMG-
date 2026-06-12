"""Extraction-accuracy + token-efficiency eval on Modal (A10G).

Runs MiniCPM-V 4.6 over the labeled synthetic dataset (scripts/make_dataset.py)
with TWO prompt variants — the production prompt and a compact one — and
scores, per variant:

  - worry-level accuracy (through guardian's own triage rules + heuristics)
  - scam recall (scam letters that reached caution/warning)
  - false-alarm rate (clean letters pushed above "low")
  - document-type accuracy, amount/deadline hit rates
  - JSON parse failures, mean latency, output size, prompt size (token economy)

Build/test-time only; the deployed runtime stays 100% local.

Prepare data, then run:
    .venv\\Scripts\\python.exe scripts\\make_dataset.py
    .venv\\Scripts\\modal.exe run modal_eval.py
Report lands in modal_artifacts/eval_report.json.
"""

from __future__ import annotations

import json
import os
import sys

import modal

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

app = modal.App("mystery-mail-guardian-eval")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "transformers[torch]>=5.7.0", "torchvision", "av", "accelerate",
        "soundfile", "numpy", "Pillow", "json-repair",
    )
    .add_local_dir("src", "/root/src")
    .add_local_dir(os.path.join("dataset", "eval"), "/root/dataset")
)

# The token-economy challenger: same JSON contract, ~60% fewer prompt tokens.
COMPACT_PROMPT = """You help an elderly person understand a photographed letter. \
Read it and answer with ONE JSON object only:
{"is_document": bool, "readable": bool,
 "document_type": one of ["utility_bill","bank","government_tax","medical","insurance","subscription","charity","marketing","suspected_scam","personal","other"],
 "sender": str|null, "what_they_want": str|null, "amount": str|null,
 "deadline": str|null, "requested_action": str|null,
 "scam_signals": [{"id": one of [%SIGNALS%], "evidence": short quote}],
 "explanation": {"what_this_is": "1-2 plain English sentences",
   "key_facts": [up to 4 short facts with real values from the letter],
   "worry_reasons": [one short sentence per signal], "what_to_do": [2-4 safe steps]}}
Rules: copy real values from the letter; never repeat this schema's words; \
never declare it definitely a scam or definitely safe; no phone numbers, \
links, or emails from the letter in what_to_do; null/[] when absent."""


@app.function(gpu="A10G", image=image, timeout=3600)
def evaluate() -> dict:
    import sys
    import time

    sys.path.insert(0, "/root/src")

    from guardian import extract, prompts, triage

    extract.load()

    from PIL import Image

    with open("/root/dataset/labels.jsonl", encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]

    variants = {
        "production": prompts.analysis_prompt("en"),
        "compact": COMPACT_PROMPT.replace(
            "%SIGNALS%", ",".join(f'"{s}"' for s in triage.SIGNAL_IDS)),
    }

    report: dict = {"n_letters": len(rows), "variants": {}}
    for vname, prompt in variants.items():
        m = {"prompt_chars": len(prompt), "parse_failures": 0, "level_hits": 0,
             "doc_type_hits": 0, "amount_hits": 0, "amount_total": 0,
             "deadline_hits": 0, "deadline_total": 0,
             "scam_total": 0, "scam_caught": 0, "clean_total": 0, "false_alarms": 0,
             "latency_s": [], "raw_chars": [], "per_case": []}
        for row in rows:
            img = Image.open(f"/root/dataset/{row['file']}").convert("RGB")
            t0 = time.time()
            raw = extract.run_vision(img, prompt)
            dt = time.time() - t0
            m["latency_s"].append(dt)
            m["raw_chars"].append(len(raw))

            data = triage.parse_model_json(raw)
            if data is None:
                m["parse_failures"] += 1
                m["per_case"].append({"file": row["file"], "name": row["name"],
                                      "level": "PARSE_FAIL"})
                continue
            ex = triage.validate_extraction(data)
            heuristic_text = " | ".join(filter(None, [
                ex.sender, ex.what_they_want, ex.requested_action,
                ex.what_this_is, *ex.key_facts, *ex.worry_reasons,
                *[s.evidence for s in ex.scam_signals]]))
            signals = triage.merge_signals(
                ex.scam_signals, triage.run_heuristics(heuristic_text))
            level = triage.worry_level(ex.document_type, signals)

            is_scam = bool(row["signal_ids"])
            if level in row["acceptable_levels"]:
                m["level_hits"] += 1
            if ex.document_type == row["document_type"]:
                m["doc_type_hits"] += 1
            if is_scam:
                m["scam_total"] += 1
                if level in ("caution", "warning"):
                    m["scam_caught"] += 1
            else:
                m["clean_total"] += 1
                if level != "low" and row["name"] != "lookalike_ad":
                    m["false_alarms"] += 1
            if row["amount"]:
                m["amount_total"] += 1
                blob = " ".join(filter(None, [ex.amount, *ex.key_facts]))
                if row["amount"].lstrip("$") in blob:
                    m["amount_hits"] += 1
            if row["deadline"]:
                m["deadline_total"] += 1
                blob = " ".join(filter(None, [ex.deadline, *ex.key_facts]))
                day = row["deadline"].split(",")[0]  # "June 28"
                if day in blob:
                    m["deadline_hits"] += 1
            m["per_case"].append({"file": row["file"], "name": row["name"],
                                  "gold": row["expected_level"], "level": level,
                                  "doc_type": ex.document_type, "seconds": round(dt, 1)})

        n = len(rows)
        report["variants"][vname] = {
            "prompt_chars": m["prompt_chars"],
            "parse_failures": m["parse_failures"],
            "level_accuracy": round(m["level_hits"] / n, 3),
            "doc_type_accuracy": round(m["doc_type_hits"] / n, 3),
            "scam_recall": round(m["scam_caught"] / max(m["scam_total"], 1), 3),
            "false_alarm_rate": round(m["false_alarms"] / max(m["clean_total"], 1), 3),
            "amount_hit_rate": round(m["amount_hits"] / max(m["amount_total"], 1), 3),
            "deadline_hit_rate": round(m["deadline_hits"] / max(m["deadline_total"], 1), 3),
            "mean_latency_s": round(sum(m["latency_s"]) / n, 2),
            "mean_output_chars": int(sum(m["raw_chars"]) / n),
            "per_case": m["per_case"],
        }
    return report


@app.local_entrypoint()
def main():
    report = evaluate.remote()
    os.makedirs("modal_artifacts", exist_ok=True)
    with open(os.path.join("modal_artifacts", "eval_report.json"), "w",
              encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    cols = ["prompt_chars", "parse_failures", "level_accuracy", "doc_type_accuracy",
            "scam_recall", "false_alarm_rate", "amount_hit_rate",
            "deadline_hit_rate", "mean_latency_s", "mean_output_chars"]
    print(f"\n{report['n_letters']} letters per variant\n")
    header = f"{'metric':<22}" + "".join(f"{v:>14}" for v in report["variants"])
    print(header)
    for c in cols:
        print(f"{c:<22}" + "".join(
            f"{report['variants'][v][c]:>14}" for v in report["variants"]))
    print("\nsaved: modal_artifacts/eval_report.json")
