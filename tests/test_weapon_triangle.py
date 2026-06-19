"""Weapon triangle: red > green > blue > red, colorless is neutral."""
from combat import (
    damage_amount,
    hit_rate,
    triangle_modifier,
    triangle_relation,
    weapon_color,
)
from constants import TRIANGLE_DAMAGE_BONUS, TRIANGLE_HIT_BONUS
from helpers import make_unit, make_weapon


def test_color_mapping():
    assert weapon_color(make_weapon("sword")) == "red"
    assert weapon_color(make_weapon("fire", damage_kind="magical")) == "red"
    assert weapon_color(make_weapon("axe")) == "green"
    assert weapon_color(make_weapon("wind", damage_kind="magical")) == "green"
    assert weapon_color(make_weapon("lance")) == "blue"
    assert weapon_color(make_weapon("thunder", damage_kind="magical")) == "blue"
    assert weapon_color(make_weapon("dagger")) is None
    assert weapon_color(make_weapon("earth", damage_kind="magical")) is None
    assert weapon_color(None) is None


def test_physical_cycle():
    sword, axe, lance = make_weapon("sword"), make_weapon("axe"), make_weapon("lance")
    assert triangle_relation(sword, axe) == 1      # red beats green
    assert triangle_relation(axe, lance) == 1      # green beats blue
    assert triangle_relation(lance, sword) == 1    # blue beats red
    assert triangle_relation(axe, sword) == -1     # and the reverse
    assert triangle_relation(lance, axe) == -1
    assert triangle_relation(sword, lance) == -1


def test_magic_cycle():
    fire = make_weapon("fire", damage_kind="magical")
    wind = make_weapon("wind", damage_kind="magical")
    thunder = make_weapon("thunder", damage_kind="magical")
    assert triangle_relation(fire, wind) == 1
    assert triangle_relation(wind, thunder) == 1
    assert triangle_relation(thunder, fire) == 1


def test_cross_category_shares_triangle():
    # Unified color system: a red sword still beats a green wind tome.
    assert triangle_relation(make_weapon("sword"), make_weapon("wind", damage_kind="magical")) == 1


def test_neutral_cases():
    assert triangle_relation(make_weapon("sword"), make_weapon("sword")) == 0   # same color
    assert triangle_relation(make_weapon("dagger"), make_weapon("sword")) == 0  # colorless attacker
    assert triangle_relation(make_weapon("sword"), make_weapon("dagger")) == 0  # colorless defender


def test_modifier_values():
    assert triangle_modifier(make_weapon("sword"), make_weapon("axe")) == (
        TRIANGLE_HIT_BONUS,
        TRIANGLE_DAMAGE_BONUS,
    )
    assert triangle_modifier(make_weapon("axe"), make_weapon("sword")) == (
        -TRIANGLE_HIT_BONUS,
        -TRIANGLE_DAMAGE_BONUS,
    )
    assert triangle_modifier(make_weapon("dagger"), make_weapon("sword")) == (0, 0)


def test_hit_rate_reflects_triangle():
    # speed 0 keeps the base 70 away from the 95 cap so the +/-15 is visible.
    attacker_adv = make_unit("A", weapon=make_weapon("sword"))
    defender_axe = make_unit("D", weapon=make_weapon("axe"))
    defender_lance = make_unit("D2", weapon=make_weapon("lance"))
    defender_dagger = make_unit("D3", weapon=make_weapon("dagger"))

    neutral = hit_rate(attacker_adv, defender_dagger)
    advantage = hit_rate(attacker_adv, defender_axe)     # red vs green: +15
    disadvantage = hit_rate(attacker_adv, defender_lance)  # red vs blue: -15
    assert advantage - neutral == TRIANGLE_HIT_BONUS
    assert neutral - disadvantage == TRIANGLE_HIT_BONUS


def test_damage_reflects_triangle():
    attacker = make_unit("A", weapon=make_weapon("sword", might=5), strength=5)
    defender_axe = make_unit("D", weapon=make_weapon("axe"), defense=0)
    defender_dagger = make_unit("D3", weapon=make_weapon("dagger"), defense=0)
    neutral = damage_amount(attacker, defender_dagger)
    advantage = damage_amount(attacker, defender_axe)
    assert advantage - neutral == TRIANGLE_DAMAGE_BONUS
