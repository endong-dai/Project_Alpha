"""
terrain.py
Terrain definitions, rendering, battlefield generation, and effects.
"""

import random

import pygame

TERRAIN_PLAIN = "plain"
TERRAIN_GRASS = "grass"
TERRAIN_FORT = "fort"
TERRAIN_CASTLE = "castle"
TERRAIN_MOUNTAIN = "mountain"
TERRAIN_SHALLOW_WATER = "shallow_water"
TERRAIN_DEEP_WATER = "deep_water"
TERRAIN_SWAMP = "swamp"
TERRAIN_ELECTRIC = "electric"
TERRAIN_TOWN = "town"
TERRAIN_CAPITAL = "capital"
TERRAIN_FOREST = "forest"
TERRAIN_SNOW = "snow"
TERRAIN_ICE = "ice"
TERRAIN_OPEN = "open"
TERRAIN_WIND = "wind"
TERRAIN_RIVER = "river"
TERRAIN_BRIDGE = "bridge"
TERRAIN_FORD = "ford"
TERRAIN_RUINS = "ruins"
TERRAIN_TRENCH = "trench"
TERRAIN_CORRUPTION = "corruption"
TERRAIN_FOG = "fog"
TERRAIN_BOSS_CASTLE = "boss_castle"
TERRAIN_SEAL_FORT = "seal_fort"

TERRAIN_DATA = {
    TERRAIN_PLAIN: {"move_cost": 1, "avoid": 0, "defense": 0, "heal": 0, "hit": 0, "range_bonus": 0, "hp_delta": 0, "blocked": False, "thunder_multiplier": 1.0},
    TERRAIN_GRASS: {"move_cost": 1, "avoid": 0, "defense": 0, "heal": 0, "hit": 0, "range_bonus": 0, "hp_delta": 0, "blocked": False, "thunder_multiplier": 1.0},
    TERRAIN_FORT: {"move_cost": 1, "avoid": 0, "defense": 4, "heal": 0, "hit": 10, "range_bonus": 0, "hp_delta": 0, "blocked": False, "thunder_multiplier": 1.0},
    TERRAIN_CASTLE: {"move_cost": 1, "avoid": 20, "defense": 0, "heal": 3, "hit": 0, "range_bonus": 0, "hp_delta": 0, "blocked": False, "thunder_multiplier": 1.0},
    TERRAIN_MOUNTAIN: {"move_cost": 2, "avoid": 20, "defense": 2, "heal": 0, "hit": 0, "range_bonus": 0, "hp_delta": 0, "blocked": False, "thunder_multiplier": 1.0},
    TERRAIN_SHALLOW_WATER: {"move_cost": 2, "avoid": 10, "defense": 0, "heal": 0, "hit": 0, "range_bonus": 0, "hp_delta": 0, "blocked": False, "thunder_multiplier": 1.0},
    TERRAIN_DEEP_WATER: {"move_cost": 5, "avoid": 0, "defense": 0, "heal": 0, "hit": 0, "range_bonus": 0, "hp_delta": 0, "blocked": True, "thunder_multiplier": 1.0},
    TERRAIN_SWAMP: {"move_cost": 3, "avoid": -10, "defense": 0, "heal": 0, "hit": 0, "range_bonus": 0, "hp_delta": -1, "blocked": False, "thunder_multiplier": 1.0},
    TERRAIN_ELECTRIC: {"move_cost": 2, "avoid": 0, "defense": 0, "heal": 0, "hit": 0, "range_bonus": 0, "hp_delta": 0, "blocked": False, "thunder_multiplier": 1.5},
    TERRAIN_TOWN: {"move_cost": 1, "avoid": 10, "defense": 0, "heal": 2, "hit": 0, "range_bonus": 0, "hp_delta": 0, "blocked": False, "thunder_multiplier": 1.0},
    TERRAIN_CAPITAL: {"move_cost": 1, "avoid": 15, "defense": 0, "heal": 3, "hit": 0, "range_bonus": 0, "hp_delta": 0, "blocked": False, "thunder_multiplier": 1.0},
    TERRAIN_FOREST: {"move_cost": 2, "avoid": 30, "defense": 0, "heal": 0, "hit": 0, "range_bonus": 0, "hp_delta": 0, "blocked": False, "thunder_multiplier": 1.0},
    TERRAIN_SNOW: {"move_cost": 2, "avoid": 0, "defense": 0, "heal": 0, "hit": -10, "range_bonus": 0, "hp_delta": 0, "blocked": False, "thunder_multiplier": 1.0},
    TERRAIN_ICE: {"move_cost": 1, "avoid": -20, "defense": 0, "heal": 0, "hit": 0, "range_bonus": 0, "hp_delta": 0, "blocked": False, "thunder_multiplier": 1.0},
    TERRAIN_OPEN: {"move_cost": 1, "avoid": 0, "defense": 0, "heal": 0, "hit": 10, "range_bonus": 0, "hp_delta": 0, "blocked": False, "thunder_multiplier": 1.0},
    TERRAIN_WIND: {"move_cost": 1, "avoid": 0, "defense": 0, "heal": 0, "hit": 0, "range_bonus": 1, "hp_delta": 0, "blocked": False, "thunder_multiplier": 1.0},
    TERRAIN_RIVER: {"move_cost": 99, "avoid": 0, "defense": 0, "heal": 0, "hit": 0, "range_bonus": 0, "hp_delta": 0, "blocked": True, "thunder_multiplier": 1.0},
    TERRAIN_BRIDGE: {"move_cost": 1, "avoid": 0, "defense": 1, "heal": 0, "hit": 0, "range_bonus": 0, "hp_delta": 0, "blocked": False, "thunder_multiplier": 1.0},
    TERRAIN_FORD: {"move_cost": 2, "avoid": 0, "defense": 0, "heal": 0, "hit": 0, "range_bonus": 0, "hp_delta": 0, "blocked": False, "thunder_multiplier": 1.0},
    TERRAIN_RUINS: {"move_cost": 1, "avoid": 15, "defense": 1, "heal": 0, "hit": 5, "range_bonus": 0, "hp_delta": 0, "blocked": False, "thunder_multiplier": 1.0},
    TERRAIN_TRENCH: {"move_cost": 2, "avoid": 0, "defense": 2, "heal": 0, "hit": 0, "range_bonus": 0, "hp_delta": 0, "blocked": False, "thunder_multiplier": 1.0},
    TERRAIN_CORRUPTION: {"move_cost": 1, "avoid": 0, "defense": 0, "heal": 0, "hit": 0, "range_bonus": 0, "hp_delta": -2, "blocked": False, "thunder_multiplier": 1.0},
    TERRAIN_FOG: {"move_cost": 1, "avoid": 30, "defense": 0, "heal": 0, "hit": -20, "range_bonus": 0, "hp_delta": 0, "blocked": False, "thunder_multiplier": 1.0},
    TERRAIN_BOSS_CASTLE: {"move_cost": 1, "avoid": 0, "defense": 5, "heal": 5, "hit": 0, "range_bonus": 0, "hp_delta": 0, "blocked": False, "thunder_multiplier": 1.0},
    TERRAIN_SEAL_FORT: {"move_cost": 1, "avoid": 0, "defense": 3, "heal": 0, "hit": 0, "range_bonus": 0, "hp_delta": 0, "blocked": False, "thunder_multiplier": 1.0},
}

TERRAIN_COLORS = {
    TERRAIN_GRASS: (112, 180, 93, 124),
    TERRAIN_FORT: (192, 144, 68, 144),
    TERRAIN_CASTLE: (214, 190, 110, 150),
    TERRAIN_MOUNTAIN: (130, 122, 118, 150),
    TERRAIN_SHALLOW_WATER: (102, 168, 213, 132),
    TERRAIN_DEEP_WATER: (44, 104, 168, 160),
    TERRAIN_SWAMP: (106, 122, 86, 140),
    TERRAIN_ELECTRIC: (236, 224, 94, 150),
    TERRAIN_TOWN: (194, 153, 98, 136),
    TERRAIN_CAPITAL: (214, 177, 102, 150),
    TERRAIN_FOREST: (74, 141, 82, 150),
    TERRAIN_SNOW: (228, 235, 241, 150),
    TERRAIN_ICE: (176, 223, 244, 150),
    TERRAIN_OPEN: (220, 208, 159, 110),
    TERRAIN_WIND: (186, 214, 228, 118),
    TERRAIN_RIVER: (60, 113, 176, 150),
    TERRAIN_BRIDGE: (133, 101, 73, 150),
    TERRAIN_FORD: (117, 158, 194, 124),
    TERRAIN_RUINS: (168, 145, 124, 136),
    TERRAIN_TRENCH: (127, 96, 70, 130),
    TERRAIN_CORRUPTION: (124, 72, 136, 150),
    TERRAIN_FOG: (192, 194, 205, 108),
    TERRAIN_BOSS_CASTLE: (158, 86, 122, 150),
    TERRAIN_SEAL_FORT: (136, 106, 180, 145),
}

FACTION_TERRAIN_PATTERNS = {
    "qin": [
        (TERRAIN_MOUNTAIN, 1, 2), (TERRAIN_MOUNTAIN, 1, 3), (TERRAIN_MOUNTAIN, 2, 3),
        (TERRAIN_MOUNTAIN, 3, 4), (TERRAIN_MOUNTAIN, 5, 4), (TERRAIN_MOUNTAIN, 6, 5),
        (TERRAIN_FORT, 2, 6), (TERRAIN_FORT, 5, 2), (TERRAIN_CASTLE, 4, 5),
    ],
    "chu": [
        (TERRAIN_SHALLOW_WATER, 1, 2), (TERRAIN_SHALLOW_WATER, 1, 3), (TERRAIN_DEEP_WATER, 2, 3),
        (TERRAIN_DEEP_WATER, 3, 3), (TERRAIN_SHALLOW_WATER, 4, 4), (TERRAIN_SWAMP, 5, 5),
        (TERRAIN_SWAMP, 6, 6), (TERRAIN_ELECTRIC, 4, 6), (TERRAIN_ELECTRIC, 6, 4),
    ],
    "qi": [
        (TERRAIN_TOWN, 2, 2), (TERRAIN_TOWN, 2, 6), (TERRAIN_TOWN, 5, 3),
        (TERRAIN_CAPITAL, 4, 4), (TERRAIN_OPEN, 6, 6), (TERRAIN_OPEN, 3, 5),
    ],
    "yan": [
        (TERRAIN_FOREST, 1, 2), (TERRAIN_FOREST, 2, 3), (TERRAIN_FOREST, 5, 5),
        (TERRAIN_FOREST, 6, 2), (TERRAIN_SNOW, 2, 6), (TERRAIN_SNOW, 3, 6),
        (TERRAIN_ICE, 4, 4), (TERRAIN_ICE, 6, 6),
    ],
    "zhao": [
        (TERRAIN_GRASS, 1, 3), (TERRAIN_GRASS, 2, 3), (TERRAIN_GRASS, 3, 4),
        (TERRAIN_OPEN, 4, 5), (TERRAIN_OPEN, 6, 5), (TERRAIN_WIND, 3, 6), (TERRAIN_WIND, 5, 2),
    ],
    "wei": [
        (TERRAIN_RIVER, 1, 4), (TERRAIN_RIVER, 2, 4), (TERRAIN_RIVER, 4, 4),
        (TERRAIN_RIVER, 5, 4), (TERRAIN_RIVER, 7, 4),
        (TERRAIN_BRIDGE, 3, 4), (TERRAIN_BRIDGE, 6, 4), (TERRAIN_FORD, 4, 5),
    ],
    "han": [
        (TERRAIN_RUINS, 2, 2), (TERRAIN_RUINS, 2, 6), (TERRAIN_RUINS, 5, 5),
        (TERRAIN_TRENCH, 3, 3), (TERRAIN_TRENCH, 3, 4), (TERRAIN_TRENCH, 3, 5),
        (TERRAIN_TRENCH, 6, 3), (TERRAIN_TRENCH, 6, 4), (TERRAIN_TRENCH, 6, 5),
    ],
    "luo": [
        (TERRAIN_CORRUPTION, 2, 2), (TERRAIN_CORRUPTION, 2, 6), (TERRAIN_CORRUPTION, 6, 2),
        (TERRAIN_CORRUPTION, 6, 6), (TERRAIN_FOG, 3, 3), (TERRAIN_FOG, 3, 5),
        (TERRAIN_FOG, 5, 3), (TERRAIN_FOG, 5, 5), (TERRAIN_SEAL_FORT, 2, 4),
        (TERRAIN_SEAL_FORT, 4, 2), (TERRAIN_SEAL_FORT, 4, 6), (TERRAIN_SEAL_FORT, 6, 4),
        (TERRAIN_BOSS_CASTLE, 4, 4),
    ],
}


def get_terrain_at(tile_x, tile_y, terrain_map):
    if terrain_map is None:
        return TERRAIN_PLAIN
    return terrain_map[tile_x][tile_y]


def get_terrain_data(terrain_type):
    return TERRAIN_DATA.get(terrain_type, TERRAIN_DATA[TERRAIN_PLAIN])


def get_terrain_avoid_bonus(terrain_type):
    return get_terrain_data(terrain_type)["avoid"]


def get_terrain_def_bonus(terrain_type):
    return get_terrain_data(terrain_type)["defense"]


def get_terrain_hit_bonus(terrain_type):
    return get_terrain_data(terrain_type)["hit"]


def get_terrain_range_bonus(terrain_type):
    return get_terrain_data(terrain_type)["range_bonus"]


def get_terrain_move_cost(unit, terrain_type):
    return get_terrain_data(terrain_type)["move_cost"]


def is_terrain_blocked(unit, terrain_type):
    return get_terrain_data(terrain_type)["blocked"]


def get_thunder_damage_multiplier(terrain_type):
    return get_terrain_data(terrain_type)["thunder_multiplier"]


def apply_end_turn_terrain_effect(unit, terrain_type):
    if not unit or not unit.is_alive():
        return 0

    terrain_data = get_terrain_data(terrain_type)
    hp_delta = terrain_data["hp_delta"]
    heal_amount = terrain_data["heal"]

    total_delta = 0
    if hp_delta < 0:
        old_hp = unit.hp
        unit.hp = max(0, unit.hp + hp_delta)
        total_delta += unit.hp - old_hp

    if heal_amount > 0:
        old_hp = unit.hp
        unit.hp = min(unit.max_hp, unit.hp + heal_amount)
        total_delta += unit.hp - old_hp

    return total_delta


def _create_overlay(cell_size, terrain_type, color):
    surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
    surface.fill(color)

    if terrain_type in {TERRAIN_MOUNTAIN, TERRAIN_RUINS}:
        pygame.draw.polygon(surface, (70, 70, 70, 170), [(6, cell_size - 6), (cell_size // 2, 8), (cell_size - 6, cell_size - 6)])
    elif terrain_type in {TERRAIN_SHALLOW_WATER, TERRAIN_DEEP_WATER, TERRAIN_RIVER, TERRAIN_FORD}:
        for y in range(6, cell_size, 10):
            pygame.draw.line(surface, (230, 245, 255, 90), (4, y), (cell_size - 4, y + 2), 2)
    elif terrain_type in {TERRAIN_FOREST, TERRAIN_GRASS}:
        for x in range(8, cell_size, 12):
            pygame.draw.circle(surface, (34, 86, 34, 140), (x, min(cell_size - 8, x)), 4)
    elif terrain_type in {TERRAIN_FORT, TERRAIN_CASTLE, TERRAIN_BOSS_CASTLE, TERRAIN_SEAL_FORT, TERRAIN_CAPITAL, TERRAIN_TOWN}:
        inner = pygame.Rect(6, 6, cell_size - 12, cell_size - 12)
        pygame.draw.rect(surface, (245, 232, 198, 120), inner, border_radius=4)
        pygame.draw.rect(surface, (120, 80, 42, 180), inner, 2, border_radius=4)
    elif terrain_type == TERRAIN_ELECTRIC:
        pygame.draw.line(surface, (255, 240, 102, 200), (8, 6), (cell_size // 2, cell_size - 10), 3)
        pygame.draw.line(surface, (255, 240, 102, 200), (cell_size // 2, cell_size - 10), (cell_size - 8, 12), 3)
    elif terrain_type in {TERRAIN_SNOW, TERRAIN_ICE, TERRAIN_FOG}:
        for x in range(6, cell_size, 10):
            for y in range(6, cell_size, 10):
                pygame.draw.circle(surface, (255, 255, 255, 100), (x, y), 2)
    elif terrain_type in {TERRAIN_SWAMP, TERRAIN_CORRUPTION}:
        for x in range(4, cell_size, 8):
            pygame.draw.circle(surface, (52, 28, 58, 140), (x, (x * 3) % max(1, cell_size - 8) + 4), 3)
    elif terrain_type in {TERRAIN_TRENCH, TERRAIN_BRIDGE, TERRAIN_OPEN, TERRAIN_WIND}:
        pygame.draw.line(surface, (84, 60, 46, 160), (6, cell_size // 2), (cell_size - 6, cell_size // 2), 4)

    return surface


def build_terrain_overlays(cell_size):
    return {
        terrain_type: _create_overlay(cell_size, terrain_type, color)
        for terrain_type, color in TERRAIN_COLORS.items()
    }


def draw_terrain_tile(screen, overlays, terrain_type, dest):
    overlay = overlays.get(terrain_type)
    if overlay:
        screen.blit(overlay, dest)


def _transform_pattern(pattern, variant):
    transformed = []
    for terrain_type, row, col in pattern:
        if variant == 1:
            row, col = col, 9 - row
        elif variant == 2:
            row, col = 9 - row, 9 - col
        elif variant == 3:
            row, col = 9 - col, row
        transformed.append((terrain_type, row, col))
    return transformed


def generate_faction_battlefield(faction_id, seed_key, size=10):
    pattern = FACTION_TERRAIN_PATTERNS.get(faction_id, FACTION_TERRAIN_PATTERNS["han"])
    variant = random.Random(str(seed_key)).randint(0, 3)
    transformed = _transform_pattern(pattern, variant)
    return [
        (terrain_type, row, col)
        for terrain_type, row, col in transformed
        if 0 <= row < size and 0 <= col < size
    ]
