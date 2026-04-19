"""
terrain.py
Terrain definitions, rendering, and effects.
"""

import pygame

TERRAIN_PLAIN = "plain"
TERRAIN_GRASS = "grass"
TERRAIN_FORT = "fort"

TERRAIN_DATA = {
    TERRAIN_PLAIN: {
        "avoid": 0,
        "defense": 0,
        "heal": 0,
    },
    TERRAIN_GRASS: {
        "avoid": 20,
        "defense": 0,
        "heal": 0,
    },
    TERRAIN_FORT: {
        "avoid": 0,
        "defense": 2,
        "heal": 5,
    },
}


def get_terrain_at(tile_x, tile_y, terrain_map):
    if terrain_map is None:
        return TERRAIN_PLAIN
    return terrain_map[tile_x][tile_y]


def get_terrain_avoid_bonus(terrain_type):
    return TERRAIN_DATA.get(terrain_type, TERRAIN_DATA[TERRAIN_PLAIN])["avoid"]


def get_terrain_def_bonus(terrain_type):
    return TERRAIN_DATA.get(terrain_type, TERRAIN_DATA[TERRAIN_PLAIN])["defense"]


def apply_end_turn_terrain_effect(unit, terrain_type):
    if not unit or not unit.is_alive():
        return 0

    heal_amount = TERRAIN_DATA.get(terrain_type, TERRAIN_DATA[TERRAIN_PLAIN])["heal"]
    if heal_amount <= 0:
        return 0

    old_hp = unit.hp
    unit.hp = min(unit.max_hp, unit.hp + heal_amount)
    return unit.hp - old_hp


def build_terrain_overlays(cell_size):
    grass = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
    fort = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)

    dot_color = (60, 170, 80, 128)
    for x in range(8, cell_size, 14):
        for y in range(8, cell_size, 14):
            pygame.draw.circle(grass, dot_color, (x, y), 3)

    fort_color = (220, 185, 70, 128)
    wall_rect = pygame.Rect(8, 16, cell_size - 16, cell_size - 18)
    pygame.draw.rect(fort, fort_color, wall_rect, border_radius=4)
    pygame.draw.rect(fort, (190, 150, 45, 128), wall_rect, 2, border_radius=4)
    pygame.draw.rect(fort, fort_color, pygame.Rect(12, 10, 8, 10))
    pygame.draw.rect(fort, fort_color, pygame.Rect(cell_size - 20, 10, 8, 10))
    pygame.draw.rect(fort, fort_color, pygame.Rect(cell_size // 2 - 4, 6, 8, 14))
    pygame.draw.rect(fort, (180, 120, 40, 128), pygame.Rect(cell_size // 2 - 4, 26, 8, 14))

    return {
        TERRAIN_GRASS: grass,
        TERRAIN_FORT: fort,
    }


def draw_terrain_tile(screen, overlays, terrain_type, dest):
    overlay = overlays.get(terrain_type)
    if overlay:
        screen.blit(overlay, dest)
