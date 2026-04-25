"""
movement.py
Movement logic with terrain costs.
"""

import heapq

from terrain import get_terrain_move_cost, is_terrain_blocked


def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _get_move_budget(unit, origin, game_map):
    ox, oy = origin
    terrain_type = game_map.get_terrain(ox, oy)
    terrain_bonus = 0
    if terrain_type == "grass" and getattr(unit, "class_id", None) == "lancer":
        terrain_bonus = 1
    return unit.move + terrain_bonus


def get_reachable_tiles_from_position(unit, game_map, origin, include_origin=False):
    budget = _get_move_budget(unit, origin, game_map)
    frontier = [(0, origin)]
    costs = {origin: 0}

    while frontier:
        cost, (row, col) = heapq.heappop(frontier)
        if cost > costs[(row, col)]:
            continue

        for delta_row, delta_col in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            next_row = row + delta_row
            next_col = col + delta_col
            if not game_map.in_bounds(next_row, next_col):
                continue

            occupant = game_map.get_unit(next_row, next_col)
            if occupant is not None and (next_row, next_col) != origin:
                continue

            terrain_type = game_map.get_terrain(next_row, next_col)
            if is_terrain_blocked(unit, terrain_type):
                continue

            next_cost = cost + get_terrain_move_cost(unit, terrain_type)
            if next_cost > budget:
                continue

            if next_cost < costs.get((next_row, next_col), budget + 1):
                costs[(next_row, next_col)] = next_cost
                heapq.heappush(frontier, (next_cost, (next_row, next_col)))

    reachable = []
    for tile in sorted(costs, key=lambda tile: (tile[0], tile[1])):
        if tile == origin and not include_origin:
            continue
        if tile != origin and game_map.is_empty(tile[0], tile[1]):
            reachable.append(tile)
        elif tile == origin and include_origin:
            reachable.append(tile)
    return reachable


def get_reachable_tiles(unit, game_map, include_origin=False):
    return get_reachable_tiles_from_position(unit, game_map, unit.get_position(), include_origin)


def get_move_tiles(unit, game_map, units=None, origin=None, include_origin=False):
    del units
    move_origin = origin if origin is not None else unit.get_position()
    return set(
        get_reachable_tiles_from_position(
            unit,
            game_map,
            move_origin,
            include_origin=include_origin,
        )
    )


def can_move(unit, x, y, game_map):
    if not game_map.in_bounds(x, y):
        return False
    if not game_map.is_empty(x, y):
        return False
    return (x, y) in get_reachable_tiles(unit, game_map, include_origin=False)


def find_shortest_move_path(unit, game_map, origin, destination):
    if origin == destination:
        return [origin]

    budget = _get_move_budget(unit, origin, game_map)
    frontier = [(0, origin)]
    costs = {origin: 0}
    parents = {origin: None}

    while frontier:
        cost, (row, col) = heapq.heappop(frontier)
        if cost > costs[(row, col)]:
            continue
        if (row, col) == destination:
            break

        for delta_row, delta_col in ((-1, 0), (0, -1), (0, 1), (1, 0)):
            next_row = row + delta_row
            next_col = col + delta_col
            next_tile = (next_row, next_col)
            if not game_map.in_bounds(next_row, next_col):
                continue

            occupant = game_map.get_unit(next_row, next_col)
            if occupant is not None and next_tile not in {origin, destination}:
                continue
            if next_tile == destination and occupant is not None and next_tile != origin:
                continue

            terrain_type = game_map.get_terrain(next_row, next_col)
            if is_terrain_blocked(unit, terrain_type):
                continue

            next_cost = cost + get_terrain_move_cost(unit, terrain_type)
            if next_cost > budget:
                continue

            if next_cost < costs.get(next_tile, budget + 1):
                costs[next_tile] = next_cost
                parents[next_tile] = (row, col)
                heapq.heappush(frontier, (next_cost, next_tile))

    if destination not in parents:
        return []

    path = []
    current = destination
    while current is not None:
        path.append(current)
        current = parents[current]
    path.reverse()
    return path
