"""
combat.py
Combat with hit rate (based on speed)
"""

import random

from terrain import get_terrain_avoid_bonus, get_terrain_def_bonus


def get_attack_tiles_from_position(origin, attack_range, size):
    ox, oy = origin
    cells = []
    for x in range(size):
        for y in range(size):
            distance = abs(x - ox) + abs(y - oy)
            if 0 < distance <= attack_range:
                cells.append((x, y))
    return cells


def get_attack_tiles(unit, size, origin=None):
    if not unit.weapon:
        return []
    attack_origin = origin if origin is not None else unit.get_position()
    return get_attack_tiles_from_position(attack_origin, unit.weapon.range, size)


def in_range(a, b):
    if not a.weapon:
        return False
    ax, ay = a.get_position()
    bx, by = b.get_position()
    return 0 < abs(ax - bx) + abs(ay - by) <= a.weapon.range


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
    terrain_type = get_unit_terrain(unit)
    terrain_defense = get_terrain_def_bonus(terrain_type)
    return unit.defense + terrain_defense


def hit_rate(attacker, defender):
    rate = 70 + attacker.speed * 5 - avoid_amount(defender)
    return max(30, min(95, rate))


def damage_amount(attacker, defender):
    return max(0, attacker.get_attack() - defense_amount(defender))


def expected_hp_after_attack(attacker, defender):
    return max(0, defender.hp - damage_amount(attacker, defender))


def attack_preview(attacker, defender):
    counter = in_range(defender, attacker)
    return {
        "attacker_hit": hit_rate(attacker, defender),
        "attacker_damage": damage_amount(attacker, defender),
        "defender_hp": expected_hp_after_attack(attacker, defender),
        "counter": counter,
        "defender_hit": hit_rate(defender, attacker) if counter else 0,
        "defender_damage": damage_amount(defender, attacker) if counter else 0,
        "attacker_hp": expected_hp_after_attack(defender, attacker) if counter else attacker.hp,
    }


def attack_once(attacker, defender):
    rate = hit_rate(attacker, defender)
    if random.randint(1, 100) <= rate:
        dmg = damage_amount(attacker, defender)
        defender.hp -= dmg
        return True, dmg
    return False, 0


def combat(a, b):
    log = []

    if not a.is_alive() or not b.is_alive() or not a.weapon:
        return log

    hit, dmg = attack_once(a, b)
    log.append((a.name, hit, dmg))

    if b.is_alive() and in_range(b, a):
        hit, dmg = attack_once(b, a)
        log.append((b.name, hit, dmg))

    return log
