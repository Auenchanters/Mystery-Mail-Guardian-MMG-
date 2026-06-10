# Mystery-Mail Guardian — Build Brief for Claude Code

> **How to use this file:** Save it in the repo root as `PROJECT.md`. Start your Claude Code session with: *"Read PROJECT.md in full, then do the FIRST TASK at the bottom. Do not start building the full pipeline until the Day-1 de-risk is green and you've reported back."* Re-paste or `@PROJECT.md` whenever context resets.

---

## 0. Your role and the one-sentence mission

You are Claude Code, building a complete, working **Gradio app** that we will submit to the **Hugging Face × Gradio "Build Small Hackathon."** The app is **Mystery-Mail Guardian**. The mission: **win the "Backyard AI" track** by building a genuinely useful, privacy-first tool that a specific real person actually uses — and stack as many sponsor/bonus awards as possible without compromising that.

Optimize for the judging rubric, not for flash. Every decision should serve: *the problem is specific and real → a real person actually used it → the small-model/local constraint is an honest fit → the app is polished.*

---

## 1. The event — full context (self-contained)

- **What it is:** A hackathon hosted by Hugging Face + Gradio. The whole theme is **"build small"** — go back to the era of small, tinkerable models instead of giant cloud APIs. They explicitly do **not** want "yet another B2B SaaS."
- **Dates:** Hack window **June 5–15, 2026**. Submissions close **June 15, 2026**. (We are inside the window.)
- **Two tracks:**
  - **Backyard AI** ← *this is ours.* Solve a real problem for someone you actually know. Judged on: (1) problem is specific and real, (2) **the person actually used it**, (3) honest fit between the problem and the small-model constraint, (4) polish of the Gradio app.
  - Thousand Token Wood — whimsical/joyful. (Not ours.)
- **Three hard rules (non-negotiable):**
  1. **Total model parameters ≤ 32 billion.** This is the *sum of all distinct models loaded* (total params, not active). Multiple small models are fine as long as the sum is under 32B.
  2. The submission **must be a Gradio app hosted as a Hugging Face Space** (Gradio SDK or Docker, but a Gradio app underneath).
  3. A short **demo video** and a **social-media post** are required parts of the submission (links go in the Space README).
- **Compute:** Hosted free on **ZeroGPU** (an H200 slice allocated *per call* and released after — roughly ~40 min of GPU compute/day for org members). This means the app **must be request-driven** (one photo in → one result out). **No always-on streaming, no continuous background loops.**
- **Credits available:** ~$250 Modal, ~$20 Hugging Face, ~$100 OpenAI Codex per participant (we will not need most of these).
- **Sponsor prize categories we care about:**
  - **OpenBMB — $10,000 cash** (split across both tracks). Eligibility: a **MiniCPM-family model must be a *central* part of the app.** Ours is — MiniCPM-V is the engine. ✅
  - Modal ($20k credits, requires using Modal for training/inference + a README note), NVIDIA (needs a Nemotron model — *not* us), OpenAI (needs Codex commits — *not* our focus), Black Forest Labs (FLUX image models — *not* needed for this idea).
- **Bonus badges (each adds points):**
  - **Off the Grid** — no cloud APIs at runtime; the model runs locally in the Space. ← **This is our killer feature and our entire thesis. Mandatory.**
  - **Llama Champion** — model runs via the **llama.cpp** runtime (GGUF). ← Target this.
  - **Well-Tuned** — uses a fine-tuned model published on HF. (Optional stretch — see §5.)
  - **Off-Brand** — custom frontend beyond default Gradio look. (Nice-to-have.)
  - **Field Notes** — a blog post / write-up about what we built and learned. ← Easy; keep a build log from day one.
  - There is also a **Tiny-Model** angle — keeping total params very low is rewarded; our lean config leans into this.

**Differentiation to state explicitly in the README and demo:** This is **NOT a generic OCR/document parser.** It is **scam-and-action triage for a specific vulnerable person, running fully on-device** — because these documents (financial, legal, medical) are exactly the ones people refuse to upload to a cloud API. The privacy/local angle *is* the product.

---

## 2. The product — Mystery-Mail Guardian

**One line:** Photograph a confusing letter, bill, or form; the app reads it **locally**, explains in plain language (in the person's native language) what it is, flags whether it shows signs of a scam, says what to actually do next, and reads the summary aloud.

**Who it's for (name the real person in the README/video):** an elderly parent/grandparent or an immigrant elder who struggles with official English-language mail, dense bureaucratic language, or telling real bills from scams. (The builder must choose a real person, get their consent, have them use it, and film it.)

**Core user flow (keep it dead simple — the user may be 70+):**
1. **Snap or upload** a photo of the document.
2. App extracts the text and layout **on-device**.
3. App produces, in the chosen language, at a **low reading level**:
   - **What this is** (e.g., "an electricity bill," "a letter from the tax office," "a marketing flyer pretending to be a bill").
   - **The key facts** — who sent it, what they want, any amount, any deadline.
   - **Scam check** — a *cautious flag with reasons*, never a verdict (see §7).
   - **What to do next** — concrete, safe steps.
4. **Read it aloud** with one big button.
5. **Language toggle** so the elder reads/hears it in their language.

**The privacy promise, shown in the UI:** "Your documents never leave this device. Everything runs on a small model, locally." This sentence is the soul of the project — make it visible.

---

## 3. Prize/badge strategy for this specific build

- **Win Backyard AI** by nailing the rubric: real person, real use (filmed), honest local-model fit, polish.
- **OpenBMB $10k:** MiniCPM-V is the central engine → eligible. Keep it central and say so.
- **Off the Grid:** everything local, zero cloud calls at runtime. **Do not add any dependency that phones home at inference time** — if one does, flag it to the human.
- **Llama Champion:** run the models via **llama.cpp (GGUF)** where supported.
- **Field Notes:** maintain `BUILD_LOG.md` as you go; it becomes the blog post.
- **Tiny-Model:** prefer the leanest config that still works well (see §5).
- **Deliberately skipped:** NVIDIA (would force a Nemotron model and break OpenBMB-central), OpenAI Codex (not our build tool), Black Forest Labs / image generation (no image-gen needed here), Modal (no training needed — *optional* stretch in §5). We are trading breadth for a clean, honest, winnable Backyard entry. Do not bolt on unrelated sponsor tech just to chase badges; it dilutes the rubric fit.

---

## 4. Hard constraints (check these on every commit)

- [ ] **Total model params ≤ 32B** — print the running total in the README and logs.
- [ ] **Gradio app, hosted as a Hugging Face Space.**
- [ ] **Fully local / Off the Grid** — no cloud API calls at runtime. No OpenAI/Anthropic/Google APIs, no remote inference endpoints, no hosted OCR. (Building *with* Claude Code is fine — the rule is about the *deployed app's runtime*.)
- [ ] **Request-driven**, not streaming or always-on (ZeroGPU quota).
- [ ] **Demo video + social post** links in the README before submission.

---

## 5. Technical stack & architecture

**Verify every model's current details against its live Hugging Face model card / docs before coding — do not rely on training memory for params, APIs, or llama.cpp support. Report what you find.**

**Models (target):**
- **MiniCPM-V 4.6** (~1.3B, vision/OCR/layout/document understanding) — **central engine.** Reads the photo → structured text + document cues. (OpenBMB eligibility hinges on this being central.)
- **MiniCPM4.1-8B** (text reasoning) — plain-language rewriting + scam-signal reasoning + next-step generation, in the target language. Run via **llama.cpp GGUF** → Llama Champion.
- **VoxCPM2** (~2B, multilingual TTS, OpenBMB family) — reads the summary aloud; supports many languages and voice design.

**Two configs — test both, pick by quality:**
- **Lean (~3.3B): MiniCPM-V 4.6 + VoxCPM2 only**, letting MiniCPM-V do the reasoning too. Maximizes the Tiny-Model angle and simplicity. Try this first.
- **Full (~11.3B): add MiniCPM4.1-8B** for stronger plain-language + scam reasoning if the lean config's reasoning is weak. Still far under 32B.

**Pipeline (request-driven, one pass):**
1. **Input** — `gr.Image` (camera/upload).
2. **Extract** — MiniCPM-V: OCR + layout → structured text, sender, document-type cues. Wrap inference to load/run efficiently under ZeroGPU (`@spaces.GPU`, load per request or pre-warm at module scope per ZeroGPU docs — verify the current ZeroGPU pattern).
3. **Triage** — classify type (utility bill, bank, government/tax, medical, marketing, **suspected scam**); extract who/what/amount/deadline/requested-action; detect scam signals (urgency/threats, payment via gift cards/crypto/wire, requests for passwords/OTP/SSN, sender/domain mismatch, "too good to be true," pressure to act now, contact info that bypasses official channels).
4. **Explain** — produce, in the chosen language at a low reading level: *what this is*, *key facts*, *scam check (cautious, with reasons)*, *what to do next*.
5. **Speak** — VoxCPM2 reads the summary aloud (clear, calm voice; adjustable pace).
6. **Output UI** — big plain summary, the scam flag + reasons, the suggested action, a large "Read aloud" button, a language toggle, and the visible privacy statement.

**Runtime:** Prefer **llama.cpp GGUF** for the text model (Llama Champion) and confirm current GGUF/llama.cpp support for MiniCPM-V 4.6 and VoxCPM2; fall back to transformers where needed. Everything local in the Space.

**Optional stretch (only if ahead of schedule):** fine-tune a tiny scam-signal classifier or a doc-type classifier **on Modal**, publish it on HF → grabs **Well-Tuned** + the **Modal** category + a README note. Do **not** attempt this until the core app works end-to-end and a real person has used it.

---

## 6. UX spec (designed for a 70-year-old, not a developer)

- Large fonts, high contrast, minimal steps, no jargon.
- One primary action per screen ("Take a photo of your letter" → result).
- Result laid out as: **What this is** → **Should you worry?** (the scam flag) → **What to do** → 🔊 **Read aloud**.
- Prominent **language selector** (start with the real person's language + English).
- Always-visible privacy line: *"Nothing leaves this device."*
- Optional **Off-Brand** custom styling (calm, accessible, large-tap-target theme) — nice-to-have, after function works.

---

## 7. Safety & framing — REQUIRED, bake into prompts AND UI

This protects a vulnerable user and is also what earns judge trust. Non-negotiable:

- **Never output a definitive verdict on scams.** Do not say "this is safe" or "this is a scam." Use cautious language: *"This looks like a normal bill from X, but always verify,"* or *"⚠️ This shows several warning signs often seen in scams: [list]. Be careful."* Always list the *reasons*.
- **Always recommend independent verification** through official channels the person already trusts (e.g., the number on the back of their bank card, the official website typed by hand) — **never** the contact details printed in the suspicious document.
- **No definitive legal, medical, or financial advice.** For those, summarize plainly and say *"check with your doctor / a lawyer / the official institution."*
- **Privacy is real, not marketing:** ensure no document content is sent anywhere at runtime. If any library makes a network call during inference, stop and flag it.
- **Tone:** calm, reassuring, never alarmist; never condescending to the user.
- Add a short, gentle disclaimer in the UI: *"I can make mistakes. For anything important, check with someone you trust."*

---

## 8. Build order (10 days; you write code, the human does §9)

- **Day 1 — DE-RISK (gate before building):** scaffold repo, `README.md`, `PROJECT.md` (this file), `BUILD_LOG.md`. Then prove each model **in isolation** on the target runtime: does MiniCPM-V correctly read a *real photographed letter*? Does VoxCPM2 sound clear in the target language? Does the reasoning model produce safe, plain summaries? Confirm the **param total** and that it **runs within ZeroGPU limits.** Report sample outputs and a go/no-go. **Do not proceed until green.**
- **Days 2–4:** build the pipeline (extract → triage → explain → speak) with the §7 safety framing as structured prompts; handle blurry/low-quality photos and non-document images gracefully.
- **Days 4–6:** Gradio UI per §6 — accessible layout, language toggle, read-aloud, privacy line; optional custom theme.
- **Days 6–7:** deploy to the **HF Space (ZeroGPU)**; tune per-request loading for the quota; full end-to-end test.
- **Days 7–9:** **real-person testing** (human-led) → iterate on clarity, accuracy, and scam heuristics; keep writing `BUILD_LOG.md`.
- **Days 9–10:** human records the **demo video** (the real person using it) + writes the **social post**; you finalize the README (model list + **param total**, privacy statement, "what this is NOT," demo + social links); buffer for fixes.

---

## 9. What ONLY the human does (not you, Claude Code)

- Create the HF account, **join the hackathon org**, create the Space, set up tokens/secrets, claim credits.
- Choose a **real person**, get their **consent**, have them **use the app**, and **film** it. (This is the single most important rubric item — "the person actually used it.")
- Record the **demo video** and write/post the **social media** post.
- Final **safety + accuracy + taste review** of real outputs before submission.
- Any **voice-clone consent** if VoxCPM2 cloning is used (prefer a neutral designed voice to avoid this entirely).

---

## 10. How I want you (Claude Code) to work

- **Read this whole brief first.** Then do the FIRST TASK below — nothing more — and report back.
- **Verify model facts** (params, APIs, llama.cpp/GGUF support, ZeroGPU patterns) against current HF cards/docs; don't trust memory. Tell me what you find.
- **De-risk before building.** If a model can't read a real letter or won't run in the quota, surface it on Day 1, not Day 8.
- **Guard the constraints automatically:** keep total params under 32B and print the running total; never introduce a runtime cloud call or a dependency that phones home — if you must, stop and ask.
- **Keep it modular:** each pipeline stage (extract / triage / explain / speak) swappable, so we can switch lean↔full config easily.
- **Implement the §7 safety layer explicitly** as its own module; it is a feature, not an afterthought.
- **Maintain `BUILD_LOG.md`** (decisions, dead ends, learnings) — it becomes the Field Notes blog.
- **Ask before** adding heavy dependencies, changing the model set, or anything that risks the 32B cap or the off-grid rule.
- Write a clear **README** with: what it is, who it's for, the privacy thesis, the model list + total params, how to run, "what this is NOT," and slots for the demo video + social post links.

---

## 11. Definition of done (submission checklist)

- [ ] Gradio app **live on a Space under the hackathon org.**
- [ ] **≤ 32B total params**, stated in the README.
- [ ] **Fully local / Off the Grid** — verified no runtime cloud calls.
- [ ] Works on **real photographed letters** in **≥ 2 languages** (English + the person's language).
- [ ] **Cautious scam framing** everywhere (no verdicts; reasons + verify-independently).
- [ ] **Read-aloud** works.
- [ ] Text model via **llama.cpp (GGUF)** for Llama Champion (if supported).
- [ ] **Demo video** (real person using it) + **social post** linked in README.
- [ ] **Field Notes** write-up published.
- [ ] README names the real person/problem and states **"this is not a generic OCR parser."**

---

## FIRST TASK (do this now, then stop and report)

1. Scaffold the repo: `README.md`, `PROJECT.md` (this file), `BUILD_LOG.md`, a clean Python project, and a `requirements.txt`.
2. Look up and report the **current** facts for **MiniCPM-V 4.6**, **MiniCPM4.1-8B**, and **VoxCPM2**: exact parameter counts, license, llama.cpp/GGUF availability, and how to run each locally. Compute the **total params** for both the lean and full configs.
3. Confirm the **ZeroGPU** usage pattern (how to wrap inference, how per-request loading works, quota implications).
4. Write three tiny **isolation test scripts** (one per model) so we can verify: MiniCPM-V reads a real letter photo, the reasoning step produces a safe plain summary, and VoxCPM2 speaks it.
5. **Report back** with: the param totals, what you verified vs. couldn't, any constraint risks (32B cap, off-grid, ZeroGPU), and a recommended lean-vs-full call. **Do not build the full pipeline yet.**
