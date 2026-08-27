"""Tests for map.py: parse_level and coordinate helpers."""
from constants import (
    TILE_SIZE, GRID_W, GRID_H,
    T_EMPTY, T_BRICK, T_STEEL, T_WATER, T_GRASS,
)
from map import (
    LEVEL_MAP, parse_level,
    cell_to_pixel, pixel_to_cell, snap_axis,
    rect_for_center, bullet_rect,
)


# ======================================================================
# parse_level
# ======================================================================
class TestParseLevel:
    def test_grid_dimensions(self):
        grid, _, _, _ = parse_level()
        assert len(grid) == GRID_H
        for row in grid:
            assert len(row) == GRID_W

    def test_returns_list_of_lists(self):
        grid, _, _, _ = parse_level()
        assert isinstance(grid, list)
        assert isinstance(grid[0], list)

    def test_enemy_spawns_found(self):
        _, enemy_spawns, _, _ = parse_level()
        assert len(enemy_spawns) == 3
        cols = sorted([c for c, r in enemy_spawns])
        assert cols == [0, 6, 12]

    def test_enemy_spawns_at_row_zero(self):
        _, enemy_spawns, _, _ = parse_level()
        for c, r in enemy_spawns:
            assert r == 0

    def test_player_spawn(self):
        _, _, player_spawn, _ = parse_level()
        assert player_spawn == (6, 12)

    def test_base_cell(self):
        _, _, _, base_cell = parse_level()
        assert base_cell == (6, 11)

    def test_brick_tiles(self):
        grid, _, _, _ = parse_level()
        # Row 2: "..BBBBBBBBB.." -> cols 2-10 are brick
        for c in range(2, 11):
            assert grid[2][c] == T_BRICK, f"Expected brick at col {c}, row 2"

    def test_steel_tiles(self):
        grid, _, _, _ = parse_level()
        # Row 4: "..B.SSSSS.B.." -> cols 4-8 are steel
        for c in range(4, 9):
            assert grid[4][c] == T_STEEL, f"Expected steel at col {c}, row 4"

    def test_water_tiles(self):
        grid, _, _, _ = parse_level()
        # Row 8: ".WW...G...WW." -> cols 1,2 and 10,11 are water
        assert grid[8][1] == T_WATER
        assert grid[8][2] == T_WATER
        assert grid[8][10] == T_WATER
        assert grid[8][11] == T_WATER

    def test_grass_tiles(self):
        grid, _, _, _ = parse_level()
        # Row 5: "..B...G...B.." -> col 6 is grass
        assert grid[5][6] == T_GRASS

    def test_empty_cells(self):
        grid, _, _, _ = parse_level()
        # Row 0: "E.....E.....E" -> cols 1-5, 7-11 should be empty
        for c in range(1, 6):
            assert grid[0][c] == T_EMPTY
        for c in range(7, 12):
            assert grid[0][c] == T_EMPTY

    def test_base_not_in_grid(self):
        """The base marker 'H' should not appear as a terrain tile."""
        grid, _, _, _ = parse_level()
        for row in grid:
            for tile in row:
                assert tile in (T_EMPTY, T_BRICK, T_STEEL, T_WATER, T_GRASS)

    def test_returns_tuple_of_four(self):
        result = parse_level()
        assert len(result) == 4


# ======================================================================
# LEVEL_MAP
# ======================================================================
class TestLevelMap:
    def test_dimensions(self):
        assert len(LEVEL_MAP) == GRID_H
        for row in LEVEL_MAP:
            assert len(row) == GRID_W

    def test_valid_characters(self):
        valid = {'E', '.', 'B', 'S', 'W', 'G', 'H', 'P'}
        for row in LEVEL_MAP:
            for ch in row:
                assert ch in valid


# ======================================================================
# cell_to_pixel
# ======================================================================
class TestCellToPixel:
    def test_origin(self):
        assert cell_to_pixel(0, 0) == (16, 16)

    def test_one_cell(self):
        assert cell_to_pixel(1, 1) == (48, 48)

    def test_corner(self):
        assert cell_to_pixel(GRID_W - 1, GRID_H - 1) == (
            (GRID_W - 1) * TILE_SIZE + TILE_SIZE // 2,
            (GRID_H - 1) * TILE_SIZE + TILE_SIZE // 2,
        )

    def test_center_offset(self):
        x, y = cell_to_pixel(3, 5)
        assert x == 3 * TILE_SIZE + TILE_SIZE // 2
        assert y == 5 * TILE_SIZE + TILE_SIZE // 2


# ======================================================================
# pixel_to_cell
# ======================================================================
class TestPixelToCell:
    def test_center_of_first_cell(self):
        assert pixel_to_cell(16, 16) == (0, 0)

    def test_center_of_second_cell(self):
        assert pixel_to_cell(48, 48) == (1, 1)

    def test_round_trip(self):
        for col in range(GRID_W):
            for row in range(GRID_H):
                px, py = cell_to_pixel(col, row)
                assert pixel_to_cell(px, py) == (col, row)


# ======================================================================
# snap_axis
# ======================================================================
class TestSnapAxis:
    def test_already_snapped(self):
        assert snap_axis(16) == 16

    def test_snap_to_nearest(self):
        assert snap_axis(20) == 16
        assert snap_axis(40) == 48

    def test_snap_midpoint(self):
        result = snap_axis(32)
        assert result in (16, 48)

    def test_snap_negative(self):
        result = snap_axis(-5)
        assert result == -16
