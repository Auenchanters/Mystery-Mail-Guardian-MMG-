"""Mystery-Mail Guardian — Gradio app (Hugging Face Space entrypoint).

Photograph a confusing letter; the app explains it in plain language, flags
scam warning signs (cautiously, with reasons), says what to do next, and reads
the summary aloud — all locally, on small models. Nothing leaves the device.

Models (all OpenBMB, total 3.3B params in the default lean config):
  MiniCPM-V 4.6 (1.3B) central engine | VoxCPM2 (2B) TTS
  [GUARDIAN_CONFIG=full adds MiniCPM4.1-8B GGUF via llama.cpp -> 11.3B]
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import gradio as gr

from guardian import config, pipeline, render, speak, theme, ui_text

# --- ZeroGPU compatibility ---------------------------------------------------
# @spaces.GPU is effect-free off-Space per the ZeroGPU docs; this shim makes it
# effect-free where the `spaces` package isn't installed at all (local dev).
try:
    import spaces
except ImportError:  # local development

    class _SpacesShim:
        @staticmethod
        def GPU(*args, **kwargs):
            if args and callable(args[0]):
                return args[0]
            return lambda fn: fn

    spaces = _SpacesShim()

# --- Startup: param-budget guard + model loading at module scope --------------
_TOTAL_B = config.assert_param_budget()
print(f"[guardian] config={config.CONFIG} mock={config.MOCK}")
print(f"[guardian] models={config.active_models()}")
print(f"[guardian] TOTAL PARAMS: {_TOTAL_B:.1f}B / {config.PARAM_CAP_B:.0f}B cap")

if not config.MOCK:
    # ZeroGPU pattern: load on cuda at startup (emulated CUDA outside @spaces.GPU).
    from guardian import explain, extract

    extract.load()
    speak.load()
    explain.load()  # no-op unless GUARDIAN_CONFIG=full


# --- Request-driven GPU functions ---------------------------------------------
@spaces.GPU(duration=config.GPU_DURATION_ANALYZE)
def gpu_analyze(image, lang: str) -> pipeline.AnalysisResult:
    return pipeline.analyze(image, lang)


@spaces.GPU(duration=config.GPU_DURATION_SPEAK)
def gpu_speak(text: str):
    return speak.synthesize(text)


# --- UI callbacks --------------------------------------------------------------
def _lang_code(label: str) -> str:
    return config.LANGUAGES.get(label, "en")


def on_analyze(image, lang_label: str):
    lang = _lang_code(lang_label)
    result = gpu_analyze(image, lang)
    what_html, worry_html, todo_html = render.render_result(result)
    return (what_html, worry_html, todo_html, result.speak_text,
            None, gr.Group(visible=False))


def on_speak(speak_text: str, lang_label: str):
    lang = _lang_code(lang_label)
    if not speak_text:
        gr.Warning(ui_text.get(lang, "err_no_speech"))
        return None, gr.Group(visible=False)
    return gpu_speak(speak_text), gr.Group(visible=True)


# Inline SVG (vendored in code — no image files, no runtime fetches).
_ENVELOPE_SVG = """<svg viewBox="0 0 64 48" width="56" height="42" aria-hidden="true" focusable="false">
  <rect x="2" y="4" width="60" height="40" rx="3" fill="none" stroke="var(--postal-blue)" stroke-width="3"/>
  <path d="M5 9 L32 30 L59 9" fill="none" stroke="var(--postal-red)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="47" y="10" width="9" height="7" fill="var(--postal-red)" opacity=".85"/>
</svg>"""

_SHIELD_SVG = """<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false" fill="currentColor">
  <path d="M12 2l8 3v6c0 5.4-3.4 9.6-8 11-4.6-1.4-8-5.6-8-11V5z"/>
  <path d="M8.6 11.6l2.4 2.4 4.4-4.6" fill="none" stroke="var(--seal-green)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""


def _steps_html(lang: str) -> str:
    items = "".join(
        f'<div class="step"><span class="step-ring">{i}</span>'
        f'<span>{ui_text.get(lang, key)}</span></div>'
        for i, key in ((1, "step1"), (2, "step2"), (3, "step3"))
    )
    return f'<div class="guardian-steps">{items}</div>'


def _header_html(lang: str) -> str:
    return f"""
    <div class="guardian-header">
      <div class="wordmark">{_ENVELOPE_SVG}<h1>{ui_text.get(lang, "title")}</h1></div>
      <p class="tagline">{ui_text.get(lang, "tagline")}</p>
      <p class="privacy-banner">{_SHIELD_SVG}<span>{ui_text.get(lang, "privacy")}</span></p>
    </div>"""


def _footer_html(lang: str) -> str:
    models = " + ".join(f"{m} ({config.PARAMS_B[m]:.1f}B)" for m in config.active_models())
    return f"""
    <div class="guardian-footer">
      <p class="disclaimer">🤍 {ui_text.get(lang, "disclaimer")}</p>
      <p class="model-note">Off the Grid: 100% local inference · {models} ·
      total {config.total_params_b():.1f}B of 32B allowed</p>
      <p class="colophon">Built with Gradio ❤️ · every model by OpenBMB</p>
    </div>"""


def on_language_change(lang_label: str):
    lang = _lang_code(lang_label)
    what_html, worry_html, todo_html = render.render_placeholder(lang)
    return (
        _header_html(lang),
        gr.Image(label=ui_text.get(lang, "upload_label")),
        gr.Button(value=ui_text.get(lang, "analyze_btn")),
        gr.Button(value=ui_text.get(lang, "read_aloud_btn")),
        gr.Audio(label=ui_text.get(lang, "audio_label"), value=None),
        what_html,
        worry_html,
        todo_html,
        "",          # clear pending speech
        _footer_html(lang),
        gr.Group(visible=False),   # hide the (now empty) audio sheet
        _steps_html(lang),
    )


# --- Layout (all styling lives in assets/guardian.css + guardian/theme.py) -----
_DEFAULT_LANG = config.LANGUAGES[config.DEFAULT_LANGUAGE]

with gr.Blocks(title="Mystery-Mail Guardian") as demo:
    header = gr.HTML(_header_html(_DEFAULT_LANG))

    language = gr.Radio(
        choices=list(config.LANGUAGES),
        value=config.DEFAULT_LANGUAGE,
        label=ui_text.get(_DEFAULT_LANG, "language_label"),
        elem_id="language-seg",
    )

    steps = gr.HTML(_steps_html(_DEFAULT_LANG))

    with gr.Row(equal_height=False):
        with gr.Column(scale=5):
            image = gr.Image(
                type="pil",
                sources=["upload", "webcam"],
                label=ui_text.get(_DEFAULT_LANG, "upload_label"),
                elem_classes=["upload-zone"],
            )
            examples = gr.Examples(
                examples=[["assets/samples/bill.png"], ["assets/samples/scam.png"]],
                inputs=[image],
                label=ui_text.get(_DEFAULT_LANG, "samples_label"),
                cache_examples=False,  # never burn GPU quota at build time
                elem_id="sample-letters",
            )
            analyze_btn = gr.Button(
                ui_text.get(_DEFAULT_LANG, "analyze_btn"),
                variant="primary",
                elem_classes=["big-button"],
            )
        with gr.Column(scale=6):
            placeholder_what, _, _ = render.render_placeholder(_DEFAULT_LANG)
            out_what = gr.HTML(placeholder_what)
            out_worry = gr.HTML("")
            out_todo = gr.HTML("")
            read_btn = gr.Button(
                ui_text.get(_DEFAULT_LANG, "read_aloud_btn"),
                variant="secondary",
                elem_classes=["big-button"],
            )
            with gr.Group(visible=False, elem_classes=["audio-sheet"]) as audio_group:
                audio = gr.Audio(
                    label=ui_text.get(_DEFAULT_LANG, "audio_label"),
                    type="numpy",
                    autoplay=True,
                    interactive=False,
                )

    speak_state = gr.State("")
    footer = gr.HTML(_footer_html(_DEFAULT_LANG))

    analyze_btn.click(
        on_analyze,
        inputs=[image, language],
        outputs=[out_what, out_worry, out_todo, speak_state, audio, audio_group],
    )
    read_btn.click(on_speak, inputs=[speak_state, language], outputs=[audio, audio_group])
    language.change(
        on_language_change,
        inputs=[language],
        outputs=[header, image, analyze_btn, read_btn, audio,
                 out_what, out_worry, out_todo, speak_state, footer, audio_group,
                 steps],
    )

if __name__ == "__main__":
    # Gradio 6: theme/css are launch() parameters. css_paths is inlined by
    # Gradio, so fonts resolve via /gradio_api/file= + allowed_paths.
    demo.launch(
        css=theme.css_variables(),
        css_paths=["assets/guardian.css"],
        theme=theme.build_theme(),
        allowed_paths=["assets"],
    )
