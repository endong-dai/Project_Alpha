"""
verify_imports.py
Headless smoke check of the full import chain (incl. gui_main + pygame).
Run:  python3 verify_imports.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import gui_main  # noqa: F401,E402  - importing is the test
from chapters_data import CHAPTERS  # noqa: E402
from terrain_render import build_terrain_overlays  # noqa: F401,E402

print("导入OK: gui_main + terrain_render + chapters_data")
print("chapters =", list(CHAPTERS))
