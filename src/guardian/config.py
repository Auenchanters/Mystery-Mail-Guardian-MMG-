"""Model registry, runtime configuration, and the 32B parameter-budget guard.

Model facts verified against live Hugging Face model cards on 2026-06-10:
  - openbmb/MiniCPM-V-4.6   : 1.3B params (SigLIP2-400M vision + Qwen3.5-0.8B LLM), Apache-2.0
  - openbmb/VoxCPM2         : 2.0B params, multilingual TTS (30 languages), Apache-2.0
  - openbmb/MiniCPM4.1-8B   : 8.0B params, Apache-2.0, official GGUF for llama.cpp
"""

from __future__ import annotations

import os

# --- Model registry -------------------------------------------------------
MINICPM_V_ID = "openbmb/MiniCPM-V-4.6"        # central engine: OCR + layout + reasoning
VOXCPM_ID = "openbmb/VoxCPM2"                  # multilingual TTS
REASONER_GGUF_REPO = "openbmb/MiniCPM4.1-8B-GGUF"  # "full" config only, via llama.cpp
REASONER_GGUF_FILE = os.environ.get(
    "GUARDIAN_REASONER_GGUF", "MiniCPM4.1-8B-Q4_K_M.gguf"
)

PARAMS_B = {
    MINICPM_V_ID: 1.3,
    VOXCPM_ID: 2.0,
    REASONER_GGUF_REPO: 8.0,
}
PARAM_CAP_B = 32.0  # hackathon hard rule: sum of all distinct loaded models

# --- Runtime configuration -------------------------------------------------
# GUARDIAN_CONFIG=lean (default) : MiniCPM-V 4.6 + VoxCPM2          = 3.3B
# GUARDIAN_CONFIG=full           : + MiniCPM4.1-8B GGUF (llama.cpp) = 11.3B
CONFIG = os.environ.get("GUARDIAN_CONFIG", "lean").strip().lower()
MOCK = os.environ.get("GUARDIAN_MOCK", "") == "1"  # UI development without model weights


def active_models() -> list[str]:
    models = [MINICPM_V_ID, VOXCPM_ID]
    if CONFIG == "full":
        models.append(REASONER_GGUF_REPO)
    return models


def total_params_b() -> float:
    return sum(PARAMS_B[m] for m in active_models())


def assert_param_budget() -> float:
    """Hard guard: refuse to start if the model set exceeds the 32B cap."""
    total = total_params_b()
    if total > PARAM_CAP_B:
        raise RuntimeError(
            f"Parameter budget exceeded: {total:.1f}B > {PARAM_CAP_B:.0f}B cap"
        )
    return total


# --- Languages -------------------------------------------------------------
# Display label -> ISO code. All four are in VoxCPM2's supported-language list.
LANGUAGES = {
    "English": "en",
    "हिन्दी (Hindi)": "hi",
    "Español (Spanish)": "es",
    "日本語 (Japanese)": "ja",
}
DEFAULT_LANGUAGE = "English"

PROMPT_LANGUAGE_NAMES = {"en": "English", "hi": "Hindi", "es": "Spanish", "ja": "Japanese"}

# --- Generation / quota tuning ---------------------------------------------
MAX_NEW_TOKENS = 1600          # vision model output budget (JSON + explanation text)
TTS_MAX_CHARS = 700            # cap spoken text to respect the ZeroGPU quota
GPU_DURATION_ANALYZE = 120     # seconds; one document analysis pass
GPU_DURATION_SPEAK = 90        # seconds; one TTS pass
