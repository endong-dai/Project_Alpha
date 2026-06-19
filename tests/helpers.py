"""Small factories for building units/weapons in tests without pygame."""
from unit import Unit
from weapon import Weapon


def make_weapon(weapon_type, might=5, damage_kind="physical", crit_bonus=0, attack_range=1, name=None):
    name = name or f"Test {weapon_type}"
    return Weapon(name, weapon_type, damage_kind, might, attack_range, crit_bonus=crit_bonus)


def make_unit(
    name="U",
    weapon=None,
    allowed=None,
    strength=5,
    magic=5,
    defense=0,
    resistance=0,
    speed=0,
    move=5,
    crit=0,
    max_hp=20,
    class_id="sword_fighter",
    level=1,
):
    if allowed is None:
        allowed = [weapon.weapon_type] if weapon else ["sword"]
    return Unit(
        name,
        strength,
        magic,
        defense,
        resistance,
        speed,
        move,
        weapon,
        "Test",
        allowed,
        max_hp=max_hp,
        class_id=class_id,
        crit=crit,
        level=level,
    )
