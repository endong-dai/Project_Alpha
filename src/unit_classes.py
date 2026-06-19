"""
unit_classes.py
Class and weapon definitions for battle units.
"""

import random

from constants import TIER1_MAX_LEVEL, TIER2_MAX_LEVEL

PHYSICAL = "physical"
MAGICAL = "magical"

# Each tier-1 class has a fixed promotion target (no horizontal transfer).
# ``promotion_bonuses`` is the one-time stat boost applied when a unit promotes
# *into* a tier-2 class (see progression.promote).
CLASS_PROFILES = [
    # --- Tier 1 (base classes, Lv cap 20) -----------------------------------
    {
        "id": "sword_fighter",
        "name": "Sword Fighter",
        "allowed_weapon_types": ["sword"],
        "strength_mod": 1,
        "magic_mod": 0,
        "defense_mod": 0,
        "resistance_mod": 0,
        "tier": 1,
        "max_level": TIER1_MAX_LEVEL,
        "promotes_to": "swordmaster",
        "promotion_bonuses": {},
    },
    {
        "id": "lancer",
        "name": "Lancer",
        "allowed_weapon_types": ["lance"],
        "strength_mod": 0,
        "magic_mod": 0,
        "defense_mod": 1,
        "resistance_mod": 0,
        "tier": 1,
        "max_level": TIER1_MAX_LEVEL,
        "promotes_to": "paladin",
        "promotion_bonuses": {},
    },
    {
        "id": "axe_fighter",
        "name": "Axe Fighter",
        "allowed_weapon_types": ["axe"],
        "strength_mod": 2,
        "magic_mod": 0,
        "defense_mod": 0,
        "resistance_mod": -1,
        "tier": 1,
        "max_level": TIER1_MAX_LEVEL,
        "promotes_to": "berserker",
        "promotion_bonuses": {},
    },
    {
        "id": "rogue",
        "name": "Rogue",
        "allowed_weapon_types": ["dagger"],
        "strength_mod": 0,
        "magic_mod": 0,
        "defense_mod": 0,
        "resistance_mod": 1,
        "tier": 1,
        "max_level": TIER1_MAX_LEVEL,
        "promotes_to": "assassin",
        "promotion_bonuses": {},
    },
    {
        "id": "elementalist",
        "name": "Elementalist",
        "allowed_weapon_types": ["fire", "thunder"],
        "strength_mod": -1,
        "magic_mod": 2,
        "defense_mod": 0,
        "resistance_mod": 1,
        "tier": 1,
        "max_level": TIER1_MAX_LEVEL,
        "promotes_to": "sage",
        "promotion_bonuses": {},
    },
    {
        "id": "druid",
        "name": "Druid",
        "allowed_weapon_types": ["earth", "wind"],
        "strength_mod": 0,
        "magic_mod": 2,
        "defense_mod": 1,
        "resistance_mod": 0,
        "tier": 1,
        "max_level": TIER1_MAX_LEVEL,
        "promotes_to": "archsage",
        "promotion_bonuses": {},
    },
    # --- Tier 2 (promoted classes, Lv cap 20) -------------------------------
    {
        "id": "swordmaster",
        "name": "Swordmaster",
        "allowed_weapon_types": ["sword"],
        "strength_mod": 2,
        "magic_mod": 0,
        "defense_mod": 1,
        "resistance_mod": 1,
        "tier": 2,
        "max_level": TIER2_MAX_LEVEL,
        "promotes_to": None,
        "promotion_bonuses": {"max_hp": 3, "strength": 2, "speed": 2, "defense": 1, "resistance": 1, "crit": 5},
    },
    {
        "id": "paladin",
        "name": "Paladin",
        "allowed_weapon_types": ["lance"],
        "strength_mod": 1,
        "magic_mod": 0,
        "defense_mod": 2,
        "resistance_mod": 1,
        "tier": 2,
        "max_level": TIER2_MAX_LEVEL,
        "promotes_to": None,
        "promotion_bonuses": {"max_hp": 4, "strength": 2, "defense": 2, "resistance": 1, "speed": 1, "move": 1},
    },
    {
        "id": "berserker",
        "name": "Berserker",
        "allowed_weapon_types": ["axe"],
        "strength_mod": 3,
        "magic_mod": 0,
        "defense_mod": 1,
        "resistance_mod": -1,
        "tier": 2,
        "max_level": TIER2_MAX_LEVEL,
        "promotes_to": None,
        "promotion_bonuses": {"max_hp": 5, "strength": 3, "defense": 1, "speed": 1, "crit": 5},
    },
    {
        "id": "assassin",
        "name": "Assassin",
        "allowed_weapon_types": ["dagger"],
        "strength_mod": 1,
        "magic_mod": 0,
        "defense_mod": 0,
        "resistance_mod": 1,
        "tier": 2,
        "max_level": TIER2_MAX_LEVEL,
        "promotes_to": None,
        "promotion_bonuses": {"max_hp": 3, "strength": 2, "speed": 2, "resistance": 1, "crit": 8, "move": 1},
    },
    {
        "id": "sage",
        "name": "Sage",
        "allowed_weapon_types": ["fire", "thunder"],
        "strength_mod": -1,
        "magic_mod": 3,
        "defense_mod": 1,
        "resistance_mod": 2,
        "tier": 2,
        "max_level": TIER2_MAX_LEVEL,
        "promotes_to": None,
        "promotion_bonuses": {"max_hp": 3, "magic": 3, "resistance": 2, "speed": 1, "defense": 1},
    },
    {
        "id": "archsage",
        "name": "Archsage",
        "allowed_weapon_types": ["earth", "wind"],
        "strength_mod": 0,
        "magic_mod": 3,
        "defense_mod": 2,
        "resistance_mod": 1,
        "tier": 2,
        "max_level": TIER2_MAX_LEVEL,
        "promotes_to": None,
        "promotion_bonuses": {"max_hp": 3, "magic": 3, "defense": 1, "resistance": 2, "speed": 1},
    },
]

CLASS_LOOKUP = {profile["id"]: profile for profile in CLASS_PROFILES}


def get_max_level(class_id):
    profile = CLASS_LOOKUP.get(class_id)
    return profile["max_level"] if profile else TIER1_MAX_LEVEL


def get_promotion_target(class_id):
    """Return the tier-2 class_id this class promotes into, or None."""
    profile = CLASS_LOOKUP.get(class_id)
    return profile.get("promotes_to") if profile else None


def get_promotion_bonuses(class_id):
    profile = CLASS_LOOKUP.get(class_id)
    return dict(profile.get("promotion_bonuses", {})) if profile else {}

WEAPON_LIBRARY = [
    {"id": "iron_sword", "name": "Iron Sword", "weapon_type": "sword", "damage_kind": PHYSICAL, "might": 5, "range": 1, "cost": 120, "crit_bonus": 0, "starter": True},
    {"id": "steel_sword", "name": "Steel Sword", "weapon_type": "sword", "damage_kind": PHYSICAL, "might": 6, "range": 1, "cost": 170, "crit_bonus": 0, "starter": True},
    {"id": "silver_sword", "name": "Silver Sword", "weapon_type": "sword", "damage_kind": PHYSICAL, "might": 8, "range": 1, "cost": 260, "crit_bonus": 0, "starter": False},
    {"id": "killer_sword", "name": "Killer Sword", "weapon_type": "sword", "damage_kind": PHYSICAL, "might": 6, "range": 1, "cost": 220, "crit_bonus": 30, "starter": False},
    {"id": "swift_blade", "name": "Swift Blade", "weapon_type": "sword", "damage_kind": PHYSICAL, "might": 4, "range": 1, "cost": 140, "crit_bonus": 0, "starter": True},
    {"id": "iron_lance", "name": "Iron Lance", "weapon_type": "lance", "damage_kind": PHYSICAL, "might": 5, "range": 1, "cost": 130, "crit_bonus": 0, "starter": True},
    {"id": "steel_lance", "name": "Steel Lance", "weapon_type": "lance", "damage_kind": PHYSICAL, "might": 6, "range": 1, "cost": 180, "crit_bonus": 0, "starter": True},
    {"id": "silver_lance", "name": "Silver Lance", "weapon_type": "lance", "damage_kind": PHYSICAL, "might": 8, "range": 1, "cost": 270, "crit_bonus": 0, "starter": False},
    {"id": "killer_lance", "name": "Killer Lance", "weapon_type": "lance", "damage_kind": PHYSICAL, "might": 6, "range": 1, "cost": 225, "crit_bonus": 30, "starter": False},
    {"id": "heavy_lance", "name": "Heavy Lance", "weapon_type": "lance", "damage_kind": PHYSICAL, "might": 6, "range": 1, "cost": 150, "crit_bonus": 0, "starter": True},
    {"id": "pike", "name": "Pike", "weapon_type": "lance", "damage_kind": PHYSICAL, "might": 4, "range": 2, "cost": 145, "crit_bonus": 0, "starter": True},
    {"id": "iron_axe", "name": "Iron Axe", "weapon_type": "axe", "damage_kind": PHYSICAL, "might": 6, "range": 1, "cost": 140, "crit_bonus": 0, "starter": True},
    {"id": "steel_axe", "name": "Steel Axe", "weapon_type": "axe", "damage_kind": PHYSICAL, "might": 7, "range": 1, "cost": 190, "crit_bonus": 0, "starter": True},
    {"id": "silver_axe", "name": "Silver Axe", "weapon_type": "axe", "damage_kind": PHYSICAL, "might": 9, "range": 1, "cost": 280, "crit_bonus": 0, "starter": False},
    {"id": "killer_axe", "name": "Killer Axe", "weapon_type": "axe", "damage_kind": PHYSICAL, "might": 7, "range": 1, "cost": 235, "crit_bonus": 30, "starter": False},
    {"id": "battle_axe", "name": "Battle Axe", "weapon_type": "axe", "damage_kind": PHYSICAL, "might": 7, "range": 1, "cost": 165, "crit_bonus": 0, "starter": True},
    {"id": "hand_axe", "name": "Hand Axe", "weapon_type": "axe", "damage_kind": PHYSICAL, "might": 5, "range": 2, "cost": 155, "crit_bonus": 0, "starter": True},
    {"id": "iron_dagger", "name": "Iron Dagger", "weapon_type": "dagger", "damage_kind": PHYSICAL, "might": 4, "range": 1, "cost": 115, "crit_bonus": 0, "starter": True},
    {"id": "steel_dagger", "name": "Steel Dagger", "weapon_type": "dagger", "damage_kind": PHYSICAL, "might": 5, "range": 1, "cost": 155, "crit_bonus": 0, "starter": True},
    {"id": "silver_dagger", "name": "Silver Dagger", "weapon_type": "dagger", "damage_kind": PHYSICAL, "might": 7, "range": 1, "cost": 240, "crit_bonus": 0, "starter": False},
    {"id": "killer_dagger", "name": "Killer Dagger", "weapon_type": "dagger", "damage_kind": PHYSICAL, "might": 5, "range": 1, "cost": 210, "crit_bonus": 30, "starter": False},
    {"id": "stiletto", "name": "Stiletto", "weapon_type": "dagger", "damage_kind": PHYSICAL, "might": 5, "range": 1, "cost": 135, "crit_bonus": 0, "starter": True},
    {"id": "throwing_knife", "name": "Throwing Knife", "weapon_type": "dagger", "damage_kind": PHYSICAL, "might": 3, "range": 2, "cost": 145, "crit_bonus": 0, "starter": True},
    {"id": "fire_tome", "name": "Fire Tome", "weapon_type": "fire", "damage_kind": MAGICAL, "might": 5, "range": 2, "cost": 160, "crit_bonus": 0, "starter": True},
    {"id": "steel_fire_tome", "name": "Steel Fire", "weapon_type": "fire", "damage_kind": MAGICAL, "might": 6, "range": 2, "cost": 190, "crit_bonus": 0, "starter": True},
    {"id": "silver_fire_tome", "name": "Silver Fire", "weapon_type": "fire", "damage_kind": MAGICAL, "might": 8, "range": 2, "cost": 270, "crit_bonus": 0, "starter": False},
    {"id": "ember_tome", "name": "Ember Tome", "weapon_type": "fire", "damage_kind": MAGICAL, "might": 4, "range": 2, "cost": 140, "crit_bonus": 0, "starter": True},
    {"id": "thunder_tome", "name": "Thunder Tome", "weapon_type": "thunder", "damage_kind": MAGICAL, "might": 6, "range": 2, "cost": 170, "crit_bonus": 0, "starter": True},
    {"id": "steel_thunder_tome", "name": "Steel Thunder", "weapon_type": "thunder", "damage_kind": MAGICAL, "might": 7, "range": 2, "cost": 200, "crit_bonus": 0, "starter": True},
    {"id": "silver_thunder_tome", "name": "Silver Thunder", "weapon_type": "thunder", "damage_kind": MAGICAL, "might": 9, "range": 2, "cost": 285, "crit_bonus": 0, "starter": False},
    {"id": "spark_tome", "name": "Spark Tome", "weapon_type": "thunder", "damage_kind": MAGICAL, "might": 4, "range": 2, "cost": 150, "crit_bonus": 0, "starter": True},
    {"id": "earth_tome", "name": "Earth Tome", "weapon_type": "earth", "damage_kind": MAGICAL, "might": 5, "range": 2, "cost": 160, "crit_bonus": 0, "starter": True},
    {"id": "steel_earth_tome", "name": "Steel Earth", "weapon_type": "earth", "damage_kind": MAGICAL, "might": 6, "range": 2, "cost": 190, "crit_bonus": 0, "starter": True},
    {"id": "silver_earth_tome", "name": "Silver Earth", "weapon_type": "earth", "damage_kind": MAGICAL, "might": 8, "range": 2, "cost": 270, "crit_bonus": 0, "starter": False},
    {"id": "stone_tome", "name": "Stone Tome", "weapon_type": "earth", "damage_kind": MAGICAL, "might": 6, "range": 2, "cost": 170, "crit_bonus": 0, "starter": True},
    {"id": "wind_tome", "name": "Wind Tome", "weapon_type": "wind", "damage_kind": MAGICAL, "might": 4, "range": 2, "cost": 150, "crit_bonus": 0, "starter": True},
    {"id": "steel_wind_tome", "name": "Steel Wind", "weapon_type": "wind", "damage_kind": MAGICAL, "might": 5, "range": 2, "cost": 180, "crit_bonus": 0, "starter": True},
    {"id": "silver_wind_tome", "name": "Silver Wind", "weapon_type": "wind", "damage_kind": MAGICAL, "might": 7, "range": 2, "cost": 250, "crit_bonus": 0, "starter": False},
    {"id": "gale_tome", "name": "Gale Tome", "weapon_type": "wind", "damage_kind": MAGICAL, "might": 5, "range": 2, "cost": 160, "crit_bonus": 0, "starter": True},
]

WEAPON_LOOKUP = {weapon["id"]: weapon for weapon in WEAPON_LIBRARY}


def get_class_profile(class_id):
    return CLASS_LOOKUP[class_id]


TIER1_PROFILES = [profile for profile in CLASS_PROFILES if profile.get("tier", 1) == 1]


def random_class_profile():
    # Only base (tier-1) classes can be rolled for new recruits / enemies;
    # tier-2 classes are reached exclusively through promotion.
    return random.choice(TIER1_PROFILES)


def get_weapon_spec(weapon_id):
    return WEAPON_LOOKUP[weapon_id]


def get_allowed_weapon_specs(class_id):
    profile = get_class_profile(class_id)
    allowed_types = set(profile["allowed_weapon_types"])
    return [
        weapon
        for weapon in WEAPON_LIBRARY
        if weapon["weapon_type"] in allowed_types
    ]


def choose_starting_weapon_specs(class_id, count=2):
    pool = [weapon for weapon in get_allowed_weapon_specs(class_id) if weapon.get("starter", True)]
    if len(pool) < count:
        pool = get_allowed_weapon_specs(class_id)
    if len(pool) <= count:
        return list(pool)
    return random.sample(pool, count)


def build_stats(spec, class_profile):
    base_strength = spec["strength"]
    base_magic = spec.get("magic", max(1, spec["strength"] - 2))
    base_defense = spec["defense"]
    base_resistance = spec.get("resistance", max(0, spec["defense"] - 2))

    return {
        "strength": max(0, base_strength + class_profile["strength_mod"]),
        "magic": max(0, base_magic + class_profile["magic_mod"]),
        "defense": max(0, base_defense + class_profile["defense_mod"]),
        "resistance": max(0, base_resistance + class_profile["resistance_mod"]),
    }
