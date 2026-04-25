"""
ai.py
Enemy AI.
"""
from combat import effective_attack_range, in_range, combat
from movement import get_reachable_tiles, manhattan_distance
from utils import simulate_damage


def choose_target(enemy, players):
    alive = [p for p in players if p.is_alive()]
    best = None
    best_score = None
    for p in alive:
        score = (p.hp, simulate_damage(enemy, p), manhattan_distance(enemy.get_position(), p.get_position()))
        if best_score is None or score < best_score:
            best_score = score
            best = p
    return best


def choose_destination(enemy, target, game_map):
    reachable = get_reachable_tiles(enemy, game_map, include_origin=True)
    current = enemy.get_position()
    target_pos = target.get_position()

    attack_positions = [
        tile
        for tile in reachable
        if manhattan_distance(tile, target_pos) <= effective_attack_range(enemy)
    ]

    if attack_positions:
        return min(
            attack_positions,
            key=lambda tile: (
                manhattan_distance(tile, current),
                manhattan_distance(tile, target_pos),
            ),
        )

    return min(
        reachable,
        key=lambda tile: (
            manhattan_distance(tile, target_pos),
            manhattan_distance(tile, current),
        ),
    )


def enemy_action(enemy, players, game_map):
    log = {"attacks": [], "events": []}
    if not enemy.is_alive():
        return log

    target = choose_target(enemy, players)
    if not target:
        return log

    destination = choose_destination(enemy, target, game_map)
    if destination != enemy.get_position():
        game_map.move_unit(enemy, destination[0], destination[1])
        enemy.has_moved = True

    if in_range(enemy, target):
        log = combat(enemy, target)

    enemy.has_acted = True
    return log
