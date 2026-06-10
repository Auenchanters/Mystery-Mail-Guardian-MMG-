"""Explain stage.

Lean config (default): the explanation already produced by MiniCPM-V 4.6 in the
extract pass is used directly (after the safety layer).

Full config (GUARDIAN_CONFIG=full): MiniCPM4.1-8B (GGUF, llama.cpp runtime ->
Llama Champion badge) rewrites the explanation from the extracted facts for
stronger plain-language quality. Runs CPU-side: ZeroGPU virtualizes CUDA
through PyTorch, which llama.cpp does not use. If llama-cpp-python or the GGUF
weights are unavailable, we fall back to the lean explanation gracefully.
"""

from __future__ import annotations

import traceback

from . import config, prompts, triage

_llm = None
_llm_failed = False


def load() -> None:
    """Load the GGUF reasoner once (full config only)."""
    global _llm, _llm_failed
    if config.CONFIG != "full" or config.MOCK or _llm is not None or _llm_failed:
        return
    try:
        from llama_cpp import Llama

        _llm = Llama.from_pretrained(
            repo_id=config.REASONER_GGUF_REPO,
            filename=config.REASONER_GGUF_FILE,
            n_ctx=4096,
            n_gpu_layers=0,  # CPU: llama.cpp cannot see ZeroGPU's virtualized CUDA
            verbose=False,
        )
    except Exception:
        _llm_failed = True
        print("[guardian] full-config reasoner unavailable, falling back to lean:")
        traceback.print_exc()


def refine(extraction: triage.Extraction, lang: str) -> triage.Extraction:
    """Optionally rewrite the explanation with MiniCPM4.1-8B. Never fails the
    pipeline: any problem returns the lean extraction unchanged."""
    if config.CONFIG != "full" or config.MOCK:
        return extraction
    load()
    if _llm is None:
        return extraction
    try:
        completion = _llm.create_chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": prompts.refine_prompt(extraction.facts_json(), lang),
                }
            ],
            max_tokens=700,
            temperature=0.2,
        )
        raw = completion["choices"][0]["message"]["content"]
        data = triage.parse_model_json(raw)
        if not data:
            return extraction
        refined = triage.validate_extraction({"explanation": data})
        # Adopt refined text only where the reasoner actually produced content.
        if refined.what_this_is:
            extraction.what_this_is = refined.what_this_is
        if refined.key_facts:
            extraction.key_facts = refined.key_facts
        if refined.worry_reasons:
            extraction.worry_reasons = refined.worry_reasons
        if refined.what_to_do:
            extraction.what_to_do = refined.what_to_do
    except Exception:
        print("[guardian] refinement failed, using lean explanation:")
        traceback.print_exc()
    return extraction
