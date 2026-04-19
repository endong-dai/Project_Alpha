"""
movement.py
Movement logic.
"""


def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def get_reachable_tiles(unit, game_map, include_origin=False):
    ux, uy = unit.get_position()
    cells = []

    for x in range(game_map.size):
        for y in range(game_map.size):
            distance = abs(x - ux) + abs(y - uy)
            if distance > unit.move:
                continue
            if distance == 0:
                if include_origin:
                    cells.append((x, y))
                continue
            if game_map.is_empty(x, y):
                cells.append((x, y))

    return cells


def can_move(unit, x, y, game_map):
    ux, uy = unit.get_position()
    if abs(x - ux) + abs(y - uy) > unit.move:
        return False
    if not game_map.in_bounds(x, y):
        return False
    if not game_map.is_empty(x, y):
        return False
    return True
