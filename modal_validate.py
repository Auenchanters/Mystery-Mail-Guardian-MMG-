"""GPU validation of all three models on Modal (uses the hackathon's $250 credits).

This is a BUILD/TEST-TIME harness only — the deployed Space runs 100% locally
(Off the Grid). Modal here replaces "borrow a GPU box" for the Day-1 de-risk:
it renders two synthetic letters (a normal bill + a gift-card scam), runs the
full extract→triage→explain pipeline on MiniCPM-V 4.6, exercises the safety
layer, and synthesizes Hindi + English speech with VoxCPM2.

One-time setup (human, browser login):
    .venv\\Scripts\\modal.exe token new
Run:
    .venv\\Scripts\\modal.exe run modal_validate.py
Artifacts (transcripts + WAVs) are written back to ./modal_artifacts/.
"""

from __future__ import annotations

import json
import os
import sys

import modal

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from guardian.samples import NORMAL_BILL, SCAM_LETTER, render_letter  # noqa: E402

app = modal.App("mystery-mail-guardian-validation")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "transformers[torch]>=5.7.0", "torchvision", "av", "accelerate",
        "voxcpm", "soundfile", "numpy", "Pillow",
    )
    .add_local_dir("src", "/root/src")
)

@app.function(gpu="A10G", image=image, timeout=1800)
def validate() -> dict:
    import base64
    import io
    import sys
    import time

    sys.path.insert(0, "/root/src")
    import soundfile as sf

    from guardian import pipeline, speak

    report: dict = {"analyses": {}, "speech": {}}

    for name, lines, expect in [
        ("normal_bill", NORMAL_BILL, "low"),
        ("scam_letter", SCAM_LETTER, "warning"),
    ]:
        t0 = time.time()
        result = pipeline.analyze(render_letter(lines), "en")
        report["analyses"][name] = {
            "ok": result.ok,
            "seconds": round(time.time() - t0, 1),
            "document_type": result.document_type,
            "worry_level": result.worry_level,
            "expected_level": expect,
            "level_matches": result.worry_level == expect,
            "what_this_is": result.what_this_is,
            "reasons": result.worry_reasons,
            "actions": result.actions,
            "error": result.error,
        }

    for lang, text in [
        ("en", "This looks like a normal electricity bill. The amount is 84 dollars, due June 28."),
        ("hi", "यह बिजली का बिल लगता है। रक़म 84 डॉलर है और आख़िरी तारीख़ 28 जून है।"),
    ]:
        t0 = time.time()
        sr, wav = speak.synthesize(text)
        buf = io.BytesIO()
        sf.write(buf, wav, sr, format="WAV")
        report["speech"][lang] = {
            "seconds": round(time.time() - t0, 1),
            "sample_rate": sr,
            "audio_seconds": round(len(wav) / sr, 1),
            "wav_b64": base64.b64encode(buf.getvalue()).decode(),
        }

    return report


@app.local_entrypoint()
def main():
    import base64
    import os

    report = validate.remote()
    os.makedirs("modal_artifacts", exist_ok=True)
    for lang, info in report["speech"].items():
        wav_b64 = info.pop("wav_b64")
        path = os.path.join("modal_artifacts", f"speech_{lang}.wav")
        with open(path, "wb") as f:
            f.write(base64.b64decode(wav_b64))
        info["saved_to"] = path
    with open(os.path.join("modal_artifacts", "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(json.dumps(report, indent=2, ensure_ascii=False))
    checks = [a["level_matches"] for a in report["analyses"].values()]
    print("\nGO" if all(checks) else "\nNO-GO: worry levels did not match expectations")
