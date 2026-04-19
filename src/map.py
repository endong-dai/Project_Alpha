"""
map.py
Grid management.
"""

from terrain import TERRAIN_PLAIN


class Map:
    def __init__(self, size=10):
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.terrain_grid = [[TERRAIN_PLAIN for _ in range(size)] for _ in range(size)]

    def in_bounds(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

    def is_empty(self, x, y):
        if not self.in_bounds(x, y):
            return False
        return self.grid[x][y] is None

    def place_unit(self, unit, x, y):
        if not self.in_bounds(x, y):
            return
        self.grid[x][y] = unit
        unit.game_map = self
        unit.set_position(x, y)

    def move_unit(self, unit, new_x, new_y):
        x, y = unit.get_position()
        self.grid[x][y] = None
        self.grid[new_x][new_y] = unit
        unit.game_map = self
        unit.set_position(new_x, new_y)

    def get_unit(self, x, y):
        if not self.in_bounds(x, y):
            return None
        return self.grid[x][y]

    def remove_unit(self, unit):
        x, y = unit.get_position()
        if x is None or y is None:
            return
        if self.in_bounds(x, y) and self.grid[x][y] is unit:
            self.grid[x][y] = None
        unit.game_map = None
        unit.set_position(None, None)

    def set_terrain(self, x, y, terrain_type):
        if not self.in_bounds(x, y):
            return
        self.terrain_grid[x][y] = terrain_type

    def get_terrain(self, x, y):
        if not self.in_bounds(x, y):
            return TERRAIN_PLAIN
        return self.terrain_grid[x][y]
