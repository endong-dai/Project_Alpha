"""
shop.py
Shared shop catalog and item factory helpers.
"""

from inventory import Antidote, Potion
from unit_classes import get_weapon_spec
from weapon import Weapon

STARTING_GOLD = 500
DEFAULT_STOCK = 9

SHOP_ITEMS = [
    {"id": "iron_sword", "name": "Iron Sword", "kind": "weapon", "price": 120},
    {"id": "steel_sword", "name": "Steel Sword", "kind": "weapon", "price": 170},
    {"id": "silver_sword", "name": "Silver Sword", "kind": "weapon", "price": 260},
    {"id": "killer_sword", "name": "Killer Sword", "kind": "weapon", "price": 220},
    {"id": "iron_lance", "name": "Iron Lance", "kind": "weapon", "price": 130},
    {"id": "steel_lance", "name": "Steel Lance", "kind": "weapon", "price": 180},
    {"id": "silver_lance", "name": "Silver Lance", "kind": "weapon", "price": 270},
    {"id": "killer_lance", "name": "Killer Lance", "kind": "weapon", "price": 225},
    {"id": "iron_axe", "name": "Iron Axe", "kind": "weapon", "price": 140},
    {"id": "steel_axe", "name": "Steel Axe", "kind": "weapon", "price": 190},
    {"id": "silver_axe", "name": "Silver Axe", "kind": "weapon", "price": 280},
    {"id": "killer_axe", "name": "Killer Axe", "kind": "weapon", "price": 235},
    {"id": "iron_dagger", "name": "Iron Dagger", "kind": "weapon", "price": 115},
    {"id": "killer_dagger", "name": "Killer Dagger", "kind": "weapon", "price": 210},
    {"id": "fire_tome", "name": "Fire Tome", "kind": "weapon", "price": 160},
    {"id": "thunder_tome", "name": "Thunder Tome", "kind": "weapon", "price": 170},
    {"id": "earth_tome", "name": "Earth Tome", "kind": "weapon", "price": 160},
    {"id": "wind_tome", "name": "Wind Tome", "kind": "weapon", "price": 150},
    {
        "id": "vulnerary",
        "name": "Vulnerary",
        "kind": "potion",
        "price": 80,
        "heal_amount": 6,
    },
    {
        "id": "heal_potion",
        "name": "Heal Potion",
        "kind": "potion",
        "price": 100,
        "heal_amount": 8,
    },
    {
        "id": "antidote",
        "name": "Antidote",
        "kind": "antidote",
        "price": 60,
    },
]

SHOP_LOOKUP = {item["id"]: item for item in SHOP_ITEMS}


def create_shop_stock():
    return {item["id"]: DEFAULT_STOCK for item in SHOP_ITEMS}


def get_item(item_id):
    return SHOP_LOOKUP[item_id]


def create_item(item_id):
    item = get_item(item_id)
    if item["kind"] == "weapon":
        weapon = get_weapon_spec(item_id)
        return Weapon(
            weapon["name"],
            weapon["weapon_type"],
            weapon["damage_kind"],
            weapon["might"],
            weapon["range"],
            cost=weapon["cost"],
            crit_bonus=weapon.get("crit_bonus", 0),
            max_durability=weapon.get("max_durability"),
        )
    if item["kind"] == "potion":
        return Potion(item["name"], item["heal_amount"])
    return Antidote(item["name"])


def stock_label(item_id, stock):
    item = get_item(item_id)
    if item["kind"] == "weapon":
        weapon = get_weapon_spec(item_id)
        return f"{item['name']} {item['price']}G CRT:{weapon.get('crit_bonus', 0)} S:{stock}"
    return f"{item['name']} {item['price']}G Stock:{stock}"
