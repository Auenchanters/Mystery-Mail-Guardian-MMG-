# BUILD_LOG — Mystery-Mail Guardian (Field Notes)

Running log of decisions, dead ends, and learnings. This becomes the Field Notes blog post.

## 2026-06-10 — Day 1+: verify, then build the whole pipeline

### Model facts verified against live HF cards (don't trust memory — good thing, too)

- **MiniCPM-V 4.6** is **1.3B** (SigLIP2-400M vision + Qwen3.5-0.8B LLM), Apache-2.0,
  needs `transformers>=5.7.0`, loaded via `AutoModelForImageTextToText`. GGUF + Ollama
  variants exist. New-to-us API detail: `downsample_mode` ("4x"/"16x" visual-token
  compression) must be passed to **both** `apply_chat_template` and `generate`. We use
  `"4x"` — letters have small print; finer detail beats token savings here.
- **VoxCPM2** is **2B**, Apache-2.0, `pip install voxcpm`, 30 languages incl. Hindi &
  Spanish, ~8GB VRAM. Tokenizer-free diffusion-AR TTS. We use a neutral built-in voice —
  deliberately **no voice cloning**, so no cloning-consent question at all (§9).
- **MiniCPM4.1-8B** is 8B, Apache-2.0, official GGUF → llama.cpp works.
- **ZeroGPU today:** RTX Pro 6000 Blackwell (48GB `large` slice), not the H200 the brief
  mentioned. Pattern confirmed: load models on `cuda` at module scope (CUDA is *emulated*
  outside `@spaces.GPU`; the real GPU attaches inside). Gradio SDK only; Python 3.12;
  duration param per call; quota ~40 min/day for org members.

### Param budget

| Config | Models | Total |
|---|---|---|
| **lean (deployed)** | MiniCPM-V 4.6 + VoxCPM2 | **3.3B** |
| full (env switch) | + MiniCPM4.1-8B GGUF | 11.3B |

Both miles under 32B. `config.assert_param_budget()` refuses to boot over cap and the
total prints in startup logs + UI footer.

### Decision: lean config as deployed default

MiniCPM-V 4.6 does extract + triage + explain in **one structured-JSON pass** (it's a
capable instruction follower, and one pass = one GPU window = quota-friendly +
Tiny-Model angle). The full config exists behind `GUARDIAN_CONFIG=full` if real-person
testing shows the 0.8B LLM's reasoning is too weak.

### Dead end discovered early: llama.cpp × ZeroGPU

ZeroGPU virtualizes CUDA **through PyTorch**. llama.cpp doesn't use PyTorch, so it can't
see the ZeroGPU GPU at all. Full config therefore runs the GGUF reasoner **CPU-side**
(`n_gpu_layers=0`) — works, but adds latency. This is exactly why the Llama Champion
badge is "available, documented, honest" rather than default-on.

### Architecture: safety as code, not vibes

`safety.py` is its own module and the most-tested file in the repo:
- The worry headline ("Should you worry?") is **never model text** — it's one of three
  calm, pre-written templates per language (low/caution/warning). The model can only
  contribute *reasons*.
- Verdict-sounding phrases ("this is a scam", "completely safe") get softened by regex
  post-processing even if the prompt is ignored. Defense in depth.
- **Contact details printed in the letter are stripped from the action steps.** A scam
  letter's entire goal is to make you use *its* phone number. The app's advice always
  routes through channels the person already trusts. This one rule is, we think, the
  single most protective line of code in the project.
- An independent regex heuristic scan (gift cards, OTP, urgency, threats, lottery) runs
  over everything extracted — a second pair of eyes that doesn't trust the model's
  self-reported signals. Union of both decides the worry level: ≥2 signals or
  `suspected_scam` → warning; 1 → caution; 0 → "looks normal, **but always verify**"
  (there is no "safe" state by design).

### Built today

Full pipeline (`extract → triage → explain → speak`, each stage swappable), trilingual
UI (en/hi/es — large type, big buttons, one action per screen, permanent privacy banner
and disclaimer), mock mode (`GUARDIAN_MOCK=1`) so the UI develops/tests without weights,
66 offline unit tests (all passing), three GPU isolation-check scripts for the Space,
Space-ready README with param accounting.

### Verified in a real browser (mock mode)

Upload → analyze → three result cards render; read-aloud produces audio; switching to
Hindi re-localizes the entire UI and the analysis. Found & fixed along the way: Gradio 6
moved `theme`/`css` from `Blocks()` to `launch()`; a duplicate-output bug in the
language-change wiring.

## 2026-06-10 (later) — Deployment + rules audit against the live event page

- **Event-page deltas vs the original brief:** Off-Brand officially requires a custom
  frontend via `gr.Server` (CSS theming alone doesn't count — we don't claim it);
  there's a **Tiny Titan special award for ≤4B total params** (our 3.3B lean config
  qualifies — another reason to ship lean); and a "Sharing is Caring" badge exists for
  published agent traces.
- **Deployed to the hackathon org Space** (build-small-hackathon/Mystery_Mail_Guardian,
  ZeroGPU `zero-a10g`) and pushed the full repo to GitHub. Gotcha discovered: the Space
  had **Dev Mode enabled**, so the container kept serving the old template after the
  push — the repo sha updated but the running app didn't. Fixed with a factory restart
  via the API (`POST .../restart?factory=true`).
- **Modal credits put to honest use:** `modal_validate.py` runs the full pipeline
  (synthetic normal bill + gift-card scam letter) and VoxCPM2 Hindi/English speech on a
  Modal A10G — replacing "borrow a GPU box" for model validation. Build/test-time only;
  the deployed runtime stays 100% local, so Off the Grid is intact. OpenAI Codex credits
  deliberately unused: chasing that prize requires Codex-built commits and would dilute
  the OpenBMB-central thesis (a trade the brief makes explicitly).

## 2026-06-11 — Live-fire debugging: small models write creative JSON

Ran the deployed Space against a synthetic gift-card scam letter via
`checks/check_live_space.py` (real ZeroGPU inference). Three rounds of fixes,
each found by reading the Space's own logs:

1. **Invalid escape** — the model wrote `don\'t` inside a JSON string (`\'` is
   not legal JSON). Fixed with targeted escape repair.
2. **Truncated JSON** — generation hit the token cap mid-explanation, leaving
   the object unterminated. Fixed by salvage-closing open strings/brackets,
   raising the token budget, and demanding a compact explanation object.
3. **Stray punctuation** — next run produced `"...threats".` (period instead
   of comma between fields). Stopped playing regex whack-a-mole and added
   `json-repair` (tiny, offline) as the final parse fallback.

**The safety layer earned its keep in live fire:** for the scam letter the
model suggested *"check with the tax bureau and ensure you pay soon"* — unsafe
advice. Because it arrived in the wrong shape it was discarded, and the
composed result showed the safe fallback step + the always-appended
verification advice instead. The scammer's 1-800 number appeared nowhere.

**Final live result (PASS):** warning card with 4 reasons (3 model + 1
heuristic), key facts ($500, 24 hours, gift cards) extracted from the photo,
19.7s of 48kHz VoxCPM2 speech. Total GPU time per analysis: well inside the
120s budget.

Also learned: ZeroGPU repacks ~8GB of cuda tensors at startup ("ZeroGPU
tensors packing") and pushes don't always trigger rebuilds — the API's
`restart?factory=true` does, reliably.

## 2026-06-11 (later) — Kitchen-Table Post Office: the UI redesign ships

Executed docs/superpowers/plans/2026-06-11-ui-redesign.md end-to-end (Tasks 4–12
plus 7b), TDD throughout: 66 → **85 offline tests**, all green.

### What shipped

- **Japanese (ja) as a fourth language** — full `ui_text` dict (polite です/ます,
  short sentences), all signal/doc-type labels, mock result, prompt name. JP text
  renders via the OS-native stack (Hiragino/Yu Gothic/Meiryo) — a deliberate
  deviation from the plan's "vendor NotoSansJP": CJK woff2 runs to megabytes and
  every target OS ships an excellent native JP font (documented in
  assets/fonts/LICENSES.md).
- **The skin** (assets/guardian.css + guardian/theme.py): forced-dark midnight
  study desk, letter-sheet cards with deckle edges and semantic left borders,
  wax-seal privacy badge, envelope SVG wordmark, postage-stamp verdict badge
  (perforated edge + 3 hand-drawn SVG icons), postmark step rings, segmented
  language buttons (2×2 on phones), envelope-flap analyzing loader with
  localized "Reading your letter…" via gr.Progress.
- **One-tap examples**: synthetic bill + scam letters (assets/samples/, rendered
  by the now-shared guardian/samples.py — modal_validate.py imports it).
  `cache_examples=False` so build never burns GPU.
- **`?lang=hi|es|ja` deep-link** for the demo video; `?autorun` is mock-gated so
  it can never trigger a live GPU run.

### Gradio 6.17.3 field notes (verified against the installed package, not memory)

1. `launch(css_paths=…)` **inlines** the CSS into the page — relative `url()`
   breaks; fonts must go through `/gradio_api/file=` + `allowed_paths`.
2. `launch(js=…)` is accepted but **not executed on page load** — a `head=`
   `<script>` is the reliable path.
3. The busy component gets `.pending` on its inner container (`.html-container`),
   not `.generating` on the block — loader CSS targets that.
4. `gr.Progress()` as a default arg is a safe no-op when the handler is called
   outside an event (tests call handlers directly).

### Accessibility audit (mock app, all PASS)

WCAG AA contrast enforced by tests for BOTH palettes; keyboard order =
language → upload → examples → analyze → read-aloud, visible 3px focus ring;
380×800 = single column, no horizontal scroll, 73px segments / 71px+ buttons;
forced dark verified under a light-scheme OS; Devanagari fully covered by
vendored Noto (fonts.check); zero console errors. Screenshots in docs/ui/
(captured via scripts/shoot_ui.py — headless Edge over CDP, because the
preview screenshot tool kept timing out).

## 2026-06-12 — The Modal matrix earns its keep on its first run

Redeemed the sponsor credits and ran the new **GPU validation matrix on Modal**
(`modal run modal_validate.py`, A10G): 10 analyses — four letter types
including the real-world land-letter regression case, the gift-card scam in
all four languages, and three degraded photos (blur / dim / rotation) — plus
VoxCPM2 speech in en/hi/es/ja. All worry levels landed in their acceptable
ranges; the model read the scam right through every degradation.

**And the harness caught a real safety bug on run #1:** the lottery scammer's
reply address (`claims@prize-winner-intl.example`) surfaced in the *key facts*
card. Contact-detail stripping only covered action steps — the threat model
("the letter wants you to use ITS contact details") applies to every card.
Fixed in `safety.sanitize_fact`/`sanitize_reason` (strip + drop facts that
were essentially nothing but the contact), TDD'd to 91 tests, redeployed.

Timings worth keeping: first analysis 38s (model load), then ~7–9s per
analysis; first speech 151s (load), then ~4s per language. Whole matrix ≈
well under $1 of the $250 credits. Modal usage stays strictly build/test-time —
the deployed runtime is still 100% local (Off the Grid intact).

## 2026-06-12 (later) — Soft Club easter egg, loader redesign, and the eval that said "don't fine-tune"

**Gen X Soft Club easter egg:** selecting 日本語 swaps the whole app to a
pastel Y2K dreamscape — third token palette in theme.py, held to the same
WCAG-AA tests as the others ("an easter egg an elder cannot read is a bug").
One class toggle re-maps our tokens AND Gradio's own theme variables (which
Gradio re-declares at `:root.dark` with literal colors — found in-browser).
Getting the toggle script to run took three attempts, all verified against
rendered pages: `launch(js=…)` never executes in Gradio 6.17.3; a js-only
`demo.load(…)` registers in the config but never runs; `launch(head=…)`
works — but the Space's SSR drops it. Final: head script + `ssr_mode=False`.

**Loader redesign + UX:** one progress overlay instead of one per output
(`show_progress_on`), Gradio's generic bar/timer hidden behind the envelope
flap + breathing localized text; read-aloud button now appears only after a
successful analysis (a wrapper Group's visibility update gets stomped when
its child is updated in the same event — switched to single-component
button updates).

**Modal eval program (the "train it more" answer):** built
`guardian/letterforge.py` (8 parameterized letter factories, gold labels
derived through triage itself, SFT-ready targets) + `scripts/make_dataset.py`
+ `modal_eval.py`. Ran 48 letters × 2 prompt variants on an A10G:

| metric | production | compact |
|---|---|---|
| prompt chars | 2634 | 1111 |
| level accuracy | **0.854** | 0.708 |
| scam recall | **1.0** | **1.0** |
| false alarms | **0.0** | **0.0** |
| amount / deadline hits | 1.0 / 1.0 | 1.0 / 1.0 |
| mean latency | 7.0s | 5.8s |

Decisions the data made for us: (1) the compact prompt saves 58% of prompt
tokens but costs 15 points of level accuracy — **keep the production
prompt**; (2) every "miss" was a phishing scam at *caution* instead of
*warning* — fixed by feeding the model's worry_reasons into the heuristic
scan (offline-tested); (3) **no fine-tune before submission**: safety
behavior is already perfect on the eval distribution (recall 1.0, zero
false alarms), the weak metric (doc-type labeling, 0.42) barely touches
user-facing output, and a model swap two days before judging is risk with
no payoff. The SFT dataset (images + gold JSON targets) is generated and
ready if post-hackathon training is wanted.

### Still ahead (humans + GPU required)

1. Run the three `checks/` scripts on real photographed letters on the Space → go/no-go
   on lean vs full quality.
2. Real-person testing (§9), demo video, social post, fill README placeholders.
3. Optional: Off-Brand theming polish, Field Notes publication.
