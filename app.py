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

from guardian import config, pipeline, render, speak, ui_text

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
    return what_html, worry_html, todo_html, result.speak_text, None


def on_speak(speak_text: str, lang_label: str):
    lang = _lang_code(lang_label)
    if not speak_text:
        gr.Warning(ui_text.get(lang, "err_no_speech"))
        return None
    return gpu_speak(speak_text)


def _header_html(lang: str) -> str:
    return f"""
    <div class="guardian-header">
      <h1>{ui_text.get(lang, "title")}</h1>
      <p class="tagline">{ui_text.get(lang, "tagline")}</p>
      <p class="privacy-banner">{ui_text.get(lang, "privacy")}</p>
    </div>"""


def _footer_html(lang: str) -> str:
    models = " + ".join(f"{m} ({config.PARAMS_B[m]:.1f}B)" for m in config.active_models())
    return f"""
    <div class="guardian-footer">
      <p class="disclaimer">🤍 {ui_text.get(lang, "disclaimer")}</p>
      <p class="model-note">Off the Grid: 100% local inference · {models} ·
      total {config.total_params_b():.1f}B of 32B allowed</p>
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
    )


# --- Layout & styling (accessible: large type, big targets, high contrast) -----
CSS = """
.gradio-container { max-width: 980px !important; margin: 0 auto !important; }
.guardian-header { text-align: center; padding: 8px 0 4px; }
.guardian-header h1 { font-size: 2.4rem; margin-bottom: 4px; }
.guardian-header .tagline { font-size: 1.35rem; margin: 4px 0; }
.privacy-banner {
  display: inline-block; font-size: 1.1rem; font-weight: 600;
  background: rgba(46, 125, 50, 0.14); border: 2px solid rgba(46, 125, 50, 0.55);
  border-radius: 12px; padding: 8px 16px; margin-top: 6px;
}
.guardian-card {
  border-radius: 14px; padding: 16px 20px; margin: 10px 0;
  font-size: 1.25rem; line-height: 1.65; border: 2px solid transparent;
}
.guardian-card h2 { font-size: 1.45rem; margin: 0 0 8px; }
.guardian-card ul { margin: 6px 0 0 2px; padding-left: 24px; }
.guardian-card li { margin: 5px 0; }
.card-neutral { background: rgba(100, 130, 200, 0.10); border-color: rgba(100, 130, 200, 0.40); }
.card-low     { background: rgba(46, 125, 50, 0.10);  border-color: rgba(46, 125, 50, 0.45); }
.card-caution { background: rgba(230, 150, 0, 0.13);  border-color: rgba(230, 150, 0, 0.55); }
.card-warning { background: rgba(198, 40, 40, 0.12);  border-color: rgba(198, 40, 40, 0.60); }
.card-todo    { background: rgba(2, 119, 189, 0.10);  border-color: rgba(2, 119, 189, 0.45); }
.big-button { min-height: 72px; font-size: 1.4rem !important; font-weight: 700; }
.guardian-footer { text-align: center; font-size: 1.0rem; opacity: 0.85; padding-top: 10px; }
.guardian-footer .disclaimer { font-size: 1.15rem; font-weight: 600; }
label span { font-size: 1.1rem !important; }
"""

_DEFAULT_LANG = config.LANGUAGES[config.DEFAULT_LANGUAGE]

with gr.Blocks(title="Mystery-Mail Guardian") as demo:
    header = gr.HTML(_header_html(_DEFAULT_LANG))

    language = gr.Dropdown(
        choices=list(config.LANGUAGES),
        value=config.DEFAULT_LANGUAGE,
        label=ui_text.get(_DEFAULT_LANG, "language_label"),
    )

    with gr.Row(equal_height=False):
        with gr.Column(scale=5):
            image = gr.Image(
                type="pil",
                sources=["upload", "webcam"],
                label=ui_text.get(_DEFAULT_LANG, "upload_label"),
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
        outputs=[out_what, out_worry, out_todo, speak_state, audio],
    )
    read_btn.click(on_speak, inputs=[speak_state, language], outputs=[audio])
    language.change(
        on_language_change,
        inputs=[language],
        outputs=[header, image, analyze_btn, read_btn, audio,
                 out_what, out_worry, out_todo, speak_state, footer],
    )

if __name__ == "__main__":
    # Gradio 6: theme/css are launch() parameters.
    demo.launch(
        css=CSS,
        theme=gr.themes.Soft(
            text_size=gr.themes.sizes.text_lg, radius_size=gr.themes.sizes.radius_lg
        ),
    )
