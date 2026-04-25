"""
combat.py
Combat with hit rate (based on speed)
"""

import random

from progression import calculate_attack_exp, calculate_defend_exp, gain_exp
from terrain import (
    get_terrain_avoid_bonus,
    get_terrain_def_bonus,
    get_terrain_hit_bonus,
    get_terrain_range_bonus,
    get_thunder_damage_multiplier,
)

FOLLOW_UP_SPEED_GAP = 4


def get_weapon_range_bounds(weapon_or_range):
    if hasattr(weapon_or_range, "range"):
        raw_range = weapon_or_range.range
    else:
        raw_range = weapon_or_range

    if isinstance(raw_range, (tuple, list)) and len(raw_range) >= 2:
        min_range = int(raw_range[0])
        max_range = int(raw_range[1])
    else:
        min_range = 1
        max_range = int(raw_range)

    return max(1, min_range), max(min_range, max_range)


def get_attack_tiles_from_position(origin, weapon_or_range, game_map_or_size):
    ox, oy = origin
    if hasattr(game_map_or_size, "size"):
        size = game_map_or_size.size
        terrain_type = game_map_or_size.get_terrain(ox, oy)
    else:
        size = int(game_map_or_size)
        terrain_type = None

    min_range, max_range = get_weapon_range_bounds(weapon_or_range)
    if hasattr(weapon_or_range, "range") and max_range > 1:
        max_range += get_terrain_range_bonus(terrain_type)
        max_range = max(min_range, max_range)

    cells = set()
    for x in range(size):
        for y in range(size):
            distance = abs(x - ox) + abs(y - oy)
            if min_range <= distance <= max_range:
                cells.add((x, y))
    return cells


def get_attack_tiles(unit, size, origin=None):
    if not unit.has_usable_weapon():
        return []
    attack_origin = origin if origin is not None else unit.get_position()
    return sorted(get_attack_tiles_from_position(attack_origin, unit.weapon, size))


def effective_attack_range(unit):
    if not unit.has_usable_weapon():
        return 0
    terrain_type = get_unit_terrain(unit)
    range_bonus = 0
    if unit.weapon.range > 1:
        range_bonus = get_terrain_range_bonus(terrain_type)
    return max(1, unit.weapon.range + range_bonus)


def in_range(a, b):
    if not a.has_usable_weapon():
        return False
    ax, ay = a.get_position()
    bx, by = b.get_position()
    return 0 < abs(ax - bx) + abs(ay - by) <= effective_attack_range(a)


def get_unit_terrain(unit):
    if not unit or not unit.game_map:
        return None
    x, y = unit.get_position()
    if x is None or y is None:
        return None
    return unit.game_map.get_terrain(x, y)


def avoid_amount(unit):
    terrain_type = get_unit_terrain(unit)
    terrain_avoid = get_terrain_avoid_bonus(terrain_type)
    return unit.speed * 5 + terrain_avoid


def defense_amount(unit):
    return defense_amount_for_kind(unit, "physical")


def defense_amount_for_kind(unit, damage_kind):
    terrain_type = get_unit_terrain(unit)
    terrain_defense = get_terrain_def_bonus(terrain_type)
    if damage_kind == "magical":
        return unit.resistance + terrain_defense
    return unit.defense + terrain_defense


def hit_rate(attacker, defender):
    terrain_type = get_unit_terrain(attacker)
    rate = 70 + attacker.speed * 5 + get_terrain_hit_bonus(terrain_type) - avoid_amount(defender)
    return max(30, min(95, rate))


def damage_amount(attacker, defender):
    if not attacker.has_usable_weapon():
        return 0
    damage = max(
        0,
        attacker.get_attack() - defense_amount_for_kind(defender, attacker.weapon.damage_kind),
    )
    if attacker.weapon.weapon_type == "thunder":
        damage = int(damage * get_thunder_damage_multiplier(get_unit_terrain(defender)))
    return damage


def crit_rate(attacker):
    if not attacker.has_usable_weapon():
        return 0
    return max(0, min(100, attacker.crit + getattr(attacker.weapon, "crit_bonus", 0)))


def can_counterattack(attacker, defender):
    return defender.is_alive() and in_range(defender, attacker)


def can_follow_up(attacker, defender):
    return (
        attacker.is_alive()
        and defender.is_alive()
        and attacker.has_usable_weapon()
        and attacker.speed - defender.speed >= FOLLOW_UP_SPEED_GAP
    )


def get_combat_sequence(attacker, defender):
    sequence = []
    if not attacker.is_alive() or not defender.is_alive() or not attacker.has_usable_weapon():
        return sequence

    sequence.append((attacker, defender))
    counter = can_counterattack(attacker, defender)
    if counter:
        sequence.append((defender, attacker))

    if can_follow_up(attacker, defender):
        sequence.append((attacker, defender))
    elif counter and can_follow_up(defender, attacker):
        sequence.append((defender, attacker))

    return sequence


def get_follow_up_owner(attacker, defender):
    if can_follow_up(attacker, defender):
        return attacker
    if can_counterattack(attacker, defender) and can_follow_up(defender, attacker):
        return defender
    return None


def build_forecast_side(attacker, defender, can_strike):
    return {
        "name": attacker.name,
        "weapon": attacker.weapon.name if attacker.weapon else "None",
        "weapon_durability": (
            f"{attacker.weapon.durability}/{attacker.weapon.max_durability}"
            if attacker.weapon
            else "--"
        ),
        "hp": attacker.hp,
        "atk": damage_amount(attacker, defender) if can_strike else 0,
        "hit": hit_rate(attacker, defender) if can_strike else 0,
        "crit": crit_rate(attacker) if can_strike else 0,
    }


def expected_hp_after_attack(attacker, defender):
    return max(0, defender.hp - damage_amount(attacker, defender))


def attack_preview(attacker, defender):
    counter = can_counterattack(attacker, defender)
    sequence = get_combat_sequence(attacker, defender)
    follow_up_owner = get_follow_up_owner(attacker, defender)
    attacker_hits = sum(1 for actor, _ in sequence if actor is attacker)
    defender_hits = sum(1 for actor, _ in sequence if actor is defender)
    attacker_side = build_forecast_side(attacker, defender, True)
    defender_side = build_forecast_side(defender, attacker, counter)
    return {
        "attacker_hit": attacker_side["hit"],
        "attacker_damage": attacker_side["atk"],
        "attacker_crit": attacker_side["crit"],
        "defender_hp": expected_hp_after_attack(attacker, defender),
        "counter": counter,
        "defender_hit": defender_side["hit"],
        "defender_damage": defender_side["atk"],
        "defender_crit": defender_side["crit"],
        "attacker_hp": expected_hp_after_attack(defender, attacker) if counter else attacker.hp,
        "attacker": attacker_side,
        "defender": defender_side,
        "sequence": sequence,
        "sequence_text": " -> ".join(actor.name for actor, _ in sequence) if sequence else "No combat",
        "attacker_hits": attacker_hits,
        "defender_hits": defender_hits,
        "follow_up": (
            attacker.name if follow_up_owner is attacker else defender.name if follow_up_owner is defender else "None"
        ),
    }


def attack_once(attacker, defender):
    rate = hit_rate(attacker, defender)
    if random.randint(1, 100) <= rate:
        dmg = damage_amount(attacker, defender)
        if random.randint(1, 100) <= crit_rate(attacker):
            dmg *= 3
        defender.hp -= dmg
        return True, dmg
    return False, 0


def roll_attack_result(attacker, defender):
    weapon_name = attacker.weapon.name if attacker.weapon else "None"
    rate = hit_rate(attacker, defender)
    hit = random.randint(1, 100) <= rate
    critical = hit and random.randint(1, 100) <= crit_rate(attacker)
    damage = damage_amount(attacker, defender) if hit else 0
    if critical:
        damage *= 3
    return {
        "attacker_name": attacker.name,
        "weapon_name": weapon_name,
        "hit": hit,
        "damage": damage,
        "critical": critical,
    }


def _format_level_up_events(unit, old_level, level_gains):
    events = []
    current_level = old_level

    for gains in level_gains:
        next_level = current_level + 1
        events.append(f"{unit.name} leveled up: Lv {current_level} -> Lv {next_level}")
        gained_stats = []
        for stat_name, label in (
            ("max_hp", "HP"),
            ("speed", "SPD"),
            ("strength", "STR"),
            ("magic", "MAG"),
            ("defense", "DEF"),
            ("resistance", "RES"),
            ("crit", "CRT"),
        ):
            if gains.get(stat_name, 0) > 0:
                gained_stats.append(f"{label} +1")
        events.append(", ".join(gained_stats) if gained_stats else "No stat increases")
        current_level = next_level

    return events


def _apply_exp_events(unit, amount):
    if amount <= 0:
        return [], []

    old_level = unit.level
    level_gains = gain_exp(unit, amount)
    events = [
        f"{unit.name} gained {amount} EXP",
        f"{unit.name} EXP: {unit.exp} / 100",
    ]
    events.extend(_format_level_up_events(unit, old_level, level_gains))
    level_up_results = []
    current_level = old_level
    for gains in level_gains:
        next_level = current_level + 1
        stat_lines = []
        for stat_name, label in (
            ("max_hp", "HP"),
            ("speed", "SPD"),
            ("strength", "STR"),
            ("magic", "MAG"),
            ("defense", "DEF"),
            ("resistance", "RES"),
            ("crit", "CRT"),
        ):
            if gains.get(stat_name, 0) > 0:
                stat_lines.append(f"{label} +1")
        level_up_results.append(
            {
                "unit_name": unit.name,
                "old_level": current_level,
                "new_level": next_level,
                "gains": gains,
                "stat_lines": stat_lines or ["No stat increases"],
            }
        )
        current_level = next_level
    return events, level_up_results


def _apply_capped_exp_events(unit, amount, awarded_exp):
    remaining = max(0, 100 - awarded_exp.get(unit, 0))
    actual_amount = min(max(0, amount), remaining)
    if actual_amount <= 0:
        return [], []

    awarded_exp[unit] = awarded_exp.get(unit, 0) + actual_amount
    return _apply_exp_events(unit, actual_amount)


def consume_weapon_use(attacker):
    if not attacker.has_usable_weapon():
        return []

    weapon = attacker.weapon
    weapon.consume_use()
    if weapon.is_usable():
        return []

    attacker.remove_item(weapon)
    attacker.weapon = None
    return [f"{attacker.name}'s {weapon.name} broke!"]


def apply_attack_result(attacker, defender, attack_result, awarded_exp=None):
    if awarded_exp is None:
        awarded_exp = {}

    attack_entry = (
        attack_result["attacker_name"],
        attack_result["hit"],
        attack_result["damage"],
        attack_result.get("critical", False),
    )
    events = consume_weapon_use(attacker)
    level_ups = []

    if attack_result["hit"]:
        if attack_result.get("critical", False):
            events.append(f"{attacker.name} landed a critical hit!")
            events.append("Damage x3")
        defender.hp -= attack_result["damage"]
        exp_events, level_up_results = _apply_capped_exp_events(
            attacker,
            calculate_attack_exp(attacker, defender, attack_result["damage"]),
            awarded_exp,
        )
        events.extend(exp_events)
        level_ups.extend(level_up_results)
        exp_events, level_up_results = _apply_capped_exp_events(
            defender,
            calculate_defend_exp(defender, attacker, attack_result["damage"]),
            awarded_exp,
        )
        events.extend(exp_events)
        level_ups.extend(level_up_results)

    return {
        "attack": attack_entry,
        "events": events,
        "level_ups": level_ups,
    }


def combat(a, b):
    result = {"attacks": [], "events": []}
    awarded_exp = {a: 0, b: 0}

    if not a.is_alive() or not b.is_alive() or not a.has_usable_weapon():
        return result

    for attacker, defender in get_combat_sequence(a, b):
        if not attacker.is_alive() or not defender.is_alive() or not attacker.has_usable_weapon():
            continue
        attack_result = roll_attack_result(attacker, defender)
        applied = apply_attack_result(attacker, defender, attack_result, awarded_exp)
        result["attacks"].append(applied["attack"])
        result["events"].extend(applied["events"])
        if not defender.is_alive():
            break

    return result
