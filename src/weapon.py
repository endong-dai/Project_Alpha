"""
weapon.py
Defines Weapon class.
"""


class Weapon:
    item_type = "weapon"

    def __init__(self, name, attack, attack_range):
        self.name = name
        self.attack = attack
        self.range = attack_range

    def label(self):
        return f"{self.name} ATK:{self.attack} RNG:{self.range}"
