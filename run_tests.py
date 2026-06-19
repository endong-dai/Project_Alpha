"""
run_tests.py
Lightweight test runner that needs neither pytest nor pygame.

The game modules `import pygame` at module top level (terrain.py), so on a
Python without pygame we inject a stub module first. The tests only exercise
pure combat/progression/movement logic and never touch real rendering.

Usage:  python3 run_tests.py
"""
import importlib
import os
import sys
import traceback
import types

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
TESTS = os.path.join(ROOT, "tests")
for path in (SRC, TESTS):
    if path not in sys.path:
        sys.path.insert(0, path)

# Stub pygame so `import pygame` succeeds without the real package installed.
if "pygame" not in sys.modules:
    sys.modules["pygame"] = types.ModuleType("pygame")

TEST_MODULES = ["test_weapon_triangle", "test_promotion", "test_combat_movement"]


def main():
    passed = 0
    failures = []
    for modname in TEST_MODULES:
        module = importlib.import_module(modname)
        for name in sorted(dir(module)):
            if not name.startswith("test_"):
                continue
            fn = getattr(module, name)
            if not callable(fn):
                continue
            try:
                fn()
                passed += 1
                print(f"PASS  {modname}.{name}")
            except Exception as exc:  # noqa: BLE001 - report every failure
                failures.append((modname, name, traceback.format_exc()))
                print(f"FAIL  {modname}.{name}: {exc}")

    print(f"\n{passed} passed, {len(failures)} failed")
    for modname, name, tb in failures:
        print(f"\n===== {modname}.{name} =====\n{tb}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
