"""
utils.py
Helper functions.
"""

from combat import defense_amount


def simulate_damage(attacker, defender):
    return defender.hp - max(0, attacker.get_attack() - defense_amount(defender))
