"""
balance_sim.py
Monte-Carlo balance simulation for 阶段4 (no pytest / pygame needed).

Two reports:
  1) Weapon-triangle win rates  — same-stat duels, only weapon color differs,
     to confirm advantage/neutral/disadvantage move the win rate the right way.
  2) Growth curves              — average stats at Tier1 Lv20 and (after a
     promotion) Tier2 Lv20, per base class, to eyeball the progression curve.

Usage:  python3 balance_sim.py [trials]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from combat import crit_rate, damage_amount, get_combat_sequence, hit_rate  # noqa: E402
from progression import create_enemy_unit, level_up, promote  # noqa: E402
from unit import Unit  # noqa: E402
from unit_classes import TIER1_PROFILES  # noqa: E402
from weapon import Weapon  # noqa: E402

GROWTH_STATS = ("max_hp", "strength", "magic", "defense", "resistance", "speed", "crit")


# --------------------------------------------------------------------------- #
# 1) Weapon triangle win rates
# --------------------------------------------------------------------------- #
def _duelist(weapon_type, damage_kind="physical"):
    weapon = Weapon(weapon_type, weapon_type, damage_kind, 5, 1)
    unit = Unit(
        "Duelist", strength=8, magic=8, defense=4, resistance=4, speed=6, move=4,
        weapon=weapon, unit_class="T", allowed_weapon_types=[weapon_type],
        max_hp=30, class_id="sword_fighter", crit=5,
    )
    return unit


def _one_strike(attacker, defender):
    if random.randint(1, 100) <= hit_rate(attacker, defender):
        dmg = damage_amount(attacker, defender)
        if random.randint(1, 100) <= crit_rate(attacker):
            dmg *= 3
        defender.hp -= dmg


def _simulate_battle(attacker_type, defender_type):
    # Fresh full-HP units each battle; no EXP/level-ups to avoid polluting stats.
    attacker = _duelist(attacker_type)
    defender = _duelist(defender_type)
    attacker.set_position(0, 0)
    defender.set_position(0, 1)
    rounds = 0
    while attacker.is_alive() and defender.is_alive() and rounds < 100:
        for striker, target in get_combat_sequence(attacker, defender):
            if striker.is_alive() and target.is_alive():
                _one_strike(striker, target)
        rounds += 1
    if attacker.is_alive() and not defender.is_alive():
        return "attacker"
    if defender.is_alive() and not attacker.is_alive():
        return "defender"
    return "draw"


def report_triangle(trials):
    print("=" * 60)
    print("1) 武器三角胜率 (attacker 持剑/红, 双方属性相同, attacker 先手)")
    print("=" * 60)
    scenarios = [
        ("优势  (red vs green=axe)", "sword", "axe"),
        ("中立  (red vs colorless=dagger)", "sword", "dagger"),
        ("劣势  (red vs blue=lance)", "sword", "lance"),
    ]
    for label, atk, dfn in scenarios:
        wins = sum(1 for _ in range(trials) if _simulate_battle(atk, dfn) == "attacker")
        print(f"  {label:<34} attacker 胜率 {wins / trials:6.1%}")
    print()


# --------------------------------------------------------------------------- #
# 2) Growth curves
# --------------------------------------------------------------------------- #
def _grow_to_20(unit):
    while unit.level < 20:
        level_up(unit)


def _avg_stats(class_id, trials, promote_after):
    totals = {stat: 0 for stat in GROWTH_STATS}
    spec = {
        "name": "Sim", "class_id": class_id,
        "strength": 5, "magic": 5, "defense": 5, "resistance": 5,
        "speed": 5, "move": 4, "max_hp": 18, "level": 1,
    }
    for _ in range(trials):
        unit = create_enemy_unit(spec)
        _grow_to_20(unit)
        if promote_after:
            promote(unit)
            _grow_to_20(unit)
        for stat in GROWTH_STATS:
            totals[stat] += getattr(unit, stat)
    return {stat: totals[stat] / trials for stat in GROWTH_STATS}


def report_growth(trials):
    print("=" * 60)
    print(f"2) 成长曲线 (每职业平均 {trials} 次)")
    print("=" * 60)
    header = "  {:<14}".format("class") + "".join(f"{s.upper():>5}" for s in GROWTH_STATS)
    for profile in TIER1_PROFILES:
        cid = profile["id"]
        t1 = _avg_stats(cid, trials, promote_after=False)
        t2 = _avg_stats(cid, trials, promote_after=True)
        print(f"\n  [{profile['name']}]")
        print(header)
        print("  {:<14}".format("Tier1 @Lv20") + "".join(f"{t1[s]:5.1f}" for s in GROWTH_STATS))
        print("  {:<14}".format("Tier2 @Lv20") + "".join(f"{t2[s]:5.1f}" for s in GROWTH_STATS))
    print()


def main():
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    random.seed(12345)  # deterministic report
    report_triangle(trials)
    report_growth(max(500, trials // 3))


if __name__ == "__main__":
    main()
