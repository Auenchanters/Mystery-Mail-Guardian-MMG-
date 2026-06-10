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

### Still ahead (humans + GPU required)

1. Run the three `checks/` scripts on real photographed letters on the Space → go/no-go
   on lean vs full quality.
2. Real-person testing (§9), demo video, social post, fill README placeholders.
3. Optional: Off-Brand theming polish, Field Notes publication.
