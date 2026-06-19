"""Sanity checks for the unchanged combat/movement cores (regression net)."""
from combat import can_follow_up, get_combat_sequence, hit_rate
from constants import HIT_RATE_MAX, HIT_RATE_MIN
from helpers import make_unit, make_weapon
from map import Map
from movement import get_reachable_tiles, manhattan_distance


def test_hit_rate_clamped():
    fast = make_unit("F", weapon=make_weapon("sword"), speed=99)
    slow = make_unit("S", weapon=make_weapon("dagger"), speed=0)
    assert hit_rate(fast, slow) == HIT_RATE_MAX
    evasive = make_unit("E", weapon=make_weapon("dagger"), speed=99)
    weak = make_unit("W", weapon=make_weapon("dagger"), speed=0)
    assert hit_rate(weak, evasive) == HIT_RATE_MIN


def test_follow_up_requires_speed_gap():
    fast = make_unit("F", weapon=make_weapon("sword"), speed=10)
    slow = make_unit("S", weapon=make_weapon("sword"), speed=3)
    assert can_follow_up(fast, slow) is True
    assert can_follow_up(slow, fast) is False


def test_combat_sequence_has_attacker_first():
    a = make_unit("A", weapon=make_weapon("sword"), speed=10)
    b = make_unit("B", weapon=make_weapon("sword"), speed=3)
    a.set_position(0, 0)
    b.set_position(0, 1)
    seq = get_combat_sequence(a, b)
    assert seq[0][0] is a


def test_reachable_tiles_on_empty_map():
    game_map = Map(size=10)
    unit = make_unit("U", weapon=make_weapon("sword"), move=3)
    game_map.place_unit(unit, 5, 5)
    reachable = get_reachable_tiles(unit, game_map)
    assert (5, 5) not in reachable          # origin excluded by default
    assert (5, 8) in reachable              # 3 tiles away, all plains
    for tile in reachable:
        assert manhattan_distance((5, 5), tile) <= 3
