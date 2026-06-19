# Project_Alpha

I am a big Fire Emblem fan and have played the series from the GBA era to Switch 2.  
This is a Python project developed with Codex, inspired by classic Fire Emblem-style tactical gameplay.  
Have fun :D

## Current Status
Working in progress...

## Features
- Grid-based map movement with terrain costs and effects
- Turn-based combat (hit / damage / crit / counter / follow-up, weapon durability)
- **Weapon triangle** — color-based (red > green > blue > red); covers both the
  physical triangle (sword/axe/lance) and the anima magic triangle (fire/wind/thunder)
- **Class promotion** — tier-1 classes (Lv cap 20) promote into a fixed tier-2
  class via a Master Seal at Lv10+ (Lv cap 20 again); no horizontal transfer
- Stat growth & leveling with per-class growth rates
- Player and enemy units, movement/attack range display
- Chapter-based unit setup, sprite-based character rendering

## Tech
- Python
- Pygame

## Development
Core combat/progression logic is pygame-free, so tests and balance tooling run
on any Python (no display needed):

```
python3 run_tests.py        # unit tests (weapon triangle, promotion, combat, movement)
python3 balance_sim.py 3000  # Monte-Carlo: triangle win rates + growth curves
python3 verify_imports.py   # headless smoke check of the full import chain
```

Tuning knobs live in `src/constants.py` (triangle bonuses, hit/crit, level caps);
class/promotion data in `src/unit_classes.py`; chapter data in `src/chapters_data.py`.

## Notes
This project is currently under development and will continue to be expanded with more gameplay systems, UI improvements, terrain mechanics, and chapter content.

## Debug 
Use http://localhost:8000/?-i to find errors when testing on localhost

