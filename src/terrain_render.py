"""
terrain_render.py
Pygame rendering for terrain tiles.

Split out from terrain.py so the terrain *data and rules* stay pygame-free and
importable in headless contexts (tests, balance simulation). Only the drawing
code lives here.
"""

import pygame

from terrain import (
    TERRAIN_BOSS_CASTLE,
    TERRAIN_BRIDGE,
    TERRAIN_CAPITAL,
    TERRAIN_CASTLE,
    TERRAIN_COLORS,
    TERRAIN_CORRUPTION,
    TERRAIN_DEEP_WATER,
    TERRAIN_ELECTRIC,
    TERRAIN_FOG,
    TERRAIN_FORD,
    TERRAIN_FOREST,
    TERRAIN_FORT,
    TERRAIN_GRASS,
    TERRAIN_ICE,
    TERRAIN_MOUNTAIN,
    TERRAIN_OPEN,
    TERRAIN_RIVER,
    TERRAIN_RUINS,
    TERRAIN_SEAL_FORT,
    TERRAIN_SHALLOW_WATER,
    TERRAIN_SNOW,
    TERRAIN_SWAMP,
    TERRAIN_TOWN,
    TERRAIN_TRENCH,
    TERRAIN_WIND,
)


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
