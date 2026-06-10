"""Isolation check 3/3 — VoxCPM2 speaks the summary clearly.

Run on a GPU machine (or the Space) with requirements.txt installed:
    python checks/check_speak.py [language]

Writes check_speak_<lang>.wav next to this script — listen and judge clarity.
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

SAMPLES = {
    "en": "This looks like a normal electricity bill from City Power Company. "
          "The amount is 84 dollars, due June 28. Before you pay, check with the "
          "company through a number you already trust.",
    "hi": "यह City Power Company का बिजली का बिल लगता है। रक़म 84 डॉलर है और आख़िरी "
          "तारीख़ 28 जून है। पैसे देने से पहले उस नंबर पर जाँच लें जिस पर आप पहले से भरोसा करते हैं।",
    "es": "Parece una factura de electricidad normal de City Power Company. El monto es "
          "84 dólares y vence el 28 de junio. Antes de pagar, confirme con la empresa "
          "por un teléfono que usted ya conozca.",
}


def main() -> int:
    import soundfile as sf

    from guardian import speak

    lang = sys.argv[1] if len(sys.argv) > 1 else "en"
    text = SAMPLES.get(lang, SAMPLES["en"])

    t0 = time.time()
    sr, wav = speak.synthesize(text)
    elapsed = time.time() - t0

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"check_speak_{lang}.wav")
    sf.write(out_path, wav, sr)
    duration = len(wav) / sr
    print(f"PASS-if-clear: wrote {out_path} ({duration:.1f}s audio, sr={sr}, "
          f"synthesized in {elapsed:.1f}s vs 90s GPU budget). Listen to judge clarity.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
