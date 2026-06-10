"""Extract stage — MiniCPM-V 4.6 (the central engine, 1.3B params).

Reads the photographed document: OCR + layout + document understanding in one
pass. On ZeroGPU the model is loaded on `cuda` at module/startup scope (CUDA
emulation outside @spaces.GPU functions); the real GPU attaches inside the
decorated request handler in app.py.

Heavy imports stay inside functions so the package imports cleanly on machines
without torch (mock mode, unit tests).
"""

from __future__ import annotations

from . import config

_model = None
_processor = None


def load() -> None:
    """Load MiniCPM-V 4.6 once, at startup (module scope on the Space)."""
    global _model, _processor
    if _model is not None or config.MOCK:
        return
    from transformers import AutoModelForImageTextToText, AutoProcessor

    # Usage per the official model card (verified 2026-06-10):
    # transformers>=5.7.0, torch_dtype="auto", device_map="auto".
    _processor = AutoProcessor.from_pretrained(config.MINICPM_V_ID)
    _model = AutoModelForImageTextToText.from_pretrained(
        config.MINICPM_V_ID, torch_dtype="auto", device_map="auto"
    )


def run_vision(image, prompt: str) -> str:
    """One request-driven pass: photo + instruction -> raw model text (JSON expected).

    `image` is a PIL.Image. Must be called from within a @spaces.GPU context on
    ZeroGPU. downsample_mode="4x" trades a few visual tokens for the finer
    detail that small print on bills and letters needs.
    """
    load()
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": prompt},
            ],
        }
    ]
    inputs = _processor.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt",
        downsample_mode="4x",
        max_slice_nums=36,
    ).to(_model.device)
    generated_ids = _model.generate(
        **inputs,
        downsample_mode="4x",
        max_new_tokens=config.MAX_NEW_TOKENS,
        do_sample=False,
    )
    trimmed = [
        out_ids[len(in_ids):]
        for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    return _processor.batch_decode(trimmed, skip_special_tokens=True)[0]
