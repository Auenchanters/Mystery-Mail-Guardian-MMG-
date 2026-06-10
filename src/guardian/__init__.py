"""Mystery-Mail Guardian — privacy-first scam-and-action triage for confusing mail.

Pipeline stages (each swappable):
    extract  -> MiniCPM-V 4.6 reads the photographed document (OCR + layout + reasoning)
    triage   -> validate model output, run heuristic scam-signal scan, compute worry level
    explain  -> compose the plain-language result (optional MiniCPM4.1-8B refinement in "full" config)
    speak    -> VoxCPM2 reads the summary aloud
    safety   -> cautious-framing layer applied to everything user-facing
"""

__version__ = "1.0.0"
