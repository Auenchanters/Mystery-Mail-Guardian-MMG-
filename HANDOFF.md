# HANDOFF

> Read this at the start of every session. Update it at the end of every session.
> Keep entries terse. Use `path:line` references, not pasted code.

_Last updated: 2026-06-10_

## Completed
- **Full Mystery-Mail Guardian app built end-to-end** (PROJECT.md §5–§7):
  - Pipeline: `src/guardian/` — extract (MiniCPM-V 4.6) → triage → explain
    (optional MiniCPM4.1-8B GGUF, `GUARDIAN_CONFIG=full`) → speak (VoxCPM2).
  - Safety layer `src/guardian/safety.py`: template worry headlines, verdict
    softening, contact-detail stripping, always-on verification advice.
  - Trilingual UI (en/hi/es) in `app.py` + `src/guardian/ui_text.py`; ZeroGPU
    `@spaces.GPU` wiring with local no-op shim; mock mode `GUARDIAN_MOCK=1`.
  - 66 offline tests in `tests/` — all passing (`.venv\Scripts\python.exe -m pytest tests -q`).
  - Browser-verified in mock mode: analyze, read-aloud, Hindi toggle all work.
  - `README.md` = HF Space card (sdk gradio 6.17.3, py 3.12) with param table.
  - Model facts verified vs live HF cards 2026-06-10 (see BUILD_LOG.md):
    lean = 3.3B, full = 11.3B, cap 32B. Param guard: `src/guardian/config.py:assert_param_budget`.
- Project-local tooling (.venv, scripts/, code-review-graph) from previous session.

## In progress
- Nothing mid-flight. **Live Space verified end-to-end 2026-06-11**: scam letter
  → warning card + reasons + safe steps + 19.7s VoxCPM2 speech, via
  `checks/check_live_space.py` (PASS). Running build: commit 5256af1.

## Blocked
- **GPU validation needs the Space (or any CUDA box):** run `checks/check_extract.py`
  on real photographed letters, `checks/check_speak.py hi`, `checks/check_reason.py`.
  No GPU on this Windows machine; weights too heavy to test locally.
- Headroom still blocked on Windows (no wheel; needs global Rust) — unchanged.

## Next steps (human, per PROJECT.md §9)
1. ~~Create HF Space~~ DONE — deployed to build-small-hackathon/Mystery_Mail_Guardian
   (ZeroGPU zero-a10g); GitHub repo Auenchanters/Mystery-Mail-Guardian-MMG- synced.
   Remotes configured: `space` (HF) and `origin` (GitHub); push auth via cached HF
   token / Windows credential manager. NOTE: Space has Dev Mode ON — pushes may not
   redeploy; use factory restart (see BUILD_LOG) or turn Dev Mode off.
2. `modal token new` (browser login, one time), then
   `.venv\Scripts\modal.exe run modal_validate.py` → GPU validation report +
   Hindi/English WAVs in modal_artifacts/ (uses the $250 Modal credits).
3. Real-person testing, consent, demo video, social post; fill the three
   `<!-- HUMAN -->` placeholders in README.md before June 15.
4. Optional: publish BUILD_LOG.md as Field Notes; consider "Sharing is Caring" badge
   (publish sanitized agent traces — review for secrets first).

## Commands used (key)
- `uv pip install --python .venv\Scripts\python.exe -r requirements-dev.txt`
- `.venv\Scripts\python.exe -m pytest tests -q`  (66 passed)
- `$env:GUARDIAN_MOCK="1"; .venv\Scripts\python.exe app.py`  (local UI on :7860)

## Files touched
- `app.py`, `src/guardian/*` (9 modules), `tests/*` (6 files), `checks/*` (3 scripts),
  `requirements.txt`, `requirements-dev.txt`, `README.md`, `BUILD_LOG.md`,
  `.gitignore`, `.gitattributes`, `HANDOFF.md`
