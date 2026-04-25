"""
unit.py
Defines the Unit class representing a character.
"""


class Unit:
    def __init__(
        self,
        name,
        strength,
        magic,
        defense,
        resistance,
        speed,
        move,
        weapon,
        unit_class,
        allowed_weapon_types,
        inventory=None,
        max_hp=20,
        sprite_key=None,
        class_id=None,
        unit_id=None,
        level=1,
        exp=0,
        crit=0,
        current_hp=None,
        persistent=False,
    ):
        self.name = name
        self.strength = strength
        self.magic = magic
        self.defense = defense
        self.resistance = resistance
        self.speed = speed
        self.move = move
        self.class_id = class_id
        self.unit_class = unit_class
        self.unit_id = unit_id
        self.level = level
        self.exp = exp
        self.crit = crit
        self.persistent = persistent
        self.allowed_weapon_types = tuple(allowed_weapon_types)
        self.weapon = weapon if self._can_use_weapon(weapon) else None
        self.inventory = list(inventory) if inventory else []
        if weapon and weapon not in self.inventory:
            self.inventory.insert(0, weapon)
        if self.weapon is None:
            self.weapon = self._find_first_weapon()

        self.max_hp = max_hp
        self.hp = self.max_hp if current_hp is None else max(0, min(self.max_hp, current_hp))
        self.sprite_key = sprite_key
        self.game_map = None
        self.x = None
        self.y = None
        self.has_moved = False
        self.has_acted = False

    def _find_first_weapon(self):
        for item in self.inventory:
            if self._can_use_weapon(item):
                return item
        return None

    def _can_use_weapon(self, weapon):
        return (
            getattr(weapon, "item_type", None) == "weapon"
            and getattr(weapon, "durability", 0) > 0
            and weapon.weapon_type in self.allowed_weapon_types
        )

    def get_position(self):
        return self.x, self.y

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def is_alive(self):
        return self.hp > 0

    def can_take_turn(self):
        return self.is_alive() and not self.has_acted

    def reset_turn(self):
        self.has_moved = False
        self.has_acted = False

    def equip_weapon(self, weapon):
        if weapon in self.inventory and self._can_use_weapon(weapon):
            self.weapon = weapon
            return True
        return False

    def can_equip_weapon(self, weapon):
        return self._can_use_weapon(weapon)

    def has_usable_weapon(self):
        return self._can_use_weapon(self.weapon)

    def heal(self, amount):
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp

    def remove_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
            if item is self.weapon:
                self.weapon = self._find_first_weapon()
            return True
        return False

    def get_attack(self):
        if not self.weapon:
            return 0
        if self.weapon.damage_kind == "magical":
            return self.magic + self.weapon.might
        return self.strength + self.weapon.might
