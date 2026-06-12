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
5. README judge-pass: embed docs/ui screenshots (landing, result, softclub,
   mobile) into README with one-line captions; verify HF renders LFS images
   (if not, switch those to non-LFS or hosted paths — check on the Space page).
6. A11y re-audit of the softclub palette in the running app (focus rings,
   keyboard path, 380px) — same checklist as BUILD_LOG 06-11 audit.
7. Field Notes polish: BUILD_LOG intro paragraph framing the whole build
   story for judges (elder-first design → safety layer → Modal QA flywheel).
8. Prepare (do NOT publish) the `achievement:sharing` bundle: sanitized agent
   trace summary in docs/agent-trace-draft.md for owner review + consent.
9. Demo-video kit: docs/demo-script.md with shot list (field-guide §6 beats),
   the ?lang= deep-links, mock autorun URLs, WAV file paths.
10. Robustness eval v2: heavier degradations (perspective warp, shadows,
    crumple noise) in letterforge; find the honest breaking point; document
    "take photos in good light" guidance numbers.
11. Stretch (only if all above done + >12h to deadline): LoRA SFT run on
    Modal using dataset sft_targets — train + eval ONLY, never deploy
    pre-judging; write up results either way.

## State notes (update every wake)
- 06-12: loop started. Live Space healthy at 5e547aa-era build (sha 37be779
  app + docs commits). 96 offline tests. Modal secret created. validate.py
  re-run kicked off this wake.
- 06-12 wake 2: matrix GO (item 2), live phishing probe PASS (item 3).
  Next: item 4 (hi/ja letter-text eval on Modal).
- 06-12 wakes 3–6: items 4/4b/4c complete — ML eval, probe, prompt fix,
  multilingual heuristics, urgency paraphrases, gate cycle, LIVE deploy
  f516a08. Next: item 5 (README screenshot gallery for judges).
