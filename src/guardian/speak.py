"""Speak stage — VoxCPM2 (2B, multilingual TTS, OpenBMB family).

One request-driven pass: summary text -> (sample_rate, int16 numpy waveform)
for gr.Audio. Uses a neutral built-in voice on purpose: no voice cloning, so no
cloning-consent issues (PROJECT.md §9).
"""

from __future__ import annotations

from . import config

_tts = None


def load() -> None:
    global _tts
    if _tts is not None or config.MOCK:
        return
    from voxcpm import VoxCPM

    # Usage per the official model card (verified 2026-06-10).
    _tts = VoxCPM.from_pretrained(config.VOXCPM_ID, load_denoiser=False)


def synthesize(text: str):
    """Speak `text` (already capped to config.TTS_MAX_CHARS by the pipeline)."""
    import numpy as np

    if config.MOCK:  # 1s gentle beep so the UI flow is testable without weights
        sr = 16000
        t = np.linspace(0, 1.0, sr, endpoint=False)
        wav = 0.2 * np.sin(2 * np.pi * 440 * t)
        return sr, (wav * 32767).astype(np.int16)

    load()
    wav = _tts.generate(
        text=text[: config.TTS_MAX_CHARS],
        cfg_value=2.0,
        inference_timesteps=10,
    )
    wav = np.asarray(wav, dtype=np.float32)
    peak = float(np.max(np.abs(wav))) or 1.0
    if peak > 1.0:
        wav = wav / peak
    return _tts.tts_model.sample_rate, (wav * 32767).astype(np.int16)
