"""
progression.py
Persistent unit progression, EXP, and roster helpers.
"""

import random

from constants import EXP_PER_LEVEL, PROMOTION_MIN_LEVEL
from inventory import Antidote, PromotionSeal, Potion
from unit import Unit
from unit_classes import (
    CLASS_PROFILES,
    WEAPON_LIBRARY,
    build_stats,
    choose_starting_weapon_specs,
    get_class_profile,
    get_max_level,
    get_promotion_bonuses,
    get_promotion_target,
    get_weapon_spec,
    random_class_profile,
)
from weapon import Weapon

PLAYER_TEMPLATES = [
    {
        "unit_id": "hero",
        "strength": 5,
        "defense": 5,
        "speed": 8,
        "move": 3,
        "max_hp": 18,
        "sprite_key": "F1",
        "inventory": [("potion", "Potion", 8)],
    },
    {
        "unit_id": "knight",
        "strength": 6,
        "defense": 7,
        "speed": 4,
        "move": 2,
        "max_hp": 20,
        "sprite_key": "M1",
        "inventory": [],
    },
]

NAME_POOL = [
    "Aldo",
    "Kael",
    "Mira",
    "Tessa",
    "Brant",
    "Riven",
    "Nia",
    "Orin",
    "Lyra",
    "Dane",
]

GROWTH_RATES = {
    "sword_fighter": {"max_hp": 0.65, "speed": 0.65, "strength": 0.55, "magic": 0.20, "defense": 0.35, "resistance": 0.30, "crit": 0.28},
    "lancer": {"max_hp": 0.70, "speed": 0.40, "strength": 0.50, "magic": 0.15, "defense": 0.55, "resistance": 0.30, "crit": 0.20},
    "axe_fighter": {"max_hp": 0.75, "speed": 0.35, "strength": 0.65, "magic": 0.10, "defense": 0.40, "resistance": 0.20, "crit": 0.18},
    "rogue": {"max_hp": 0.55, "speed": 0.70, "strength": 0.40, "magic": 0.20, "defense": 0.25, "resistance": 0.45, "crit": 0.40},
    "elementalist": {"max_hp": 0.45, "speed": 0.45, "strength": 0.10, "magic": 0.70, "defense": 0.20, "resistance": 0.55, "crit": 0.24},
    "druid": {"max_hp": 0.55, "speed": 0.35, "strength": 0.20, "magic": 0.65, "defense": 0.35, "resistance": 0.50, "crit": 0.22},
    # Tier 2 (promoted) — slightly higher growths than their base class.
    "swordmaster": {"max_hp": 0.70, "speed": 0.70, "strength": 0.60, "magic": 0.20, "defense": 0.40, "resistance": 0.35, "crit": 0.35},
    "paladin": {"max_hp": 0.75, "speed": 0.45, "strength": 0.55, "magic": 0.15, "defense": 0.60, "resistance": 0.35, "crit": 0.22},
    "berserker": {"max_hp": 0.80, "speed": 0.40, "strength": 0.70, "magic": 0.10, "defense": 0.45, "resistance": 0.25, "crit": 0.25},
    "assassin": {"max_hp": 0.60, "speed": 0.75, "strength": 0.45, "magic": 0.20, "defense": 0.30, "resistance": 0.50, "crit": 0.45},
    "sage": {"max_hp": 0.50, "speed": 0.50, "strength": 0.10, "magic": 0.75, "defense": 0.25, "resistance": 0.60, "crit": 0.26},
    "archsage": {"max_hp": 0.60, "speed": 0.40, "strength": 0.20, "magic": 0.70, "defense": 0.40, "resistance": 0.55, "crit": 0.24},
}

WEAPON_INDEX = {
    (
        weapon["name"],
        weapon["weapon_type"],
        weapon["damage_kind"],
        weapon["might"],
        weapon["range"],
    ): weapon["id"]
    for weapon in WEAPON_LIBRARY
}


def _make_item(spec):
    item_type = spec[0]
    if item_type == "potion":
        return Potion(spec[1], spec[2])
    if item_type == "antidote":
        return Antidote(spec[1])
    if item_type == "promotion_seal":
        return PromotionSeal(spec[1] if len(spec) > 1 else "Master Seal")
    return None


def _make_weapon_from_spec(weapon_spec):
    return Weapon(
        weapon_spec["name"],
        weapon_spec["weapon_type"],
        weapon_spec["damage_kind"],
        weapon_spec["might"],
        weapon_spec["range"],
        cost=weapon_spec["cost"],
        crit_bonus=weapon_spec.get("crit_bonus", 0),
        max_durability=weapon_spec.get("max_durability"),
    )


def serialize_item(item):
    if getattr(item, "item_type", None) == "weapon":
        key = (item.name, item.weapon_type, item.damage_kind, item.might, item.range)
        weapon_id = WEAPON_INDEX.get(key)
        if weapon_id is not None:
            return {
                "item_type": "weapon",
                "weapon_id": weapon_id,
                "durability": item.durability,
                "max_durability": item.max_durability,
            }
        return {
            "item_type": "weapon",
            "name": item.name,
            "weapon_type": item.weapon_type,
            "damage_kind": item.damage_kind,
            "might": item.might,
            "range": item.range,
            "cost": item.cost,
            "crit_bonus": getattr(item, "crit_bonus", 0),
            "durability": item.durability,
            "max_durability": item.max_durability,
        }

    if getattr(item, "item_type", None) == "potion":
        return {"item_type": "potion", "name": item.name, "heal_amount": item.heal_amount}

    if getattr(item, "item_type", None) == "antidote":
        return {"item_type": "antidote", "name": item.name}

    if getattr(item, "item_type", None) == "promotion_seal":
        return {"item_type": "promotion_seal", "name": item.name}

    return None


def deserialize_item(data):
    item_type = data.get("item_type")
    if item_type == "weapon":
        if "weapon_id" in data:
            item = _make_weapon_from_spec(get_weapon_spec(data["weapon_id"]))
            if "max_durability" in data:
                item.max_durability = max(1, int(data["max_durability"]))
            if "durability" in data:
                item.durability = max(0, min(item.max_durability, int(data["durability"])))
            return item
        return Weapon(
            data["name"],
            data["weapon_type"],
            data["damage_kind"],
            data["might"],
            data["range"],
            cost=data.get("cost", 0),
            crit_bonus=data.get("crit_bonus", 0),
            durability=data.get("durability"),
            max_durability=data.get("max_durability"),
        )
    if item_type == "potion":
        return Potion(data["name"], data["heal_amount"])
    if item_type == "antidote":
        return Antidote(data["name"])
    if item_type == "promotion_seal":
        return PromotionSeal(data.get("name", "Master Seal"))
    return None


def serialize_unit(unit):
    equipped_index = -1
    if unit.weapon in unit.inventory:
        equipped_index = unit.inventory.index(unit.weapon)

    return {
        "unit_id": unit.unit_id,
        "name": unit.name,
        "class_id": unit.class_id,
        "class_name": unit.unit_class,
        "allowed_weapon_types": list(unit.allowed_weapon_types),
        "level": unit.level,
        "exp": unit.exp,
        "hp": unit.hp,
        "max_hp": unit.max_hp,
        "strength": unit.strength,
        "magic": unit.magic,
        "defense": unit.defense,
        "resistance": unit.resistance,
        "speed": unit.speed,
        "crit": unit.crit,
        "move": unit.move,
        "sprite_key": unit.sprite_key,
        "inventory": [serialize_item(item) for item in unit.inventory if serialize_item(item) is not None],
        "equipped_index": equipped_index,
    }


def instantiate_player_unit(record, position):
    inventory = [deserialize_item(item_data) for item_data in record["inventory"]]
    inventory = [item for item in inventory if item is not None]
    weapon = None
    equipped_index = record.get("equipped_index", -1)
    if 0 <= equipped_index < len(inventory):
        weapon = inventory[equipped_index]

    unit = Unit(
        record["name"],
        record["strength"],
        record["magic"],
        record["defense"],
        record["resistance"],
        record["speed"],
        record["move"],
        weapon,
        record["class_name"],
        record["allowed_weapon_types"],
        inventory=inventory,
        max_hp=record["max_hp"],
        sprite_key=record.get("sprite_key"),
        class_id=record["class_id"],
        unit_id=record["unit_id"],
        level=record.get("level", 1),
        exp=record.get("exp", 0),
        crit=record.get("crit", 5),
        current_hp=record.get("hp", record["max_hp"]),
        persistent=True,
    )
    if unit.weapon is None and inventory:
        unit.equip_weapon(inventory[0])
    unit.set_position(position[0], position[1])
    return unit


def create_initial_roster():
    names = random.sample(NAME_POOL, len(PLAYER_TEMPLATES))
    roster = {}

    for template, name in zip(PLAYER_TEMPLATES, names):
        class_profile = random_class_profile()
        stats = build_stats(template, class_profile)
        class_weapons = [
            _make_weapon_from_spec(spec)
            for spec in choose_starting_weapon_specs(class_profile["id"], count=2)
        ]
        support_items = [
            _make_item(item_spec)
            for item_spec in template.get("inventory", [])
            if item_spec[0] != "weapon"
        ]
        inventory = class_weapons + [item for item in support_items if item is not None]
        roster[template["unit_id"]] = {
            "unit_id": template["unit_id"],
            "name": name,
            "class_id": class_profile["id"],
            "class_name": class_profile["name"],
            "allowed_weapon_types": list(class_profile["allowed_weapon_types"]),
            "level": 1,
            "exp": 0,
            "hp": template["max_hp"],
            "max_hp": template["max_hp"],
            "strength": stats["strength"],
            "magic": stats["magic"],
            "defense": stats["defense"],
            "resistance": stats["resistance"],
            "speed": template["speed"],
            "crit": random.randint(1, 10),
            "move": template["move"],
            "sprite_key": template["sprite_key"],
            "inventory": [serialize_item(item) for item in inventory],
            "equipped_index": 0 if class_weapons else -1,
        }

    return roster


def create_enemy_unit(spec):
    class_id = spec.get("class_id")
    class_profile = get_class_profile(class_id) if class_id else random_class_profile()
    stats = build_stats(spec, class_profile)
    weapons = [
        _make_weapon_from_spec(weapon_spec)
        for weapon_spec in choose_starting_weapon_specs(class_profile["id"], count=2)
    ]
    support_items = [
        _make_item(item_spec)
        for item_spec in spec.get("inventory", [])
        if item_spec[0] != "weapon"
    ]
    inventory = weapons + [item for item in support_items if item is not None]
    level = max(1, spec.get("level", 1))
    unit = Unit(
        spec["name"],
        stats["strength"],
        stats["magic"],
        stats["defense"],
        stats["resistance"],
        spec["speed"],
        spec["move"],
        weapons[0] if weapons else None,
        class_profile["name"],
        class_profile["allowed_weapon_types"],
        inventory=inventory,
        max_hp=spec["max_hp"],
        sprite_key=spec.get("sprite_key"),
        class_id=class_profile["id"],
        unit_id=spec.get("unit_id"),
        level=1,
        exp=0,
        crit=spec.get("crit", random.randint(1, 10)),
        persistent=False,
    )
    for _ in range(1, level):
        level_up(unit, heal_on_hp_gain=False)
    unit.hp = unit.max_hp
    return unit


def get_growth_rates(class_id):
    return GROWTH_RATES.get(class_id, GROWTH_RATES[CLASS_PROFILES[0]["id"]])


def is_at_max_level(unit):
    return unit.level >= get_max_level(unit.class_id)


def level_up(unit, heal_on_hp_gain=True):
    if is_at_max_level(unit):
        return {}
    rates = get_growth_rates(unit.class_id)
    gains = {}
    unit.level += 1

    for stat_name in ("max_hp", "speed", "strength", "magic", "defense", "resistance", "crit"):
        grew = random.random() < rates[stat_name]
        gains[stat_name] = 1 if grew else 0
        if not grew:
            continue

        if stat_name == "max_hp":
            unit.max_hp += 1
            if heal_on_hp_gain:
                unit.hp += 1
        else:
            setattr(unit, stat_name, getattr(unit, stat_name) + 1)

    unit.hp = min(unit.hp, unit.max_hp)
    return gains


def gain_exp(unit, amount):
    if amount <= 0:
        return []

    if is_at_max_level(unit):
        unit.exp = 0
        return []

    unit.exp += amount
    level_gains = []
    while unit.exp >= EXP_PER_LEVEL and not is_at_max_level(unit):
        unit.exp -= EXP_PER_LEVEL
        level_gains.append(level_up(unit))
    if is_at_max_level(unit):
        unit.exp = 0
    return level_gains


def can_promote(unit):
    """A unit may promote once it reaches PROMOTION_MIN_LEVEL on a tier-1 class."""
    if not unit.class_id or not get_promotion_target(unit.class_id):
        return False
    return unit.level >= PROMOTION_MIN_LEVEL


def promote(unit):
    """Promote a tier-1 unit into its fixed tier-2 class. Returns a result dict
    describing the change, or None if the unit cannot promote."""
    if not can_promote(unit):
        return None

    target_id = get_promotion_target(unit.class_id)
    target = get_class_profile(target_id)
    bonuses = get_promotion_bonuses(target_id)

    for stat_name, amount in bonuses.items():
        if stat_name == "max_hp":
            unit.max_hp += amount
            unit.hp = min(unit.max_hp, unit.hp + amount)
        elif stat_name == "move":
            unit.move += amount
        else:
            setattr(unit, stat_name, getattr(unit, stat_name, 0) + amount)

    old_class_name = unit.unit_class
    unit.class_id = target_id
    unit.unit_class = target["name"]
    unit.allowed_weapon_types = tuple(target["allowed_weapon_types"])
    unit.level = 1
    unit.exp = 0

    return {
        "unit_name": unit.name,
        "old_class_name": old_class_name,
        "new_class_id": target_id,
        "new_class_name": target["name"],
        "bonuses": bonuses,
    }


def calculate_attack_exp(attacker, defender, damage_dealt):
    if damage_dealt <= 0:
        return 1 if defender.level <= attacker.level - 2 else 0

    level_delta = defender.level - attacker.level
    if level_delta <= -2:
        return 1
    if level_delta == -1:
        return max(1, damage_dealt)

    multiplier = 2 + max(0, level_delta)
    return max(1, damage_dealt * multiplier)


def calculate_defend_exp(defender, attacker, damage_taken):
    if damage_taken <= 0:
        return 0

    base = calculate_attack_exp(defender, attacker, damage_taken)
    if attacker.level > defender.level:
        return max(1, base * 10)
    return max(1, base)
