"""Shared setup for the examples: a throw-away copy of data/, no LLM, a Flask test client."""
import os
import shutil
import sys
import tempfile

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(BACKEND, "examples", "output")

# Done at import time, before any example imports `crud`, so the real data/ is never touched.
_TMP = tempfile.mkdtemp(prefix="code-hinter-demo-")
for _name in ("exercises.json", "profs.json", "students.json", "stud_prof.json", "stud_exe.json"):
    shutil.copy(os.path.join(BACKEND, "data", _name), _TMP)
os.environ["CH_DATA_DIR"] = _TMP
os.environ.setdefault("CH_LLM_BACKEND", "offline")   # CH_LLM_BACKEND=smol to try the LLM path
sys.path.insert(0, BACKEND)
os.makedirs(OUTPUT, exist_ok=True)

def client():
    import main
    return main.app.test_client()

def show(title, text=""):
    print(f"\n=== {title} ===")
    if text:
        print(text)

EMAIL = "benalla@example.com"   # seed student of professor 1 (exercises 1 and 2)
