"""Tests for constants defined in main.py."""
import main


class TestTileConstants:
    def test_tile_size(self):
        assert main.TILE == 32

    def test_map_dimensions(self):
        assert main.MAP_W == 13
        assert main.MAP_H == 13

    def test_screen_dimensions(self):
        assert main.SCREEN_W == main.MAP_W * main.TILE  # 416
        assert main.SCREEN_H == main.MAP_H * main.TILE  # 416

    def test_tank_size(self):
        assert main.TANK_SIZE == 32

    def test_bullet_size(self):
        assert main.BULLET_SIZE == 16

    def test_grid_size(self):
        assert main.GRID == 16

    def test_half_tile(self):
        assert main.HALF_TILE == main.TILE // 2  # 16


class TestDirectionConstants:
    def test_direction_values(self):
        assert main.DIR_UP == 0
        assert main.DIR_RIGHT == 1
        assert main.DIR_DOWN == 2
        assert main.DIR_LEFT == 3

    def test_directions_are_unique(self):
        dirs = [main.DIR_UP, main.DIR_RIGHT, main.DIR_DOWN, main.DIR_LEFT]
        assert len(set(dirs)) == 4


class TestTerrainConstants:
    def test_terrain_values(self):
        assert main.TERRAIN_EMPTY == 0
        assert main.TERRAIN_BRICK == 1
        assert main.TERRAIN_STEEL == 2
        assert main.TERRAIN_GRASS == 3
        assert main.TERRAIN_WATER == 4

    def test_terrains_are_unique(self):
        terrains = [
            main.TERRAIN_EMPTY, main.TERRAIN_BRICK, main.TERRAIN_STEEL,
            main.TERRAIN_GRASS, main.TERRAIN_WATER,
        ]
        assert len(set(terrains)) == 5


class TestBasePosition:
    def test_base_col(self):
        assert main.BASE_COL == 6

    def test_base_row(self):
        assert main.BASE_ROW == 12

    def test_base_within_map(self):
        assert 0 <= main.BASE_COL < main.MAP_W
        assert 0 <= main.BASE_ROW < main.MAP_H


class TestStageMap:
    def test_dimensions(self):
        assert len(main.STAGE_MAP) == main.MAP_H
        for row in main.STAGE_MAP:
            assert len(row) == main.MAP_W

    def test_valid_terrain_values(self):
        valid = {main.TERRAIN_EMPTY, main.TERRAIN_BRICK, main.TERRAIN_STEEL,
                 main.TERRAIN_GRASS, main.TERRAIN_WATER}
        for row in main.STAGE_MAP:
            for tile in row:
                assert tile in valid

    def test_base_area_has_bricks(self):
        """The area around the base should have protective brick walls."""
        m = main.STAGE_MAP
        # Row 11 around base (col 6) should have bricks
        assert m[11][5] == main.TERRAIN_BRICK
        assert m[11][6] == main.TERRAIN_BRICK
        assert m[11][7] == main.TERRAIN_BRICK


class TestWindowDimensions:
    def test_width(self):
        assert main.WIDTH == main.SCREEN_W + 120

    def test_height(self):
        assert main.HEIGHT == main.SCREEN_H
