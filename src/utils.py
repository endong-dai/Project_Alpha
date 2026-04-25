"""
utils.py
Helper functions.
"""

from combat import damage_amount


def simulate_damage(attacker, defender):
    if not attacker.has_usable_weapon():
        return defender.hp
    return defender.hp - damage_amount(attacker, defender)
