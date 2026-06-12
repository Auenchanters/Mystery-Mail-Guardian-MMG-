# Demo video kit — shot list & script (target: 100–120 seconds)

> Field-guide intel: "Storytelling counts as much as the build — no humility,
> sell it." Video may be uploaded directly to the Space as a file.
> Record at 1080p+; phone-filming-a-screen is fine for the human shots.

## Ready-made assets

| Asset | Where |
|---|---|
| Live Space | https://build-small-hackathon-mystery-mail-guardian.hf.space |
| Language deep-links | append `?lang=hi` / `?lang=es` / `?lang=ja` |
| Local mock with auto-demo | `$env:GUARDIAN_MOCK="1"; .venv\Scripts\python.exe app.py` then `/?lang=ja&autorun=1` (b-roll; never burns GPU) |
| 4-language speech WAVs | `modal_artifacts/speech_{en,hi,es,ja}.wav` (48 kHz VoxCPM2) |
| UI stills (b-roll) | `docs/ui/*.png` |
| Synthetic letters to print | run `.venv\Scripts\python.exe scripts\make_samples.py`, print `assets/samples/{bill,scam}.png` |

## Shot list (the five beats the judges were told to look for)

**1. The person (0:00–0:20) — beat (a)**
Real person, real kitchen table, real mail in hand. One line of setup, in
their own words: what confusing or scary mail looks like to them.
> "This is for [name]. Letters like these are how people like her get robbed."

**2. The scam catches fire (0:20–0:50) — beat (b)**
Phone camera on the printed gift-card scam letter → "Read my letter" → the
envelope-flap loader → three paper sheets land with the red warning stamp.
Read two of the reasons out loud. Then tap 🔊 — let VoxCPM2 speak a sentence.
> "Twenty seconds, fully offline: warning stamp, the exact tricks named, and
> the scammer's phone number is nowhere on this screen."

**3. The safety layer story (0:50–1:10) — beat (c)**
One sentence over B-roll (BUILD_LOG on screen or the warning card):
> "In live testing the model once suggested *contacting the tax bureau and
> paying soon*. Our safety layer is code, not a prompt — it threw that advice
> away, kept the warning, and always appends: verify through a number YOU
> already trust."

**4. Built for elders, down to the font (1:10–1:30) — beats (d) + easter egg**
Quick cuts: 56px language buttons (`English | हिन्दी | Español | 日本語`) →
tap हिन्दी, whole UI flips → tap 日本語 and the **Gen X Soft Club easter egg**
melts the screen into pastel Y2K (still WCAG-AA, say it!).
> "The body font is Atkinson Hyperlegible — designed by the Braille Institute
> for low-vision readers. An elder-readability font in an elder-readability
> app. And yes — Japanese has an easter egg."

**5. The close (1:30–1:50) — beat (e)**
Footer on screen (model colophon visible):
> "Every model is OpenBMB — 3.3 billion parameters total, smaller than the cap
> by ten times, 100% local. The letter never leaves the device. All our GPU
> testing ran on Modal — including the eval that caught a privacy bug before
> any human did. Mystery-Mail Guardian: small models, watched closely,
> guarding the people we love."

## Recording gotchas

- ZeroGPU cold start: do one throwaway analysis before recording shot 2 so
  the real take runs warm (~20–40s).
- The easter egg toggles on selecting 日本語 — switch back to English first so
  the flip is visible on camera.
- Don't show the `?autorun` URL on screen (mock-only tooling).
- The disclaimer line must be visible in at least one shot (it always is —
  footer). Keep it: judges read it as a feature, because it is one.
