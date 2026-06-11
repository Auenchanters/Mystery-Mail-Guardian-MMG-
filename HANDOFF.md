# HANDOFF

> Read this at the start of every session. Update it at the end of every session.
> Keep entries terse. Use `path:line` references, not pasted code.

_Last updated: 2026-06-11 (UI-redesign session)_

## Completed
- **Kitchen-Table Post Office UI redesign SHIPPED + LIVE** (plan
  [docs/superpowers/plans/2026-06-11-ui-redesign.md](docs/superpowers/plans/2026-06-11-ui-redesign.md),
  Tasks 4–12 + 7b, all done). Live at sha c4b0fa5, stage RUNNING, Dev Mode off.
  - **Japanese (ja) = 4th language**: full `ui_text` dicts, mock, prompts; JP uses
    OS-native fonts (documented deviation, `assets/fonts/LICENSES.md`).
  - Skin: `assets/guardian.css` + `src/guardian/theme.py` (forced dark both Gradio
    slots); stamp verdict badge in `src/guardian/render.py`; segmented gr.Radio
    `#language-seg`; steps strip; gr.Examples (`cache_examples=False`);
    envelope loader on Gradio 6 `.pending`; `?lang=` deep-link via `head=`
    (`launch(js=)` is dead in 6.17.3 — verified); `?autorun` is MOCK-GATED.
  - **85 offline tests green** (was 66) incl. WCAG AA both palettes, ja parity.
  - A11y audit PASS (keyboard order, 380px, reduced-motion, no console errors) —
    details in BUILD_LOG 06-11 (later) entry, screenshots in `docs/ui/`.
  - **Live checks PASS** on real ZeroGPU: `checks/check_live_space.py` and the new
    rigorous `checks/check_live_letters.py` (bill→low, lottery→caution,
    gift-card scam in ja→warning + 32.8s ja speech, noise→polite error;
    verdict words and scammer contact details never leak).
  - README: `achievement:offbrand` tag, 4-language claims, Off-Brand design section.
  - **git-lfs migration**: HF rejects raw binaries — `*.png`/`*.woff2` now LFS,
    history rewritten (force-pushed origin/main + space/main; old shas invalid).
- Previous sessions: full pipeline + safety layer + trilingual base app, deploy,
  live-fire JSON repairs (see BUILD_LOG).

## In progress
- Nothing mid-flight. **UI FREEZE in effect (owner rule: 2026-06-13 EOD; frozen
  early 06-11).** June 12–15 = demo video, social post, README placeholders only.
- **06-11 hotfix (owner-reported, live at 0b6d0b6):** stacked progress bars →
  `show_progress_on=out_what`; model parroting prompt-schema text as "facts" →
  echo filter in `triage._is_prompt_echo` + prompt hardening + heuristics now
  also scan explanation text. Regression check: `checks/check_land_letter.py`
  (PASS — real facts, no echoes). ⚠️ After any `git lfs migrate`, run
  `git lfs checkout` — the working tree was left as pointer files (broke local
  mock examples; live Space unaffected).

## Known warts (acceptable, documented)
- In ja runs the model sometimes writes key-fact bullets in English; all
  safety-relevant text (headline, signal labels, advice) is template-localized so
  the contract holds. Mock mode always returns the bill/low result regardless of
  image (by design).
- `preview_screenshot` MCP tool times out on this machine — use
  `scripts/shoot_ui.py` (headless Edge over CDP) instead.

## Blocked
- GPU validation of `checks/check_extract.py` / `check_reason.py` on REAL
  photographed letters still needs a human with real mail (consent + photos).
- Headroom on Windows unchanged (no wheel; would need global Rust).

## Next steps (human, per PROJECT.md §9 + field-guide intel)
1. `modal token new` then `.venv\Scripts\modal.exe run modal_validate.py` —
   Modal prize requires actually running it once before submission.
2. Real-person testing + consent, demo video (use `?lang=hi|es|ja` deep-links;
   beats list in plan "NEW INTEL" §6), social post, fill the three
   `<!-- HUMAN -->` README placeholders before June 15.
3. Optional 4th achievement: `achievement:sharing` (publish sanitized agent
   trace as Hub dataset — needs owner consent + secret scrub).
4. ⚠️ Keep LEAN config deployed through judging (full 8B forfeits Tiny Titan).

## Commands used (key)
- `.venv\Scripts\python.exe -m pytest tests -q` (85 passed)
- `.venv\Scripts\python.exe scripts\make_samples.py` (regen example PNGs)
- `.venv\Scripts\python.exe scripts\shoot_ui.py <url> <out.png> [wait_s] [w] [h]`
- `git push space master:main` then factory restart:
  `POST .../api/spaces/build-small-hackathon/Mystery_Mail_Guardian/restart?factory=true`
- `.venv\Scripts\python.exe checks\check_live_letters.py` (post-deploy suite)

## Files touched (this session)
- `src/guardian/{ui_text,config,pipeline,render,samples}.py`, `app.py`,
  `assets/guardian.css`, `assets/samples/*`, `scripts/{make_samples,shoot_ui}.py`,
  `modal_validate.py`, `checks/check_live_letters.py`, `tests/*` (3 files),
  `docs/ui/*`, `README.md`, `BUILD_LOG.md`, `.gitattributes` (LFS), `HANDOFF.md`
