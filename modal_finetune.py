"""LoRA SFT experiment for MiniCPM-V 4.6 on Modal — TRAIN-ONLY, NEVER DEPLOYED.

Recipe per the official MiniCPM-V cookbook (ms-swift, model_type/template
minicpmv4_6, transformers>=5.7); we use tuner_type=lora + frozen ViT so it
fits an A10G. The deployed Space keeps the stock model through judging
(Tiny Titan stays clean); this exists to measure whether SFT on our
synthetic letters moves extraction quality, and to document it either way.

Prepare data, then run:
    .venv\\Scripts\\python.exe scripts\\make_dataset.py 96 dataset\\train 777
    .venv\\Scripts\\python.exe scripts\\make_swift_dataset.py
    .venv\\Scripts\\python.exe scripts\\make_swift_dataset.py dataset\\eval dataset\\eval\\swift.jsonl
    .venv\\Scripts\\modal.exe run modal_finetune.py
Adapter persists in the modal volume `guardian-lora`; metrics print locally.
"""

from __future__ import annotations

import json
import os
import sys

import modal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = modal.App("mystery-mail-guardian-lora")

vol = modal.Volume.from_name("guardian-lora", create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch==2.8.0", "torchvision==0.23.0",
        "transformers==5.7.0", "accelerate", "peft", "trl",
        "ms-swift", "av", "soundfile", "numpy", "Pillow", "json-repair",
        "einops", "safetensors", "sentencepiece",
    )
    .env({"USE_HF": "1"})  # swift defaults to ModelScope; we want the HF Hub
    .add_local_dir("src", "/root/src")
    .add_local_dir(os.path.join("dataset", "train"), "/root/train")
    .add_local_dir(os.path.join("dataset", "eval"), "/root/eval")
)


def _abs_paths(src: str, base: str, dst: str) -> None:
    with open(src, encoding="utf-8") as f, open(dst, "w", encoding="utf-8") as g:
        for line in f:
            if line.strip():
                g.write(line.replace('"./', f'"{base}/'))


@app.function(gpu="A10G", image=image, timeout=5400, volumes={"/vol": vol},
              secrets=[modal.Secret.from_name("huggingface")])
def train() -> dict:
    import re
    import subprocess

    _abs_paths("/root/train/swift.jsonl", "/root/train", "/root/train_abs.jsonl")

    cmd = [
        "swift", "sft",
        "--model", "openbmb/MiniCPM-V-4.6",
        "--model_type", "minicpmv4_6",
        "--template", "minicpmv4_6",
        "--tuner_type", "lora",
        "--dataset", "/root/train_abs.jsonl",
        "--split_dataset_ratio", "0.1",
        "--torch_dtype", "bfloat16",
        "--freeze_vit", "true",
        "--max_length", "3072",
        "--num_train_epochs", "2",
        "--per_device_train_batch_size", "1",
        "--gradient_accumulation_steps", "8",
        "--learning_rate", "1e-4",
        "--logging_steps", "2",
        "--save_strategy", "epoch",
        "--output_dir", "/vol/lora-v1",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    tail = (proc.stdout + "\n" + proc.stderr)[-6000:]
    losses = [float(m) for m in re.findall(r"'loss':\s*([0-9.]+)", proc.stdout)]
    vol.commit()
    return {
        "returncode": proc.returncode,
        "first_losses": losses[:3],
        "last_losses": losses[-3:],
        "n_loss_points": len(losses),
        "log_tail": tail,
    }


@app.local_entrypoint()
def main():
    result = train.remote()
    os.makedirs("modal_artifacts", exist_ok=True)
    with open(os.path.join("modal_artifacts", "lora_train.json"), "w",
              encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print("returncode:", result["returncode"])
    print("loss start:", result["first_losses"], "-> end:", result["last_losses"],
          f"({result['n_loss_points']} points)")
    if result["returncode"] != 0:
        print("--- log tail ---")
        print(result["log_tail"])
    else:
        print("adapter persisted in modal volume 'guardian-lora' (/vol/lora-v1)")
