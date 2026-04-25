"""
world_map.py
Deterministic 10x10 sandbox conquest grid data.
"""

from collections import deque
import copy
import random

GRID_ROWS = 10
GRID_COLS = 10
GRID_SIZE = 10
DEFAULT_MAP_SEED = 41721
DEFAULT_EMPTY_REWARD = 500

TILE_CITY = "city"
TILE_EMPTY = "empty"
TILE_BLOCKED = "blocked"

FACTIONS = [
    {"id": "qin", "name": "Qin", "color": (172, 92, 82), "playable": True},
    {"id": "zhao", "name": "Zhao", "color": (123, 139, 204), "playable": True},
    {"id": "wei", "name": "Wei", "color": (106, 114, 171), "playable": True},
    {"id": "han", "name": "Han", "color": (172, 153, 92), "playable": True},
    {"id": "qi", "name": "Qi", "color": (100, 163, 164), "playable": True},
    {"id": "yan", "name": "Yan", "color": (166, 190, 222), "playable": True},
    {"id": "chu", "name": "Chu", "color": (110, 168, 99), "playable": True},
    {"id": "luo", "name": "Luo", "color": (118, 72, 135), "playable": False},
]

FACTION_LOOKUP = {faction["id"]: faction for faction in FACTIONS}
PLAYABLE_FACTIONS = [faction for faction in FACTIONS if faction["playable"]]
FACTION_IDS = [faction["id"] for faction in FACTIONS]

CITY_TARGETS = {
    "qin": 9,
    "zhao": 9,
    "wei": 9,
    "han": 9,
    "qi": 9,
    "yan": 9,
    "chu": 9,
    "luo": 7,
}

SEED_POSITIONS = {
    "qin": (1, 1),
    "zhao": (1, 4),
    "wei": (1, 7),
    "han": (4, 1),
    "luo": (4, 4),
    "qi": (4, 8),
    "yan": (7, 2),
    "chu": (7, 7),
}


def make_tile_id(row, col):
    return f"r{row}c{col}"


def in_bounds(row, col):
    return 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS


def get_grid_neighbors(row, col):
    neighbors = []
    for delta_row, delta_col in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        next_row = row + delta_row
        next_col = col + delta_col
        if in_bounds(next_row, next_col):
            neighbors.append((next_row, next_col))
    return neighbors


def _distance_to_any(coord, owned_coords):
    row, col = coord
    return min(abs(row - other_row) + abs(col - other_col) for other_row, other_col in owned_coords)


def _choose_frontier_tile(rng, owned_coords, assigned_coords):
    frontier = []
    for row, col in sorted(owned_coords):
        for next_coord in get_grid_neighbors(row, col):
            if next_coord not in assigned_coords:
                frontier.append(next_coord)

    if frontier:
        unique_frontier = sorted(set(frontier))
        min_distance = min(_distance_to_any(coord, owned_coords) for coord in unique_frontier)
        closest = [coord for coord in unique_frontier if _distance_to_any(coord, owned_coords) == min_distance]
        return rng.choice(closest)

    remaining = [
        (row, col)
        for row in range(GRID_ROWS)
        for col in range(GRID_COLS)
        if (row, col) not in assigned_coords
    ]
    if not remaining:
        return None
    min_distance = min(_distance_to_any(coord, owned_coords) for coord in remaining)
    closest = [coord for coord in remaining if _distance_to_any(coord, owned_coords) == min_distance]
    return rng.choice(sorted(closest))


def generate_grid_map(seed=DEFAULT_MAP_SEED):
    rng = random.Random(seed)
    assigned = {faction_id: [seed_coord] for faction_id, seed_coord in SEED_POSITIONS.items()}
    assigned_coords = set(SEED_POSITIONS.values())

    growing = True
    while growing:
        growing = False
        for faction_id in FACTION_IDS:
            if len(assigned[faction_id]) >= CITY_TARGETS[faction_id]:
                continue
            next_coord = _choose_frontier_tile(rng, assigned[faction_id], assigned_coords)
            if next_coord is None:
                continue
            assigned[faction_id].append(next_coord)
            assigned_coords.add(next_coord)
            growing = True

    city_owner_lookup = {}
    for faction_id, coords in assigned.items():
        for coord in coords:
            city_owner_lookup[coord] = faction_id

    faction_name_counters = {faction_id: 1 for faction_id in FACTION_IDS}
    grid_map = []
    tile_dictionary = {}
    adjacency_graph = {}
    faction_ownership = {faction_id: [] for faction_id in FACTION_IDS}

    for row in range(GRID_ROWS):
        grid_row = []
        for col in range(GRID_COLS):
            coord = (row, col)
            tile_id = make_tile_id(row, col)
            owner = city_owner_lookup.get(coord)
            tile_type = TILE_CITY if owner is not None else TILE_EMPTY
            if tile_type == TILE_CITY:
                name = f"{FACTION_LOOKUP[owner]['name']}{faction_name_counters[owner]}"
                faction_name_counters[owner] += 1
            else:
                name = "Open"

            neighbors = [make_tile_id(next_row, next_col) for next_row, next_col in get_grid_neighbors(row, col)]
            tile = {
                "id": tile_id,
                "grid": coord,
                "type": tile_type,
                "owner_faction": owner,
                "name": name,
                "reward": DEFAULT_EMPTY_REWARD if tile_type == TILE_EMPTY else DEFAULT_EMPTY_REWARD,
                "neighbors": neighbors,
                "coord": f"{row + 1},{col + 1}",
            }
            grid_row.append(tile)
            tile_dictionary[tile_id] = tile
            adjacency_graph[tile_id] = list(neighbors)
            if owner is not None:
                faction_ownership[owner].append(tile_id)
        grid_map.append(grid_row)

    center_targets = [(4, 4), (4, 5), (5, 4), (5, 5)]
    central_expansion_score = {}
    for tile_id, tile in tile_dictionary.items():
        row, col = tile["grid"]
        central_expansion_score[tile_id] = min(
            abs(row - center_row) + abs(col - center_col)
            for center_row, center_col in center_targets
        )

    return {
        "grid_map": grid_map,
        "tile_dictionary": tile_dictionary,
        "adjacency_graph": adjacency_graph,
        "faction_ownership": faction_ownership,
        "central_expansion_score": central_expansion_score,
    }


def clone_grid_map_template():
    return copy.deepcopy(GRID_MAP_TEMPLATE)


def build_empty_grid_lookup():
    return {
        tile["id"]: copy.deepcopy(tile)
        for row in GRID_MAP_TEMPLATE
        for tile in row
    }


_GENERATED = generate_grid_map()
GRID_MAP_TEMPLATE = _GENERATED["grid_map"]
TILE_DICTIONARY = _GENERATED["tile_dictionary"]
ADJACENCY_GRAPH = _GENERATED["adjacency_graph"]
FACTION_OWNERSHIP = _GENERATED["faction_ownership"]
CENTRAL_EXPANSION_SCORE = _GENERATED["central_expansion_score"]
TILE_TEMPLATES = [tile for row in GRID_MAP_TEMPLATE for tile in row]
TILE_ID_ORDER = [tile["id"] for tile in TILE_TEMPLATES]
