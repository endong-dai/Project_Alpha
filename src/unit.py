"""
unit.py
Defines the Unit class representing a character.
"""


class Unit:
    def __init__(
        self,
        name,
        strength,
        defense,
        speed,
        move,
        weapon,
        inventory=None,
        max_hp=20,
        sprite_key=None,
    ):
        self.name = name
        self.strength = strength
        self.defense = defense
        self.speed = speed
        self.move = move
        self.weapon = weapon
        self.inventory = list(inventory) if inventory else []
        if weapon and weapon not in self.inventory:
            self.inventory.insert(0, weapon)
        if self.weapon is None:
            self.weapon = self._find_first_weapon()

        self.max_hp = max_hp
        self.hp = self.max_hp
        self.sprite_key = sprite_key
        self.game_map = None
        self.x = None
        self.y = None
        self.has_moved = False
        self.has_acted = False

    def _find_first_weapon(self):
        for item in self.inventory:
            if getattr(item, "item_type", None) == "weapon":
                return item
        return None

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
        if weapon in self.inventory and getattr(weapon, "item_type", None) == "weapon":
            self.weapon = weapon
            return True
        return False

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
        weapon_attack = self.weapon.attack if self.weapon else 0
        return self.strength + weapon_attack
