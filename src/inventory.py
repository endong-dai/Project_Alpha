"""
inventory.py
Inventory item definitions.
"""


class Potion:
    item_type = "potion"

    def __init__(self, name, heal_amount):
        self.name = name
        self.heal_amount = heal_amount

    def label(self):
        return f"{self.name} HEAL:{self.heal_amount}"


class Antidote:
    item_type = "antidote"

    def __init__(self, name):
        self.name = name

    def label(self):
        return f"{self.name} CURE"


def item_label(item):
    if hasattr(item, "label"):
        return item.label()
    return getattr(item, "name", "Item")
