# Mystery-Mail Guardian — "Kitchen-Table Post Office" UI Redesign Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement
> this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> (Note: the project owner asked for **no sub-agents** — execute inline.)

**Goal:** Replace the stock-Gradio look with a warm, postal-themed, accessibility-first UI
that is genuinely fun to look at — judged-app polish — without touching the verified
pipeline, the safety layer, or any hackathon rule.

**Architecture:** Pure presentation-layer change. A custom `gr.themes.Base` subclass +
one vendored CSS file + richer HTML in the existing `render.py`/`app.py` HTML blocks.
Handlers (`on_analyze`, `on_speak`, `on_language_change`) keep their signatures; the
pipeline and safety modules are untouched. Everything (fonts, icons, sample images) is
**vendored into the repo** — zero runtime fetches, so Off-the-Grid stays bulletproof.

**Tech Stack:** Gradio 6.17.3 theming API, hand-written CSS (no frameworks), inline SVG,
Atkinson Hyperlegible + Noto Sans Devanagari (vendored WOFF2), pytest, mock mode +
Claude preview tools for visual verification.

---

## Non-negotiables (rules + project constraints — recheck at every task)

1. **No new runtime network calls.** Fonts/icons/textures are repo files, never CDN.
2. **Pipeline untouched:** `src/guardian/{pipeline,safety,triage,extract,explain,speak,prompts,config}.py` are read-only for this plan (except `ui_text.py` string additions).
3. **Param total unchanged (3.3B)** — no new models, Tiny Titan stays valid.
4. **Request-driven** — no polling/streaming additions.
5. **§7 tone:** warm and dignified, never childish. The user is 70+, not a toddler.
6. **Accessibility beats decoration** every time the two conflict: WCAG AA contrast,
   ≥48px tap targets, ≥18px base text, `prefers-reduced-motion` respected.
7. **UI freeze 2026-06-13 EOD** — June 14–15 belong to the demo video and submission.
8. Deploy gotchas (learned 06-10/11): pushes don't reliably rebuild the Space — use
   `POST .../restart?factory=true`; never re-enable Dev Mode (it skips requirements.txt).

---

## Design concept — "The Kitchen-Table Post Office"

The app should feel like a kind neighbor reading your mail with you at a sunny kitchen
table, not like a developer dashboard. Default is a **warm paper-light** theme (elders
read high-contrast-on-light better); dark mode supported via tokens.

### Design tokens (exact values — single source of truth)

| Token | Light | Dark | Used for |
|---|---|---|---|
| `--paper` | `#FAF4E8` | `#1E1B16` | page background (warm cream) |
| `--sheet` | `#FFFDF7` | `#2A2620` | cards ("paper sheets") |
| `--ink` | `#2B2A33` | `#EDE6D6` | body text (contrast vs sheet: 12.6:1 light) |
| `--ink-soft` | `#5A5550` | `#B8AE9C` | secondary text |
| `--postal-red` | `#C84B31` | `#E07A5F` | primary buttons, stamp accents |
| `--postal-blue` | `#3D5A80` | `#8EB1D9` | links, secondary accents, postmark |
| `--seal-green` | `#3A7D44` | `#7BC88A` | privacy seal, low-worry label |
| `--amber` | `#B97700` | `#E8B339` | caution label |
| `--alert-red` | `#B3362B` | `#F08A80` | warning label |
| `--line` | `#E4D9C3` | `#3E382E` | borders, deckle edges |

Type scale: body 19px/1.6; card text 21px; H1 40px; buttons 22px bold; footer 16px.
Radius: cards 4px (paper is square-ish, not bubbly), buttons 12px. Shadows: soft,
single-direction (`0 2px 8px rgba(43,42,51,.08)`), like paper on a table.

### Typography (vendored — this is also a story for the README/demo)

- **Atkinson Hyperlegible** (body + UI): designed by the Braille Institute specifically
  for low-vision readers. Free, OFL license. *An elder-readability font in an
  elder-readability app — say this out loud in the demo.*
- **Noto Sans Devanagari** (Hindi fallback chain): OFL.
- Files: `assets/fonts/AtkinsonHyperlegible-{Regular,Bold}.woff2`,
  `assets/fonts/NotoSansDevanagari-{Regular,Bold}.woff2` + `assets/fonts/LICENSES.md`.
- `font-family: "Atkinson Hyperlegible", "Noto Sans Devanagari", system-ui, sans-serif;`

### Visual motifs (all inline SVG / pure CSS — no image files except samples)

1. **Header**: envelope wordmark (inline SVG, two-tone postal red/blue), tagline, and the
   privacy promise restyled as a **green wax-seal badge** with a 🔒→shield SVG — the
   soul of the project gets the most distinctive visual on the page.
2. **Result cards as letter sheets**: `--sheet` background, 1px `--line` border, a subtle
   CSS-gradient "deckle" top edge, slight rotation on the first card (`rotate(-0.4deg)`)
   for a hand-placed feel (rotation removed under `prefers-reduced-motion`).
3. **Worry verdict as a postage stamp**: perforated-edge stamp (CSS `radial-gradient`
   border trick) in seal-green / amber / alert-red with a big icon (✓-ish "looks usual" /
   ⚠ / 🚨 equivalents as inline SVG) + the existing template headline.
4. **Step numbers**: circled 1·2·3 postmark-style rings guiding photo → read → listen.
5. **Motion** (CSS only, each ≤400ms, all gated behind `prefers-reduced-motion`):
   - results: cards fade-slide up, staggered 0ms/120ms/240ms (`animation-delay`)
   - analyzing: envelope flap opens + three dots pulse, with localized "Reading your
     letter…" text
   - buttons: 2px lift + shadow on hover/focus; visible 3px `--postal-blue` focus ring
6. **Language picker**: the dropdown becomes three **large segmented buttons**
   (`English | हिन्दी | Español`) — one tap, always visible, 56px tall. No flags
   (flags ≠ languages).
7. **Footer**: disclaimer line stays prominent; model list set in small-caps "colophon"
   style like the printer's note on real stationery.

---

## File map

- Create: `src/guardian/theme.py` — tokens dict + `GuardianTheme(gr.themes.Base)` + contrast helper
- Create: `assets/guardian.css` — all component CSS (replaces the `CSS` string in app.py)
- Create: `assets/fonts/*.woff2` + `assets/fonts/LICENSES.md`
- Create: `src/guardian/samples.py` — synthetic letter renderer (moved from `modal_validate.py`, shared)
- Create: `scripts/make_samples.py` — writes `assets/samples/{bill,scam}.png`
- Create: `tests/test_theme.py`
- Modify: `app.py` — layout (segmented language, steps, examples, css_paths/theme in `launch()`)
- Modify: `src/guardian/render.py` — letter-sheet cards + stamp badge
- Modify: `src/guardian/ui_text.py` — new strings ×3 languages (step labels, analyzing text, sample captions)
- Modify: `modal_validate.py` — import renderer from `guardian.samples`
- Modify: `tests/test_app.py`, `tests/test_pipeline.py` — assertions for new markup
- Untouched: everything else in `src/guardian/`

---

## Task 0: Research checkpoint (do FIRST — decides Option A vs B)

**No code. Verify against live docs; do not trust memory.**

- [ ] Fetch Gradio 6 docs for **`gr.Server`** (the event page says Off-Brand badge =
  "custom frontend via `gr.Server`"). Determine: what it is, whether a custom frontend
  can reuse our existing `/gradio_api` endpoints, and whether it's ZeroGPU-compatible.
- [ ] Verify Gradio 6.17 `launch()` signature for `css` / `css_paths` / `theme` params
  (we already know `Blocks(css=…)` is deprecated) and whether `gr.Radio` supports
  `elem_classes` styling sufficient for the segmented control.
- [ ] **Decision gate:** Option A (this plan: deep theme + CSS, no badge) is the
  committed path. Option B (`gr.Server` custom frontend, earns **Off-Brand**) is a
  stretch **only if** (a) docs show it cleanly wraps existing endpoints, (b) Tasks 1–9
  are done and deployed by June 13 noon. Otherwise skip B without regret — Backyard AI
  judges polish, not badge count.
- [ ] Record findings + decision in `BUILD_LOG.md`.

## Task 1: Design tokens + automated contrast tests (TDD the palette)

**Files:** Create `src/guardian/theme.py`, `tests/test_theme.py`

- [ ] **Step 1: failing test** — every text/background pair must clear WCAG AA:

```python
# tests/test_theme.py
from guardian.theme import TOKENS, contrast_ratio

AA_PAIRS = [  # (foreground, background, minimum)
    ("ink", "paper", 4.5), ("ink", "sheet", 4.5), ("ink_soft", "sheet", 4.5),
    ("postal_red", "paper", 3.0),   # large text / UI components
    ("seal_green", "sheet", 3.0), ("amber", "sheet", 3.0), ("alert_red", "sheet", 3.0),
]

def test_light_palette_meets_wcag_aa():
    for fg, bg, minimum in AA_PAIRS:
        ratio = contrast_ratio(TOKENS["light"][fg], TOKENS["light"][bg])
        assert ratio >= minimum, f"{fg} on {bg}: {ratio:.2f} < {minimum}"

def test_dark_palette_meets_wcag_aa():
    for fg, bg, minimum in AA_PAIRS:
        ratio = contrast_ratio(TOKENS["dark"][fg], TOKENS["dark"][bg])
        assert ratio >= minimum, f"{fg} on {bg}: {ratio:.2f} < {minimum}"
```

- [ ] **Step 2:** run `pytest tests/test_theme.py -q` → FAIL (module missing)
- [ ] **Step 3: implement** tokens + WCAG math:

```python
# src/guardian/theme.py
"""Design tokens + Gradio theme for the Kitchen-Table Post Office look."""
TOKENS = {
    "light": {"paper": "#FAF4E8", "sheet": "#FFFDF7", "ink": "#2B2A33",
              "ink_soft": "#5A5550", "postal_red": "#C84B31", "postal_blue": "#3D5A80",
              "seal_green": "#3A7D44", "amber": "#B97700", "alert_red": "#B3362B",
              "line": "#E4D9C3"},
    "dark": {"paper": "#1E1B16", "sheet": "#2A2620", "ink": "#EDE6D6",
             "ink_soft": "#B8AE9C", "postal_red": "#E07A5F", "postal_blue": "#8EB1D9",
             "seal_green": "#7BC88A", "amber": "#E8B339", "alert_red": "#F08A80",
             "line": "#3E382E"},
}

def _luminance(hex_color: str) -> float:
    rgb = [int(hex_color.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]

def contrast_ratio(fg: str, bg: str) -> float:
    l1, l2 = sorted((_luminance(fg), _luminance(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)
```

- [ ] **Step 4:** run again → PASS. **If any pair fails, darken/lighten that token until
  it passes — the test defines the palette, not the mockup.** Update the table above.
- [ ] **Step 5:** `git commit -m "feat(ui): design tokens with WCAG AA contrast tests"`

## Task 2: Vendor the fonts

**Files:** `assets/fonts/*.woff2`, `assets/fonts/LICENSES.md`

- [ ] Download WOFF2s (build-time only, by the developer, committed to git):
  Atkinson Hyperlegible Regular/Bold (from the official Braille Institute release or
  google/fonts GitHub repo), Noto Sans Devanagari Regular/Bold. ~4 files, ~200KB total.
- [ ] Write `assets/fonts/LICENSES.md` naming both OFL licenses + sources.
- [ ] Verify each file is real WOFF2: `python -c "print(open('assets/fonts/AtkinsonHyperlegible-Regular.woff2','rb').read(4))"` → `b'wOF2'`
- [ ] `git commit -m "feat(ui): vendor Atkinson Hyperlegible + Noto Devanagari (OFL)"`

## Task 3: GuardianTheme class

**Files:** Modify `src/guardian/theme.py`, `app.py` (launch call only)

- [ ] **Step 1:** add to `theme.py` (import gradio lazily — tests without gradio still pass):

```python
def build_theme():
    import gradio as gr
    t = TOKENS["light"]
    return gr.themes.Base(
        primary_hue=gr.themes.Color(  # postal red ramp; c500 = token
            c50="#FBEDE8", c100="#F6D8CE", c200="#EEB3A2", c300="#E38D75",
            c400="#D66A50", c500=t["postal_red"], c600="#B04129", c700="#933622",
            c800="#752B1B", c900="#582014", c950="#3A150D",
        ),
        font=['"Atkinson Hyperlegible"', '"Noto Sans Devanagari"', "system-ui", "sans-serif"],
        text_size=gr.themes.sizes.text_lg,
        radius_size=gr.themes.sizes.radius_lg,
    ).set(
        body_background_fill=t["paper"], block_background_fill=t["sheet"],
        body_text_color=t["ink"], block_border_color=t["line"],
        button_large_text_size="22px", button_large_padding="18px 24px",
    )
```
  *(Exact `.set()` property names must be checked against the Gradio 6.17 theming docs in
  Task 0 — names drifted between v4/v5/v6. c950 above is a placeholder ramp value: compute
  a real hex, e.g. `#3a150d`.)*
- [ ] **Step 2:** in `app.py`, replace the `launch()` theme with
  `theme=build_theme(), css_paths=["assets/guardian.css"]` (param name per Task 0
  verification; fall back to `css=open(...).read()` if `css_paths` doesn't exist).
- [ ] **Step 3:** `pytest tests -q` → all pass (theme builds lazily; app smoke test still green).
- [ ] **Step 4:** `git commit -m "feat(ui): GuardianTheme postal palette"`

## Task 4: guardian.css — the big skin

**Files:** Create `assets/guardian.css`; Modify `app.py` (delete the old `CSS` string)

Write sections in this order, verifying in the browser after each (Task 11 commands):

- [ ] **Step 1 — fonts + base:**

```css
@font-face { font-family: "Atkinson Hyperlegible"; src: url("fonts/AtkinsonHyperlegible-Regular.woff2") format("woff2"); font-weight: 400; font-display: swap; }
@font-face { font-family: "Atkinson Hyperlegible"; src: url("fonts/AtkinsonHyperlegible-Bold.woff2") format("woff2"); font-weight: 700; font-display: swap; }
@font-face { font-family: "Noto Sans Devanagari"; src: url("fonts/NotoSansDevanagari-Regular.woff2") format("woff2"); font-weight: 400; font-display: swap; }
@font-face { font-family: "Noto Sans Devanagari"; src: url("fonts/NotoSansDevanagari-Bold.woff2") format("woff2"); font-weight: 700; font-display: swap; }
:root { --paper:#FAF4E8; --sheet:#FFFDF7; --ink:#2B2A33; --ink-soft:#5A5550;
        --postal-red:#C84B31; --postal-blue:#3D5A80; --seal-green:#3A7D44;
        --amber:#B97700; --alert-red:#B3362B; --line:#E4D9C3; }
@media (prefers-color-scheme: dark) { :root { /* dark tokens from theme.py table */ } }
.gradio-container { max-width: 1020px !important; margin: 0 auto !important;
                    font-size: 19px; line-height: 1.6; }
```
  *(CSS URL note: `url("fonts/…")` resolves relative to the CSS file when served via
  `css_paths`; if Gradio inlines the CSS instead, switch to `/gradio_api/file=assets/fonts/…`
  and add `allowed_paths=["assets"]` to `launch()` — decide from Task 0 findings.)*
- [ ] **Step 2 — header + wax seal:** style `.guardian-header` (H1 40px, envelope SVG
  inline in the HTML, tagline `--ink-soft` 22px) and `.privacy-banner` →
  seal-green badge: white text on `--seal-green`, border-radius 999px, subtle
  double-ring `box-shadow` like an embossed seal.
- [ ] **Step 3 — paper cards:** `.guardian-card` → `--sheet` bg, `--line` border, 4px
  radius, paper shadow, 21px text; deckle top edge via
  `border-top: 6px solid transparent; border-image: repeating-linear-gradient(90deg, var(--line) 0 8px, transparent 8px 14px) 6;`
  `.card-low/.card-caution/.card-warning` keep tinted backgrounds but switch to
  postal-label style: thick left border (8px) in the semantic color + the stamp badge
  (Task 5) instead of plain emoji headline.
- [ ] **Step 4 — buttons:** `.big-button` 64px min-height, 22px bold; primary =
  `--postal-red` bg/white text; secondary = `--sheet` bg, 2px `--postal-blue` border,
  `--postal-blue` text; hover/focus lift `transform: translateY(-2px)`; focus ring
  `outline: 3px solid var(--postal-blue); outline-offset: 2px;`.
- [ ] **Step 5 — upload zone + audio:** style the gr.Image drop zone as a dashed
  `--postal-blue` "open envelope" area with bigger icon/text; round the audio player
  into a sheet-styled block; hide the audio block entirely until it has content
  (wrap in a `gr.Group(visible=False)` toggled by the handlers — small `app.py` change,
  return `gr.Group(visible=True)` from `on_speak`).
- [ ] **Step 6 — motion + reduced motion:**

```css
@keyframes rise { from { opacity:0; transform: translateY(14px); } to { opacity:1; transform:none; } }
.guardian-card { animation: rise .35s ease-out backwards; }
.guardian-card:nth-of-type(2) { animation-delay: .12s; } .guardian-card:nth-of-type(3) { animation-delay: .24s; }
@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } .guardian-card { transform: none !important; } }
```
- [ ] **Step 7 — mobile (≤640px):** single column (Gradio Rows stack already — verify),
  buttons full-width, H1 30px, cards 18px text, language segments stay ≥48px tall.
- [ ] **Step 8 — footer colophon** + hide Gradio's "Use via API/Settings" footer:
  `footer { display: none !important; }` — **keep** a visible "Built with Gradio ❤️"
  line in our own colophon instead (polite to the host, still custom).
- [ ] `pytest tests -q` → green; `git commit -m "feat(ui): postal skin CSS"` after each
  visually-verified section (≥3 commits across this task).

## Task 5: Letter-sheet cards + stamp verdict badge in render.py

**Files:** Modify `src/guardian/render.py`, `tests/test_pipeline.py`

- [ ] **Step 1: failing tests** (add to `tests/test_pipeline.py::TestRender`):

```python
def test_worry_card_has_stamp_badge(self):
    result = pipeline.analyze(object(), "en")
    _, worry_html, _ = render.render_result(result)
    assert 'class="stamp stamp-low"' in worry_html
    assert "<svg" in worry_html          # inline icon, no external asset

def test_stamp_levels_match(self):
    ex = triage.Extraction(document_type="suspected_scam")
    _, worry_html, _ = render.render_result(pipeline._compose(ex, "en"))
    assert 'stamp-warning' in worry_html
```
- [ ] **Step 2:** run → FAIL.
- [ ] **Step 3:** in `render.py`, add `_stamp(level) -> str` returning
  `<div class="stamp stamp-{level}">{inline-svg-icon}</div>` with three hand-drawn-style
  SVG icons (check ✓ in ring / tilted ⚠ triangle / exclamation octagon — ~6 path
  elements each, `fill="currentColor"`), and prepend it inside the worry card before the
  headline. Keep `html.escape` on ALL model text exactly as now (re-run
  `test_model_text_html_escaped` to prove it).
- [ ] **Step 4:** stamp CSS in `guardian.css`: 92px square, perforated edge:

```css
.stamp { width: 92px; height: 92px; padding: 10px; float: right; margin: 0 0 8px 12px;
  background: radial-gradient(circle at 6px 6px, transparent 5px, currentColor 0) -6px -6px / 14px 14px,
              var(--sheet);  /* perforation illusion */
  color: var(--seal-green); border: 2px solid currentColor; border-radius: 6px; }
.stamp-caution { color: var(--amber); } .stamp-warning { color: var(--alert-red); }
```
  *(Tune the radial-gradient perforation visually; if it fights the border, fall back to
  a `repeating-conic-gradient` edge or a simple double border — taste call in browser.)*
- [ ] **Step 5:** `pytest tests -q` → PASS; `git commit -m "feat(ui): stamp verdict badge"`

## Task 6: Segmented language control

**Files:** Modify `app.py`, `tests/test_app.py`

- [ ] **Step 1: failing test:**

```python
def test_language_control_is_radio():
    import app
    import gradio as gr
    assert isinstance(app.language, gr.Radio)
```
- [ ] **Step 2:** replace the Dropdown:

```python
language = gr.Radio(
    choices=list(config.LANGUAGES), value=config.DEFAULT_LANGUAGE,
    label=ui_text.get(_DEFAULT_LANG, "language_label"),
    elem_id="language-seg",
)
```
  (All `.change` wiring and `on_language_change` outputs stay identical — Radio and
  Dropdown share the change-event/string-value contract; the language-change update item
  becomes `gr.Radio(label=…)` instead of the dropdown update if one exists.)
- [ ] **Step 3:** segmented CSS: hide native inputs, style labels as equal-width pill
  segments, 56px tall, selected = `--postal-blue` bg/white text, unselected = sheet +
  blue border; `:focus-visible` ring.
- [ ] **Step 4:** `pytest tests -q` → PASS (including existing
  `test_language_change_localizes_ui`); browser-verify one Hindi switch round-trip.
- [ ] **Step 5:** `git commit -m "feat(ui): segmented language buttons"`

## Task 7: Step numbers + new localized strings

**Files:** Modify `src/guardian/ui_text.py`, `app.py`; tests auto-guard via `test_all_languages_have_all_keys`

- [ ] **Step 1:** add keys to ALL THREE languages in one edit (the existing key-parity
  test fails if any language is missed — run it first to see it guard):
  `step1` ("① Take a photo" / "① फोटो लें" / "① Tome una foto"),
  `step2` ("② I read it" / "② मैं पढ़ता हूँ" / "② Yo la leo"),
  `step3` ("③ Listen" / "③ सुनिए" / "③ Escuche"),
  `analyzing` already exists; add `samples_label`
  ("Try an example letter" / "एक उदाहरण चिट्ठी आज़माएँ" / "Pruebe una carta de ejemplo").
- [ ] **Step 2:** render the three steps as a header strip in `app.py` (HTML block above
  the Row, postmark-ring styled circles) and include it in `on_language_change` outputs
  (one more `gr.HTML` output — update the test that asserts `len(updates) == 10` → 11).
- [ ] **Step 3:** `pytest tests -q` → PASS; commit.

## Task 8: Example letters (one-tap judge demo)

**Files:** Create `src/guardian/samples.py`, `scripts/make_samples.py`, `assets/samples/*.png`; Modify `app.py`, `modal_validate.py`

- [ ] **Step 1:** move `_render_letter` + `NORMAL_BILL`/`SCAM_LETTER` text out of
  `modal_validate.py` into `src/guardian/samples.py` (same code, importable); make
  `modal_validate.py` import from it. Run `pytest` — nothing breaks (modal file isn't
  imported by tests).
- [ ] **Step 2:** `scripts/make_samples.py` renders both letters at 900×1100 with a faint
  paper-grey background + slight rotation (PIL) so they look photographed, writes
  `assets/samples/bill.png` and `assets/samples/scam.png`. Run it; commit the PNGs.
- [ ] **Step 3:** wire `gr.Examples(examples=[["assets/samples/bill.png"], ["assets/samples/scam.png"]], inputs=[image], label=ui_text.get(lang, "samples_label"), cache_examples=False)`
  under the upload zone. **`cache_examples=False` is mandatory** (caching would run GPU
  jobs at build time and burn quota).
- [ ] **Step 4:** browser-verify clicking an example fills the image; commit.

## Task 9: Analyzing-state envelope loader

**Files:** Modify `app.py` (queue/progress text), `assets/guardian.css`

- [ ] **Step 1:** localized progress: wrap `on_analyze` body with
  `progress = gr.Progress()` … `progress(0.1, desc=ui_text.get(lang, "analyzing"))` at
  entry (verify the Gradio 6 `gr.Progress` injection pattern in docs — Task 0 list).
  If `gr.Progress` fights the `@spaces.GPU` wrapper, fall back to CSS-only: style
  Gradio's built-in progress overlay (`.progress-text` etc.) — acceptable either way.
- [ ] **Step 2:** CSS envelope micro-animation on the output column while
  `.generating` class is present (Gradio adds it): flap triangle rotates open + three
  `--postal-blue` dots pulse. ≤30 lines, behind reduced-motion guard.
- [ ] **Step 3:** mock-mode browser check (analysis is instant in mock — temporarily add
  `time.sleep(2)` LOCALLY ONLY to see the loader, then delete it; never commit a sleep).
- [ ] **Step 4:** `pytest tests -q`; commit.

## Task 10: Accessibility + responsive audit (gate before deploy)

Checklist — every item verified in the running mock app, results noted in BUILD_LOG:

- [ ] `pytest tests/test_theme.py -q` green (contrast, both palettes)
- [ ] Keyboard-only round trip: tab order reaches language → upload → read → listen;
  focus visibly ringed at every stop
- [ ] `preview_resize` to 380×800: single column, no horizontal scroll, buttons ≥48px
- [ ] `prefers-reduced-motion` emulation: zero animation, no rotated cards
- [ ] Dark-mode screenshot: tokens swap, contrast test already proves AA
- [ ] Hindi + Spanish screenshots: Devanagari renders in Noto (not a fallback serif),
  no overflow in segments/buttons
- [ ] Lighthouse-style sanity: no console errors (`preview_console_logs`)

## Task 11: Local verification protocol (use throughout, formally here)

- [ ] `pytest tests -q` → expect **80+ passed** (75 existing + new theme/render/app tests)
- [ ] `preview_start` guardian-mock (`.claude/launch.json` exists; port 7860)
- [ ] Full flow in browser: upload sample → analyze → 3 cards + stamp → read aloud →
  audio appears; switch to Hindi → repeat once
- [ ] Screenshots (light, dark, mobile, Hindi) — save to `docs/ui/` for the README/video
- [ ] `git commit` anything outstanding; push to GitHub **only**

## Task 12: Deploy + live check + freeze

- [ ] Push to Space remote; then **factory restart** (push alone may not rebuild):
  `curl -X POST -H "Authorization: Bearer $(cat ~/.cache/huggingface/token)" "https://huggingface.co/api/spaces/build-small-hackathon/Mystery_Mail_Guardian/restart?factory=true"`
- [ ] Monitor stage → RUNNING at new sha (procedure in BUILD_LOG 06-10/11 entries)
- [ ] `python checks/check_live_space.py` → must print
  `PASS: live Space analysis + speech meet the safety contract`
- [ ] Eyeball the live Space on desktop + phone; screenshot for README
- [ ] BUILD_LOG entry (Field Notes: the design story — Atkinson Hyperlegible, stamps,
  why light-first for elders) and HANDOFF update
- [ ] **UI FREEZE.** Remaining days = demo video + social post + README placeholders.

---

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Gradio 6 internal class names shift under custom CSS | Target our own `elem_id`/`elem_classes` hooks ≥90% of the time; sdk_version is pinned at 6.17.3 |
| `css_paths`/font URL resolution differs from assumption | Task 0 verifies; fallback inline-CSS + `allowed_paths` documented in Task 4 |
| Radio→segmented CSS fights Gradio's Radio DOM | Fallback: keep Radio semantics, accept Gradio's pill look restyled with colors only — still a big upgrade over a dropdown |
| Examples accidentally trigger GPU at build | `cache_examples=False`, verified in Task 8 |
| Scope creep past June 13 | Tasks ordered by visual impact: 1–5 are the look; 6–9 are delight; cut from 9 backwards if needed |
| Space rebuild flakiness | Factory-restart procedure, never Dev Mode |

## Open decisions — answer these before build starts

1. **Light-first postal theme** (recommended, this plan) vs keeping dark-first?
2. **Mascot** (small inline-SVG guardian owl on the header)? Recommend **no** — dignity
   over cuteness; the stamps/seal carry the charm. Say yes only if you love it.
3. **Example letters visible to judges** (Task 8)? Recommend **yes** — each judge click
   costs ~30–60s of *their* ZeroGPU quota, not yours, and removes all friction.
4. **Off-Brand stretch (`gr.Server`)**: attempt only if Tasks 1–9 deployed by June 13
   noon? (Task 0 gathers the facts; default = skip.)
5. Keep the three languages as-is, or swap Spanish for the real person's actual language
   if it differs? (Strings are one file: `ui_text.py`.)
