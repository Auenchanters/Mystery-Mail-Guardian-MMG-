import os
import sys

# Tests run offline against the pure-Python pipeline; no model weights needed.
os.environ["GUARDIAN_MOCK"] = "1"

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
)
