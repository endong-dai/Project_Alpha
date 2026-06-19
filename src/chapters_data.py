"""
chapters_data.py
Chapter (campaign battle) definitions.

Separated from gui_main.py so adding/editing a chapter no longer means touching
the 4000-line UI module. Kept as a Python module (not JSON) on purpose: the
specs use tuples for weapons/positions/terrain, and a Python module preserves
those types exactly with zero conversion risk.
"""

import copy

from terrain import TERRAIN_FORT, TERRAIN_GRASS

CHAPTERS = {
    1: {
        "name": "Chapter 1",
        "enemy_level": 1,
        "players": [
            {
                "unit_id": "hero",
                "name": "Hero",
                "strength": 5,
                "defense": 5,
                "speed": 8,
                "move": 3,
                "max_hp": 18,
                "weapon": ("Iron Sword", 5, 1),
                "inventory": [
                    ("weapon", "Iron Sword", 5, 1),
                    ("weapon", "Javelin", 4, 2),
                    ("potion", "Potion", 8),
                ],
                "sprite_key": "F1",
                "position": (3, 3),
            }
        ],
        "enemies": [
            {
                "name": "Enemy",
                "level": 1,
                "strength": 4,
                "defense": 4,
                "speed": 5,
                "move": 3,
                "max_hp": 16,
                "weapon": ("Iron Blade", 5, 1),
                "inventory": [("weapon", "Iron Blade", 5, 1)],
                "sprite_key": "E1",
                "position": (3, 6),
            }
        ],
        "terrain": [
            (TERRAIN_GRASS, 2, 2),
            (TERRAIN_GRASS, 4, 2),
            (TERRAIN_GRASS, 2, 4),
            (TERRAIN_FORT, 5, 5),
        ],
    },
    2: {
        "name": "Chapter 2",
        "enemy_level": 3,
        "players": [
            {
                "unit_id": "hero",
                "name": "Hero",
                "strength": 5,
                "defense": 5,
                "speed": 8,
                "move": 3,
                "max_hp": 18,
                "weapon": ("Iron Sword", 5, 1),
                "inventory": [
                    ("weapon", "Iron Sword", 5, 1),
                    ("weapon", "Javelin", 4, 2),
                    ("potion", "Potion", 8),
                ],
                "sprite_key": "F1",
                "position": (2, 3),
            },
            {
                "unit_id": "knight",
                "name": "Knight",
                "strength": 6,
                "defense": 7,
                "speed": 4,
                "move": 2,
                "max_hp": 20,
                "weapon": ("Lance", 4, 1),
                "inventory": [
                    ("weapon", "Lance", 4, 1),
                    ("weapon", "Javelin", 3, 2),
                ],
                "sprite_key": "M1",
                "position": (4, 3),
            },
        ],
        "enemies": [
            {
                "name": "Bandit",
                "level": 3,
                "strength": 5,
                "defense": 3,
                "speed": 5,
                "move": 3,
                "max_hp": 16,
                "weapon": ("Axe", 5, 1),
                "inventory": [("weapon", "Axe", 5, 1)],
                "sprite_key": "E1",
                "position": (2, 7),
            },
            {
                "name": "Soldier",
                "level": 3,
                "strength": 4,
                "defense": 5,
                "speed": 4,
                "move": 3,
                "max_hp": 17,
                "weapon": ("Spear", 4, 1),
                "inventory": [("weapon", "Spear", 4, 1)],
                "sprite_key": "E2",
                "position": (5, 6),
            },
        ],
        "terrain": [
            (TERRAIN_GRASS, 1, 3),
            (TERRAIN_GRASS, 2, 4),
            (TERRAIN_GRASS, 4, 4),
            (TERRAIN_GRASS, 6, 5),
            (TERRAIN_FORT, 3, 5),
            (TERRAIN_FORT, 6, 6),
        ],
    },
}


def load_chapter(chapter_id):
    """Return a deep copy of a chapter spec (safe to mutate), or None."""
    chapter = CHAPTERS.get(chapter_id)
    return copy.deepcopy(chapter) if chapter is not None else None
