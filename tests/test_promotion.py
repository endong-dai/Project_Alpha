"""Promotion + level-cap rules."""
from constants import PROMOTION_MIN_LEVEL, TIER1_MAX_LEVEL
from helpers import make_unit, make_weapon
from progression import can_promote, gain_exp, is_at_max_level, promote
from unit_classes import get_promotion_bonuses


def _sword_unit(level=1):
    return make_unit("S", weapon=make_weapon("sword"), class_id="sword_fighter", level=level)


def test_cannot_promote_below_min_level():
    assert can_promote(_sword_unit(level=PROMOTION_MIN_LEVEL - 1)) is False


def test_can_promote_at_min_level():
    assert can_promote(_sword_unit(level=PROMOTION_MIN_LEVEL)) is True


def test_promote_changes_class_and_resets_level():
    unit = _sword_unit(level=12)
    base_hp = unit.max_hp
    result = promote(unit)
    assert result is not None
    assert unit.class_id == "swordmaster"
    assert unit.unit_class == "Swordmaster"
    assert unit.level == 1
    assert unit.exp == 0
    assert unit.allowed_weapon_types == ("sword",)
    bonuses = get_promotion_bonuses("swordmaster")
    assert unit.max_hp == base_hp + bonuses["max_hp"]


def test_tier2_cannot_promote_again():
    unit = _sword_unit(level=12)
    promote(unit)
    assert can_promote(unit) is False
    assert promote(unit) is None


def test_level_cap_blocks_further_levels():
    unit = _sword_unit(level=TIER1_MAX_LEVEL)
    assert is_at_max_level(unit)
    assert gain_exp(unit, 500) == []
    assert unit.level == TIER1_MAX_LEVEL
    assert unit.exp == 0


def test_gain_exp_stops_at_cap():
    unit = _sword_unit(level=TIER1_MAX_LEVEL - 1)
    gain_exp(unit, 100000)
    assert unit.level == TIER1_MAX_LEVEL
    assert unit.exp == 0
