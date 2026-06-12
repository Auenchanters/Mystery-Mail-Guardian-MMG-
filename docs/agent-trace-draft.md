# Agent trace — Mystery-Mail Guardian (DRAFT, awaiting owner consent)

> **Status: NOT published.** This draft exists for the project owner to review.
> Publishing it as a Hugging Face dataset (+ `achievement:sharing` tag in the
> README) is a one-step action AFTER explicit owner approval in chat.
> Sanitization checklist at the bottom must be re-verified at publish time.

## What this is

Mystery-Mail Guardian was built end-to-end with Claude Code (Anthropic) as the
hands and a human owner as the director. This trace is the honest, sanitized
record of how that collaboration actually worked — the prompts that steered it,
the loop that ran it, and the evidence trail it left behind.

## How the build was driven

- **Planning first:** every major phase started as a written plan
  (`docs/superpowers/plans/`) with TDD steps, verified against live docs
  rather than model memory (Gradio 6 API drift caught this way twice).
- **The owner steered with short prompts**, e.g.:
  - "the loading icon is broken … I provided this image and it gave this
    output which I think is wrong" → led to the prompt-echo discovery (the
    1.3B model parroting our JSON schema back) and the single-overlay loader.
  - "make an Easter egg when the user switches to Japanese" → the Gen X Soft
    Club palette, held to the same WCAG-AA tests as the main themes.
  - "train the model more using our Modal credits" → answered with evidence
    instead of obedience: a labeled synthetic-letter dataset + eval matrix
    that showed safety behavior was already at ceiling, so no fine-tune
    shipped — the data made the call.
  - "enter a state of loop-craft … keep improving until June 14" → a
    self-rescheduling build loop with a committed worklist
    (`docs/loop-worklist.md`), one verified iteration per wake.
- **Every iteration had the same gate:** offline tests green → Modal GPU
  validation where behavior changed → deploy → live probes against the
  running Space → commit with evidence.

## What the trace shows (highlights)

1. **Live fire beats simulation.** Three JSON-repair bugs and one genuinely
   unsafe model suggestion ("check with the tax bureau and ensure you pay
   soon") were caught on the deployed Space; the safety layer discarded the
   bad advice by construction (BUILD_LOG 06-11).
2. **The QA harness caught real bugs on its first runs.** Run #1 of the Modal
   matrix found a scammer's reply address leaking through key facts; the
   multilingual eval found Devanagari/Japanese scam letters under-flagged.
   Both fixed, gated, and redeployed the same day (BUILD_LOG 06-12).
3. **A NO-GO gate did its job.** A prompt improvement regressed one Spanish
   case ("within a set time" paraphrase); the deploy was blocked until the
   urgency heuristic was generalized with tests, then re-gated to GO.
4. **Tooling archaeology, documented:** `launch(js=)` dead in Gradio 6.17.3,
   js-only `demo.load` registered-but-never-run, `head=` dropped by Space
   SSR — resolved with `head=` + `ssr_mode=False` (BUILD_LOG 06-12).

## Companion artifacts (already public in the repo)

- `BUILD_LOG.md` — the full field notes, including dead ends
- `docs/modal-validation-report.json`, `docs/modal-eval-report.json` — GPU
  evidence as committed JSON
- `docs/loop-worklist.md` — the autonomous loop's rules and backlog, as run
- Git history — every step, with co-authorship trailers

## Sanitization checklist (verify before publishing)

- [x] No API keys, tokens, or secret values (HF token lives only in the local
      cache + a Modal secret; never in the repo)
- [x] No real personal data — every letter in datasets/examples is synthetic;
      phone numbers use the reserved 555-01XX range
- [x] No private URLs or credentials in logs quoted here
- [ ] Owner has read this draft and approves publication
- [ ] `achievement:sharing` tag added to README only after upload
