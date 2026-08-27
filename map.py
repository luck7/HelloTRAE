"""
Battle City - Level map and coordinate utilities.

Contains the level layout data, map parsing logic, and helper functions
for converting between grid coordinates and pixel positions.
"""

from pygame import Rect

from constants import (
    TILE_SIZE, GRID_W, GRID_H,
    T_EMPTY, T_BRICK, T_STEEL, T_WATER, T_GRASS,
    BULLET_SIZE,
)

# ----------------------------------------------------------------------
# Level Map
#   .  empty       B  brick        S  steel
#   W  water       G  grass        H  base (eagle)
#   E  enemy spawn P  player spawn
# ----------------------------------------------------------------------
LEVEL_MAP = [
    "E.....E.....E",
    ".............",
    "..BBBBBBBBB..",
    "..B.......B..",
    "..B.SSSSS.B..",
    "..B...G...B..",
    "..BBBBBBBBB..",
    ".............",
    ".WW...G...WW.",
    ".WW.......WW.",
    ".....BBB.....",
    ".....BHB.....",
    "......P......",
]


def parse_level():
    """Parse LEVEL_MAP into a tile grid and locate spawn / base cells.

    Returns
    -------
    tuple of (grid, enemy_spawns, player_spawn, base_cell)
        grid           : list[list[int]]  -- 2-D tile array
        enemy_spawns   : list[tuple[int, int]]
        player_spawn   : tuple[int, int]
        base_cell      : tuple[int, int]
    """
    grid = [[T_EMPTY for _ in range(GRID_W)] for _ in range(GRID_H)]
    enemy_spawns = []
    player_spawn = (GRID_W // 2, GRID_H - 1)
    base_cell = (GRID_W // 2, GRID_H - 2)
    for r, row in enumerate(LEVEL_MAP):
        for c, ch in enumerate(row):
            if ch == 'B':
                grid[r][c] = T_BRICK
            elif ch == 'S':
                grid[r][c] = T_STEEL
            elif ch == 'W':
                grid[r][c] = T_WATER
            elif ch == 'G':
                grid[r][c] = T_GRASS
            elif ch == 'E':
                enemy_spawns.append((c, r))
            elif ch == 'P':
                player_spawn = (c, r)
            elif ch == 'H':
                base_cell = (c, r)
    return grid, enemy_spawns, player_spawn, base_cell


# ----------------------------------------------------------------------
# Coordinate helpers
# ----------------------------------------------------------------------
def cell_to_pixel(col, row):
    """Convert grid cell to pixel center for a 32x32 actor."""
    return col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2


def pixel_to_cell(x, y):
    """Convert pixel center to grid cell."""
    return int((x - TILE_SIZE // 2) // TILE_SIZE), int((y - TILE_SIZE // 2) // TILE_SIZE)


def snap_axis(value):
    """Snap a pixel center to the nearest tile center on its axis."""
    return round((value - TILE_SIZE // 2) / TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2


def rect_for_center(x, y, size=TILE_SIZE):
    """Build a Rect for an actor of given size centered at (x, y)."""
    half = size // 2
    return Rect(x - half, y - half, size, size)


def bullet_rect(b):
    """Build a pygame.Rect for a 16x16 bullet centered at (b.x, b.y).

    pgzero's Actor does not expose ``.rect`` directly, so we construct one
    from the position.  Used for collision tests against pygame.Rects.
    """
    half = BULLET_SIZE // 2
    return Rect(int(b.x) - half, int(b.y) - half, BULLET_SIZE, BULLET_SIZE)
