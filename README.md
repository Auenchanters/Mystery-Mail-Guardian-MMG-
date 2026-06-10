---
title: Mystery-Mail Guardian
emoji: 📬
colorFrom: indigo
colorTo: green
sdk: gradio
sdk_version: 6.17.3
python_version: "3.12"
app_file: app.py
license: apache-2.0
short_description: Photograph a confusing letter — it explains it, locally.
tags:
  - build-small-hackathon
  - backyard-ai
  - minicpm
  - voxcpm
  - privacy
  - accessibility
---

# 📬 Mystery-Mail Guardian

**Photograph a confusing letter, bill, or form. The app reads it _locally_, explains in plain
language what it is, cautiously flags scam warning signs (with reasons, never verdicts), says
what to actually do next, and reads the summary aloud — in English, Hindi, or Spanish.**

> 🔒 **The privacy promise:** *Your documents never leave this device. Everything runs on small
> models, locally.* Financial, legal, and medical letters are exactly the documents people
> (rightly) refuse to upload to a cloud API. The local-first constraint isn't a limitation here —
> it **is** the product.

## Who this is for

<!-- HUMAN: name the real person (with their consent) and describe their situation.
     Example: "Built for my grandmother, who reads Hindi comfortably but gets official
     English-language letters she can't always tell apart from scam mail." -->
Built for **[real person — name/relationship here]**, who struggles with official
English-language mail, dense bureaucratic language, and telling real bills from scams.
They used this app on their own real letters — see the demo video below.

## What this is NOT

This is **not a generic OCR/document parser**. It is **scam-and-action triage for a specific
vulnerable person, running fully on-device**. It never renders verdicts ("this is a scam" /
"this is safe") — it explains, lists concrete warning signs, and always points the person to
verification channels they already trust.

## Models — 3.3B total parameters (cap: 32B)

| Model | Params | Role | Runtime |
|---|---|---|---|
| [openbmb/MiniCPM-V-4.6](https://huggingface.co/openbmb/MiniCPM-V-4.6) | 1.3B | **Central engine** — reads the photo (OCR + layout), triages, explains | transformers (ZeroGPU) |
| [openbmb/VoxCPM2](https://huggingface.co/openbmb/VoxCPM2) | 2.0B | Reads the summary aloud (30 languages, neutral voice, no cloning) | voxcpm (ZeroGPU) |
| **Total (lean config, deployed)** | **3.3B** | | |

Optional **full config** (`GUARDIAN_CONFIG=full`, +[openbmb/MiniCPM4.1-8B](https://huggingface.co/openbmb/MiniCPM4.1-8B)
GGUF via **llama.cpp** for stronger plain-language reasoning): **11.3B total** — still well under
the 32B cap. The MiniCPM family is the heart of the app in both configs.

## How it works (request-driven, one photo → one result)

1. **Extract + triage + explain** — MiniCPM-V 4.6 reads the photographed document in a single
   pass and returns structured JSON: document type, sender, amount, deadline, requested action,
   scam signals with evidence, and a low-reading-level explanation in the chosen language.
2. **Safety layer** (`src/guardian/safety.py`) — its own module, by design:
   - verdict-sounding text is softened in code, not just in the prompt;
   - the "Should you worry?" headline is template-written by us, never by the model;
   - phone numbers / links / emails from the letter are **stripped from the action steps** —
     a scam letter's whole goal is to get you to use *its* contact details;
   - independent-verification advice is always appended;
   - an independent heuristic scam-signal scan (gift cards, OTP requests, urgency, threats,
     lottery language…) double-checks the model.
3. **Speak** — VoxCPM2 reads the summary aloud on demand (big 🔊 button).

## Running it

- **This Space:** upload or photograph a letter, pick a language, press "Read my letter."
- **Locally:** `pip install -r requirements.txt && python app.py` (GPU recommended).
- **UI development without weights:** `GUARDIAN_MOCK=1 python app.py`.
- **Tests** (66, offline): `pip install -r requirements-dev.txt && pytest tests`.
- **Model isolation checks** (GPU): `python checks/check_extract.py letter.jpg`,
  `python checks/check_reason.py`, `python checks/check_speak.py hi`.

## Hackathon constraints — status

- ✅ **≤ 32B total params** — 3.3B deployed (printed in logs at startup; guard refuses to boot over cap)
- ✅ **Tiny Titan (≤ 4B)** — the deployed lean config totals 3.3B parameters
- ✅ **Gradio app on a HF Space** (ZeroGPU, request-driven, `@spaces.GPU` per call)
- ✅ **Off the Grid** — zero cloud APIs at runtime; model weights download once from the HF Hub at build
- ✅ **OpenBMB-central** — MiniCPM-V 4.6 is the engine; VoxCPM2 the voice; all models are OpenBMB
- 🟡 **Llama Champion** — available via the documented `GUARDIAN_CONFIG=full` (llama.cpp GGUF)
- ✅ **Cautious scam framing** — enforced in code (see `tests/test_safety.py`)

## Submission links

<!-- HUMAN: fill these before submitting -->
- 🎥 **Demo video (real person using it):** _link goes here_
- 📣 **Social post:** _link goes here_
- 📝 **Field Notes write-up:** see [BUILD_LOG.md](BUILD_LOG.md) — _published link goes here_

## Honest limitations

- It can misread poor photos (it says so and asks for a better one).
- It is not legal, medical, or financial advice — and tells the user that.
- The scam check is a *cautious flag with reasons*, never a verdict. The UI carries a permanent
  reminder: *"I can make mistakes. For anything important, check with someone you trust."*
