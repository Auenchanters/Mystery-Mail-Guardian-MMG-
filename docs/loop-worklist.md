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
2. IN PROGRESS 06-12: re-run `modal_validate.py` — confirm phishing-severity
   boost (worry_reasons now feed heuristics) still GO; record in BUILD_LOG.
3. Extend `checks/check_live_space.py`-style live probe with a phishing
   letter (expect warning) — cheap, one ZeroGPU call, run post-deploy only.
4. Eval v2 on Modal: add Hindi + Japanese letters to letterforge (the model
   reads EN letters; UI lang ≠ letter lang — test hi/ja LETTER TEXT too),
   regenerate dataset, re-run modal_eval, record per-language table.
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
