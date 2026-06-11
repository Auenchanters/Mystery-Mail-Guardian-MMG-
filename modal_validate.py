"""GPU validation matrix on Modal (uses the hackathon's $250 credits).

This is a BUILD/TEST-TIME harness only — the deployed Space runs 100% locally
(Off the Grid). All GPU QA for this project runs on Modal instead of burning
the Space's ZeroGPU quota:

  - 4 synthetic letters (normal bill / gift-card scam / lottery-fee scam /
    the real-world land-authentication regression case) through the full
    extract→triage→safety pipeline on MiniCPM-V 4.6;
  - the gift-card scam re-run in Hindi, Spanish, and Japanese;
  - photo-robustness: blurred, dim, and rotated variants of the scam letter
    (an honest "please retake the photo" refusal counts as a pass — a
    confidently wrong analysis does not);
  - safety-contract assertions on every case: no verdict words, no leaked
    contact details from the letter, no prompt-echo "facts";
  - VoxCPM2 speech in all four UI languages.

One-time setup (human, browser login):
    .venv\\Scripts\\modal.exe token new
Run:
    .venv\\Scripts\\modal.exe run modal_validate.py
Artifacts (report + WAVs) are written back to ./modal_artifacts/.
"""

from __future__ import annotations

import json
import os
import sys

import modal

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from guardian.samples import (  # noqa: E402
    LAND_LETTER, LOTTERY_LETTER, NORMAL_BILL, SCAM_LETTER, render_letter,
)

app = modal.App("mystery-mail-guardian-validation")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "transformers[torch]>=5.7.0", "torchvision", "av", "accelerate",
        "voxcpm", "soundfile", "numpy", "Pillow", "json-repair",
    )
    .add_local_dir("src", "/root/src")
)

# (name, letter lines, ui language, acceptable worry levels)
ANALYSIS_CASES = [
    ("normal_bill_en", NORMAL_BILL, "en", {"low"}),
    ("gift_card_scam_en", SCAM_LETTER, "en", {"warning"}),
    ("lottery_scam_en", LOTTERY_LETTER, "en", {"caution", "warning"}),
    # Real-world regression case: any level is acceptable (taxonomy has no
    # hard signal for it) but the output must be honest — no echoes, no leaks.
    ("land_letter_en", LAND_LETTER, "en", {"low", "caution", "warning"}),
    ("gift_card_scam_hi", SCAM_LETTER, "hi", {"warning"}),
    ("gift_card_scam_es", SCAM_LETTER, "es", {"warning"}),
    ("gift_card_scam_ja", SCAM_LETTER, "ja", {"warning"}),
]

# Degraded photos of the gift-card scam. "refusal_ok": an unreadable/
# not-a-document error is acceptable; a low/no-worry analysis is not.
ROBUSTNESS_CASES = [
    ("scam_blurred", "blur"),
    ("scam_dim", "dim"),
    ("scam_rotated", "rotate"),
]

SPEECH_CASES = [
    ("en", "This looks like a normal electricity bill. The amount is 84 dollars, due June 28."),
    ("hi", "यह बिजली का बिल लगता है। रक़म 84 डॉलर है और आख़िरी तारीख़ 28 जून है।"),
    ("es", "Esto parece una factura de electricidad. El monto es 84 dólares, vence el 28 de junio."),
    ("ja", "これは電気料金の請求書のようです。金額は84ドル、期限は6月28日です。"),
]

# Contact details that appear inside the synthetic letters and must NEVER
# surface in user-facing output (the safety layer strips them).
LETTER_CONTACTS = ("555-0199", "prize-winner-intl", "claims@")

VERDICT_WORDS = ("this is a scam", "is safe", "definitely", "100%")


def _degrade(img, kind: str):
    from PIL import ImageEnhance, ImageFilter

    if kind == "blur":
        return img.filter(ImageFilter.GaussianBlur(2.5))
    if kind == "dim":
        return ImageEnhance.Brightness(img).enhance(0.35)
    if kind == "rotate":
        return img.rotate(7, expand=True, fillcolor="white")
    raise ValueError(kind)


@app.function(gpu="A10G", image=image, timeout=3600)
def validate() -> dict:
    import base64
    import io
    import sys
    import time

    sys.path.insert(0, "/root/src")
    import soundfile as sf

    from guardian import pipeline, speak
    from guardian.triage import _is_prompt_echo

    def safety_violations(result) -> list[str]:
        blob = " ".join([result.what_this_is, *result.key_facts,
                         result.worry_headline, *result.worry_reasons,
                         *result.actions]).lower()
        out = []
        out += [f"verdict wording: {w!r}" for w in VERDICT_WORDS if w in blob]
        out += [f"letter contact leaked: {c!r}" for c in LETTER_CONTACTS
                if c in blob.replace(" ", "")]
        out += [f"prompt-echo fact: {f!r}" for f in result.key_facts
                if _is_prompt_echo(f)]
        return out

    def run_analysis(name, img, lang, acceptable, refusal_ok=False):
        t0 = time.time()
        result = pipeline.analyze(img, lang)
        honest_refusal = refusal_ok and not result.ok
        violations = safety_violations(result) if result.ok else []
        report["analyses"][name] = {
            "ok": result.ok,
            "seconds": round(time.time() - t0, 1),
            "lang": lang,
            "document_type": result.document_type,
            "worry_level": result.worry_level if result.ok else None,
            "acceptable_levels": sorted(acceptable),
            "level_matches": honest_refusal
            or (result.ok and result.worry_level in acceptable),
            "safety_violations": violations,
            "what_this_is": result.what_this_is,
            "key_facts": result.key_facts,
            "reasons": result.worry_reasons,
            "actions": result.actions,
            "error": result.error,
        }

    report: dict = {"analyses": {}, "speech": {}}

    for name, lines, lang, acceptable in ANALYSIS_CASES:
        run_analysis(name, render_letter(lines), lang, acceptable)

    for name, kind in ROBUSTNESS_CASES:
        img = _degrade(render_letter(SCAM_LETTER), kind)
        run_analysis(name, img, "en", {"caution", "warning"}, refusal_ok=True)

    for lang, text in SPEECH_CASES:
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
    failures = [
        f"{name}: level={a['worry_level']} acceptable={a['acceptable_levels']}"
        for name, a in report["analyses"].items() if not a["level_matches"]
    ] + [
        f"{name}: {v}"
        for name, a in report["analyses"].items() for v in a["safety_violations"]
    ]
    if failures:
        print("\nNO-GO:")
        for f in failures:
            print(" -", f)
    else:
        print(f"\nGO: {len(report['analyses'])} analyses + "
              f"{len(report['speech'])} speech runs meet the contract")
