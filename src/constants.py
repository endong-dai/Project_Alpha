"""
constants.py
Central tuning numbers for combat and progression.

Keeping the magic numbers here makes a balance pass (see plan 阶段4) a
single-file change instead of a hunt through combat.py / progression.py.
"""

# --- Combat formula ---------------------------------------------------------
HIT_RATE_BASE = 70          # flat hit before speed / terrain / avoid
SPEED_HIT_FACTOR = 5        # hit gained per point of attacker speed
SPEED_AVOID_FACTOR = 5      # avoid gained per point of defender speed
HIT_RATE_MIN = 30
HIT_RATE_MAX = 95
CRIT_DAMAGE_MULTIPLIER = 3
FOLLOW_UP_SPEED_GAP = 4     # speed lead required to strike twice

# --- Weapon triangle (阶段2A) -----------------------------------------------
# Every weapon_type maps to a color; the colors form a rock-paper-scissors
# cycle: red > green > blue > red. ``None`` is colorless (neutral, no bonus).
# This single cycle reproduces both the physical triangle (sword>axe>lance)
# and the anima magic triangle (fire>wind>thunder) at the same time.
WEAPON_COLOR = {
    "sword": "red",
    "fire": "red",
    "axe": "green",
    "wind": "green",
    "lance": "blue",
    "thunder": "blue",
    "dagger": None,         # colorless: outside the triangle
    "earth": None,          # colorless: outside the triangle
}
TRIANGLE_BEATS = {"red": "green", "green": "blue", "blue": "red"}
TRIANGLE_HIT_BONUS = 15     # advantage: +hit, disadvantage: -hit
TRIANGLE_DAMAGE_BONUS = 1   # advantage: +dmg, disadvantage: -dmg

# Display colors (RGB) for the triangle markers in the battle forecast UI.
TRIANGLE_DISPLAY_RGB = {
    "red": (210, 70, 70),
    "green": (80, 175, 90),
    "blue": (80, 120, 215),
}

# --- Progression / promotion (阶段2B) ---------------------------------------
EXP_PER_LEVEL = 100
TIER1_MAX_LEVEL = 20
TIER2_MAX_LEVEL = 20
PROMOTION_MIN_LEVEL = 10    # tier-1 level required before a unit may promote
