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
  - track:backyard
  - sponsor:openbmb
  - sponsor:modal
  - achievement:offgrid
  - achievement:fieldnotes
  - achievement:offbrand
  - achievement:sharing
  - build-small-hackathon
  - minicpm
  - voxcpm
  - privacy
  - accessibility
---

# 📬 Mystery-Mail Guardian

**Photograph a confusing letter, bill, or form. The app reads it _locally_, explains in plain
language what it is, cautiously flags scam warning signs (with reasons, never verdicts), says
what to actually do next, and reads the summary aloud — in English, Hindi, Spanish, or Japanese.**

> 🔒 **The privacy promise:** *Your documents never leave this device. Everything runs on small
> models, locally.* Financial, legal, and medical letters are exactly the documents people
> (rightly) refuse to upload to a cloud API. The local-first constraint isn't a limitation here —
> it **is** the product.

## What it looks like

<table>
  <tr>
    <td align="center" width="50%">
      <img src="https://huggingface.co/spaces/build-small-hackathon/Mystery_Mail_Guardian/resolve/main/docs/ui/desktop-dark-en.png" alt="Landing page — midnight study desk theme" width="100%"/>
      <sub><b>The kitchen-table post office</b> — wax-seal privacy promise, one-tap languages, 1·2·3 steps</sub>
    </td>
    <td align="center" width="50%">
      <img src="https://huggingface.co/spaces/build-small-hackathon/Mystery_Mail_Guardian/resolve/main/docs/ui/result-en.png" alt="Analysis result — letter sheets with postage-stamp verdict" width="100%"/>
      <sub><b>Letters as paper sheets</b> — postage-stamp verdict, reasons, safe next steps</sub>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="https://huggingface.co/spaces/build-small-hackathon/Mystery_Mail_Guardian/resolve/main/docs/ui/softclub-live.png" alt="Gen X Soft Club easter egg on Japanese" width="100%"/>
      <sub><b>The 日本語 easter egg</b> — Gen X Soft Club skin, same WCAG-AA contrast tests as every palette</sub>
    </td>
    <td align="center" width="50%">
      <img src="https://huggingface.co/spaces/build-small-hackathon/Mystery_Mail_Guardian/resolve/main/docs/ui/mobile-en.png" alt="Mobile layout, 380px" width="55%"/>
      <sub><b>Phone-first</b> — ≥48px targets, single column, no horizontal scroll at 380px</sub>
    </td>
  </tr>
</table>

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

## Models — every one is OpenBMB, 3.3B total (cap: each model < 32B; ours don't even sum to 4B)

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
   - phone numbers / links / emails from the letter are **stripped from every card**
     (facts, reasons, and steps) — a scam letter's whole goal is to get you to use
     *its* contact details;
   - independent-verification advice is always appended;
   - an independent heuristic scam-signal scan (gift cards, OTP requests, urgency, threats,
     lottery language…) double-checks the model.
3. **Speak** — VoxCPM2 reads the summary aloud on demand (big 🔊 button).

## Running it

- **This Space:** upload or photograph a letter, pick a language, press "Read my letter."
- **Locally:** `pip install -r requirements.txt && python app.py` (GPU recommended).
- **UI development without weights:** `GUARDIAN_MOCK=1 python app.py`.
- **Tests** (85, offline — includes WCAG AA contrast enforcement): `pip install -r requirements-dev.txt && pytest tests`.
- **Model isolation checks** (GPU): `python checks/check_extract.py letter.jpg`,
  `python checks/check_reason.py`, `python checks/check_speak.py hi`.
- **GPU validation on Modal:** model validation for this project runs on Modal GPUs —
  `modal run modal_validate.py` exercises the full pipeline (normal bill + scam letter)
  and VoxCPM2 speech on an A10G, writing transcripts and audio to `modal_artifacts/`.
  This is build/test-time only; the deployed app's runtime remains 100% local (Off the Grid).

## Design — the Kitchen-Table Post Office (Off-Brand entry)

The UI is hand-built past the stock Gradio look: a forced-dark **"midnight study
desk"** palette with letters as lamp-lit paper sheets, a **postage-stamp verdict
badge** (perforated edge, inline SVG), a **wax-seal privacy badge** carrying the
soul of the project, postmark-ring step numbers, and one-tap segmented language
buttons — no flags, no dropdown. Typography is **Atkinson Hyperlegible** (designed
by the Braille Institute for low-vision readers — an elder-readability font in an
elder-readability app) with Noto Sans Devanagari; both are **vendored into the
repo**, so the app makes zero font/CDN requests at runtime (Off the Grid stays
intact). Every text/background pair is enforced against **WCAG AA by unit tests**;
animations sit behind `prefers-reduced-motion`; tap targets are ≥48px.

## Hackathon constraints — status

- ✅ **≤ 32B total params** — 3.3B deployed (printed in logs at startup; guard refuses to boot over cap)
- ✅ **Tiny Titan (≤ 4B)** — the deployed lean config totals 3.3B parameters
- ✅ **Gradio app on a HF Space** (ZeroGPU, request-driven, `@spaces.GPU` per call)
- ✅ **Off the Grid** — zero cloud APIs at runtime; model weights download once from the HF Hub at build
- ✅ **OpenBMB-central** — MiniCPM-V 4.6 is the engine; VoxCPM2 the voice; all models are OpenBMB
- 🟡 **Llama Champion** — available via the documented `GUARDIAN_CONFIG=full` (llama.cpp GGUF)
- ✅ **Cautious scam framing** — enforced in code (see `tests/test_safety.py`)

> If this project helped or impressed you, a ❤️ on this Space means a lot — it's how
> the Community Choice award is decided.

## Submission links

<!-- HUMAN: fill these before submitting -->
- 🎥 **Demo video (real person using it):** _link goes here_
- 📣 **Social post:** _link goes here_
- 📝 **Field Notes write-up:** [Building Mystery-Mail Guardian](https://huggingface.co/blog/build-small-hackathon/mystery-mail-guardian) (full story) · raw notes in [BUILD_LOG.md](BUILD_LOG.md)
- 🤖 **Agent build trace (Sharing is Caring):** [build-small-hackathon/mystery-mail-guardian-agent-trace](https://huggingface.co/datasets/build-small-hackathon/mystery-mail-guardian-agent-trace)

## Honest limitations

- It can misread poor photos (it says so and asks for a better one).
- It reads **English letters most reliably**. Japanese letters are read well
  enough that the independent scam check still fires; Hindi (Devanagari)
  letters can be under-read by the 1.3B vision model — measured on our Modal
  eval set and documented in the Field Notes. One more reason every result,
  always, says to verify before paying or replying.
- It is not legal, medical, or financial advice — and tells the user that.
- The scam check is a *cautious flag with reasons*, never a verdict. The UI carries a permanent
  reminder: *"I can make mistakes. For anything important, check with someone you trust."*
