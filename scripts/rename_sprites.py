"""Rename the extracted sprite files based on the Battle City sprite sheet layout.

The sprite sheet (400x256) is divided into 16x16 cells (25 columns x 16 rows).
This script renames each sprite_r{row:02}_c{col:02}.png to a descriptive name
based on the Battle City game settings, following the naming convention used in
the images/ directory (e.g. tank_player_up, tile_brick, base, explosion).

Layout summary:
  - Rows 1-3,  cols 1-16 : Player 1 tanks (3 levels) - yellow
  - Rows 4-6,  cols 1-16 : Enemy tanks (3 types) - yellow
  - Rows 7-8,  cols 1-16 : Enemy armor tank (8 frames) - yellow
  - Rows 9-11, cols 1-16 : Player 2 tanks (3 levels) - green
  - Rows 12-14,cols 1-16 : Enemy tanks (3 types) - green
  - Rows 15-16,cols 1-16 : Enemy armor tank (8 frames) - green
  - Rows 1-16, cols 17-25: Tiles, base, explosions, flags, etc.

Within each tank row, the 16 cells are 4 directions x 4 frames:
  direction order: up, right, down, left
  frame order:     frame1, frame2, frame3, frame4
  cell index:      dir*4 + frame  (0-15)

Armor tanks span 2 rows (8 frames per direction):
  row 7  -> frames 1-4
  row 8  -> frames 5-8
  row 15 -> frames 1-4
  row 16 -> frames 5-8
"""

from pathlib import Path

SPRITES_DIR = Path(__file__).resolve().parents[1] / "sprites"

# Direction order within a tank row (0-3)
DIRS = ["up", "right", "down", "left"]

# Tank owner / type per row (rows are 1-indexed)
TANK_ROWS = {
    # Player 1 (yellow)
    1: ("player", "basic"),
    2: ("player", "fast"),
    3: ("player", "power"),
    # Enemy (yellow)
    4: ("enemy", "basic"),
    5: ("enemy", "fast"),
    6: ("enemy", "power"),
    # Enemy armor (yellow) - 8 frames across rows 7-8
    7: ("enemy", "armor", 0),   # frames 1-4
    8: ("enemy", "armor", 4),   # frames 5-8
    # Player 2 (green)
    9: ("player2", "basic"),
    10: ("player2", "fast"),
    11: ("player2", "power"),
    # Enemy (green)
    12: ("enemy2", "basic"),
    13: ("enemy2", "fast"),
    14: ("enemy2", "power"),
    # Enemy armor (green) - 8 frames across rows 15-16
    15: ("enemy2", "armor", 0),  # frames 1-4
    16: ("enemy2", "armor", 4),  # frames 5-8
}

# Tile / special sprites per cell (row, col) -> name
TILE_SPRITES = {
    # Brick tile pieces (row 1)
    (1, 17): "tile_brick",
    (1, 18): "tile_brick_right",
    (1, 19): "tile_brick_bottom",
    (1, 20): "tile_brick_left",
    (1, 21): "tile_brick_top",
    # Steel tile pieces (row 2)
    (2, 17): "tile_steel",
    (2, 18): "tile_steel_right",
    (2, 19): "tile_steel_bottom",
    (2, 20): "tile_steel_left",
    (2, 21): "tile_steel_top",
    # Water / grass / steel / base (row 3)
    (3, 17): "tile_water",
    (3, 18): "tile_grass",
    (3, 19): "tile_steel_alt",
    (3, 20): "base",
    (3, 21): "base_destroyed",
    # Water frames (row 4)
    (4, 17): "tile_water_1",
    (4, 18): "tile_water_2",
    # Row 5
    (5, 17): "tile_mixed",
    (5, 18): "tile_steel_alt2",
    (5, 19): "tile_brick_alt",
    # Water frames (row 6)
    (6, 17): "tile_water_3",
    (6, 18): "tile_water_4",
    # Spawn protection (row 7)
    (7, 17): "spawn_protect_1",
    (7, 18): "spawn_protect_2",
    (7, 19): "spawn_protect_3",
    (7, 20): "spawn_protect_4",
    (7, 21): "tile_steel_alt3",
    (7, 22): "tile_steel_alt4",
    (7, 23): "tile_grass_alt",
    # Base / flag (row 8)
    (8, 17): "base_flag_1",
    (8, 18): "base_flag_2",
    (8, 19): "base_flag_3",
    (8, 20): "base_flag_4",
    (8, 21): "base_flag_5",
    (8, 22): "base_flag_6",
    (8, 23): "base_flag_7",
    # Explosion frames (row 9)
    (9, 17): "explosion_1",
    (9, 18): "explosion_2",
    (9, 19): "explosion_3",
    (9, 20): "explosion_4",
    (9, 21): "explosion_5",
    (9, 22): "explosion_6",
    (9, 23): "explosion_7",
    # Explosion frames (row 10)
    (10, 17): "explosion_8",
    (10, 18): "explosion_9",
    (10, 19): "explosion_10",
    (10, 20): "explosion_11",
    (10, 21): "explosion_12",
    (10, 22): "explosion_13",
    (10, 23): "explosion_14",
    # Flag / text (row 11)
    (11, 19): "flag_1",
    (11, 20): "flag_2",
    (11, 21): "flag_3",
    (11, 22): "flag_4",
    (11, 23): "flag_5",
    # Flag / text (row 12)
    (12, 19): "flag_6",
    (12, 20): "flag_7",
    (12, 21): "flag_8",
    (12, 22): "flag_9",
    (12, 23): "flag_10",
    # Flag / text (row 13)
    (13, 19): "flag_11",
    (13, 20): "flag_12",
    (13, 21): "flag_13",
    (13, 22): "flag_14",
    (13, 23): "flag_15",
}


def tank_name(row: int, col: int) -> str:
    """Return the descriptive name for a tank cell."""
    info = TANK_ROWS[row]
    owner, tank_type = info[0], info[1]
    frame_offset = info[2] if len(info) > 2 else 0
    # Direction and frame within the row
    idx = col - 1  # 0-15
    direction = DIRS[idx // 4]
    frame = (idx % 4) + 1 + frame_offset
    return f"tank_{owner}_{tank_type}_{direction}_{frame}"


def build_mapping() -> dict:
    """Build a mapping from old filename to new filename."""
    mapping = {}
    for row in range(1, 17):
        for col in range(1, 26):
            old = f"sprite_r{row:02}_c{col:02}.png"
            if col <= 16 and row in TANK_ROWS:
                new = tank_name(row, col) + ".png"
            elif (row, col) in TILE_SPRITES:
                new = TILE_SPRITES[(row, col)] + ".png"
            else:
                # Empty / gray block cell - unique name
                new = f"block_gray_r{row:02}_c{col:02}.png"
            mapping[old] = new
    return mapping


def main() -> None:
    if not SPRITES_DIR.exists():
        print(f"Sprites directory not found: {SPRITES_DIR}")
        return

    mapping = build_mapping()
    renamed = 0
    skipped = 0
    errors = []

    for old, new in sorted(mapping.items()):
        old_path = SPRITES_DIR / old
        if not old_path.exists():
            skipped += 1
            continue
        new_path = SPRITES_DIR / new
        if new_path.exists():
            # Target already exists - this can happen if a previous run
            # already renamed this file. Skip it.
            skipped += 1
            continue
        try:
            old_path.rename(new_path)
            renamed += 1
        except Exception as e:
            errors.append(f"{old} -> {new}: {e}")

    print(f"Renamed {renamed} files, skipped {skipped}, {len(errors)} errors")
    for err in errors:
        print(f"  ERROR: {err}")


if __name__ == "__main__":
    main()
