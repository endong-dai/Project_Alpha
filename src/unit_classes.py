"""
unit_classes.py
Class and weapon definitions for battle units.
"""

import random

PHYSICAL = "physical"
MAGICAL = "magical"

CLASS_PROFILES = [
    {
        "id": "sword_fighter",
        "name": "Sword Fighter",
        "allowed_weapon_types": ["sword"],
        "strength_mod": 1,
        "magic_mod": 0,
        "defense_mod": 0,
        "resistance_mod": 0,
    },
    {
        "id": "lancer",
        "name": "Lancer",
        "allowed_weapon_types": ["lance"],
        "strength_mod": 0,
        "magic_mod": 0,
        "defense_mod": 1,
        "resistance_mod": 0,
    },
    {
        "id": "axe_fighter",
        "name": "Axe Fighter",
        "allowed_weapon_types": ["axe"],
        "strength_mod": 2,
        "magic_mod": 0,
        "defense_mod": 0,
        "resistance_mod": -1,
    },
    {
        "id": "rogue",
        "name": "Rogue",
        "allowed_weapon_types": ["dagger"],
        "strength_mod": 0,
        "magic_mod": 0,
        "defense_mod": 0,
        "resistance_mod": 1,
    },
    {
        "id": "elementalist",
        "name": "Elementalist",
        "allowed_weapon_types": ["fire", "thunder"],
        "strength_mod": -1,
        "magic_mod": 2,
        "defense_mod": 0,
        "resistance_mod": 1,
    },
    {
        "id": "druid",
        "name": "Druid",
        "allowed_weapon_types": ["earth", "wind"],
        "strength_mod": 0,
        "magic_mod": 2,
        "defense_mod": 1,
        "resistance_mod": 0,
    },
]

CLASS_LOOKUP = {profile["id"]: profile for profile in CLASS_PROFILES}

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


def random_class_profile():
    return random.choice(CLASS_PROFILES)


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
