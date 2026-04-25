"""
weapon.py
Defines Weapon class.
"""


def default_weapon_durability(name, weapon_type):
    if "Iron" in name:
        return 40
    if "Steel" in name:
        return 30
    if "Silver" in name:
        return 20
    if "Killer" in name:
        return 20
    if weapon_type in {"fire", "thunder", "earth", "wind"}:
        return 35
    if weapon_type in {"dagger"}:
        return 30
    return 35


class Weapon:
    item_type = "weapon"

    def __init__(
        self,
        name,
        weapon_type,
        damage_kind,
        might,
        attack_range,
        cost=0,
        crit_bonus=0,
        durability=None,
        max_durability=None,
    ):
        self.name = name
        self.weapon_type = weapon_type
        self.damage_kind = damage_kind
        self.might = might
        self.range = attack_range
        self.cost = cost
        self.crit_bonus = crit_bonus
        self.attack = might
        resolved_max = max_durability if max_durability is not None else default_weapon_durability(name, weapon_type)
        self.max_durability = max(1, int(resolved_max))
        resolved_current = self.max_durability if durability is None else int(durability)
        self.durability = max(0, min(self.max_durability, resolved_current))

    def is_usable(self):
        return self.durability > 0

    def consume_use(self):
        if self.durability <= 0:
            return False
        self.durability = max(0, self.durability - 1)
        return True

    def label(self):
        return (
            f"{self.name} ({self.durability}/{self.max_durability}) "
            f"{self.weapon_type.upper()} MT:{self.might} RNG:{self.range} CRT:{self.crit_bonus}"
        )
