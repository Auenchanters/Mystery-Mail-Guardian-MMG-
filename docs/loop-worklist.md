# Autonomous loop worklist — min-max for Build Small judging

> Read by the /loop agent at every wake. **One safe, verified iteration per
> wake**, then reschedule. Owner-approved autonomous operation until the
> deadline below.

## Hard rules (never violate)
- **STOP CONDITION: 2026-06-14 12:00 local.** Check `Get-Date` first thing
  every wake; if past, do the final wrap (HANDOFF + this file), do NOT
  reschedule, end the loop.
- Tests green (`.venv\Scripts\python.exe -m pytest tests -q`) before every push.
- The live Space must stay healthy: after any app-affecting deploy, factory
  restart + verify RUNNING at new sha + one live probe. Judges may visit at
  any time — never leave it broken; if a deploy goes bad, roll back first.
- LEAN config stays deployed (Tiny Titan). No new runtime network calls
  (Off-the-Grid). Param budget untouched. Safety contract changes need tests.
- GPU work goes to Modal (`$env:PYTHONIOENCODING='utf-8'` first), never the
  Space's ZeroGPU quota. Spend cap: $250 credits; we're under $5 — fine.
- NOTHING gets published externally (Hub datasets, social, agent traces)
  without explicit owner consent in chat. Pushing to the existing GitHub/Space
  repos is pre-approved.
- Commit style: see git log; Co-Authored-By Claude Fable 5 trailer; push to
  BOTH `origin master:main` and `space master:main`.

## Backlog (work top-down; mark DONE with date; add discoveries)
1. ~~HF token for Modal containers (secret `huggingface`)~~ DONE 06-12.
2. ~~Re-run `modal_validate.py` post-boost~~ DONE 06-12: GO, all 10 levels
   correct, lottery now reaches warning (was caution pre-boost). Evidence
   refreshed in docs/modal-validation-report.json.
3. ~~Phishing live probe~~ DONE 06-12: `checks/check_live_phishing.py` PASS —
   caution + credentials signal, no link leak. Note: live run surfaced 1
   signal → caution (matrix shows warning when model writes reasons; both
   acceptable, gate is caution|warning).
4. ~~Hi/ja letter-text eval~~ DONE 06-12: 64-letter run. **Finding: model
   under-reads non-Latin letters** — hi/ja gift-card scams → "low" (hi even
   classified "personal"); EN letters unchanged (scam recall 1.0 EN-only).
   Mitigation 1 shipped: Devanagari/JA scam vocabulary in heuristics (98
   tests). Mitigation 2 pending probe: modal_probe.py dumps raw extractions
   → next wake decides (readable=false guard? README honesty line? both?).
4b. ~~Probe analysis + fix~~ DONE 06-12: prompt now demands original-script
   quotes + readable=false over guessing. Result (sim over probe raws):
   **ja scams low → warning (3/3), ja bills stay low; hi unchanged** —
   Devanagari is the model's hard OCR limit, documented in README
   "Honest limitations". scripts/sim_probe_levels.py = offline re-scorer.
4c. ~~Deploy gate~~ DONE 06-12: first gate NO-GO (es scam → caution via
   "within a set time" paraphrase) → urgency pattern generalized (TDD,
   99 tests) → re-gate GO → **live at f516a08**, both live probes PASS,
   phishing now rates WARNING live (was caution). Full chain shipped:
   original-script prompt + hi/ja scam vocabulary + paraphrase urgency.
5. ~~README screenshot gallery~~ DONE 06-12: 2×2 gallery (landing, result,
   softclub egg, mobile) with absolute HF resolve URLs — verified LFS
   serves 200 image/png, renders on both HF card and GitHub.
6. ~~Soft Club a11y re-audit~~ DONE 06-12, all PASS: card ink resolves to
   softclub #393153 (var-scope fix holds), stamp recolors, segments 72px,
   380px = 2×2 grid no h-scroll, zero console errors. Note: ?autorun + ?lang
   race can hide read-aloud in SCREENSHOTS only (lang-change response lands
   after analyze); real sequential use verified correct — not a product bug.
7. ~~Field Notes framing~~ DONE 06-12: "The story in five sentences" intro
   at the top of BUILD_LOG (privacy-is-the-product → safety in code →
   Modal QA flywheel → evals said don't fine-tune).
8. ~~Agent-trace bundle~~ DONE 06-12: docs/agent-trace-draft.md drafted,
   consent-gated — OWNER must approve before any Hub publication.
9. ~~Demo-video kit~~ DONE 06-12: docs/demo-script.md — five beats, assets
   table, recording gotchas (warm-up run, easter-egg reveal order).
10. ~~Robustness v2~~ DONE 06-12: **38/38 honest outcomes** across blur/dim/
    rotate/perspective/shadow/noise ×3 intensities. No photo-quality breaking
    point found; the real limit is script (Devanagari), already documented.
11. ~~LoRA SFT experiment~~ DONE 06-12: loss 2.14→0.03, eval_loss 0.098,
    token acc 98.8%, 5.4M trainable (0.41%), 5m44s/~$0.40 on A10G. Adapter
    in volume `guardian-lora` (checkpoint-22). Train-only, NOT deployed —
    swift-infer A/B vs base = post-hackathon. **BACKLOG COMPLETE (1–11).**

## State notes (update every wake)
- 06-12: loop started. Live Space healthy at 5e547aa-era build (sha 37be779
  app + docs commits). 96 offline tests. Modal secret created. validate.py
  re-run kicked off this wake.
- 06-12 wake 2: matrix GO (item 2), live phishing probe PASS (item 3).
  Next: item 4 (hi/ja letter-text eval on Modal).
- 06-12 wakes 3–6: items 4/4b/4c complete — ML eval, probe, prompt fix,
  multilingual heuristics, urgency paraphrases, gate cycle, LIVE deploy
  f516a08. Next: item 5 (README screenshot gallery for judges).
