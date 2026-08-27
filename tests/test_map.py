"""Tests for map initialization, random map generation, and respawn."""
import main
from main import (
    init_map, generate_random_map, respawn_player,
    MAP_W, MAP_H, TILE,
    TERRAIN_EMPTY, TERRAIN_BRICK, TERRAIN_STEEL, TERRAIN_GRASS, TERRAIN_WATER,
    BASE_COL, BASE_ROW, DIR_UP,
)
from conftest import make_empty_map


class TestInitMap:
    def test_stage_1_uses_stage_map(self):
        main.stage = 1
        init_map()
        assert len(main.map_data) == MAP_H
        for y in range(MAP_H):
            assert main.map_data[y] == main.STAGE_MAP[y]

    def test_map_data_is_copy(self):
        main.stage = 1
        init_map()
        # Modifying map_data should not affect STAGE_MAP
        main.map_data[0][0] = 999
        assert main.STAGE_MAP[0][0] != 999

    def test_stage_2_generates_random(self):
        main.stage = 2
        init_map()
        assert len(main.map_data) == MAP_H
        for row in main.map_data:
            assert len(row) == MAP_W


class TestGenerateRandomMap:
    def test_dimensions(self):
        generate_random_map()
        assert len(main.map_data) == MAP_H
        for row in main.map_data:
            assert len(row) == MAP_W

    def test_base_protection_bricks(self):
        generate_random_map()
        m = main.map_data
        assert m[11][5] == TERRAIN_BRICK
        assert m[11][6] == TERRAIN_BRICK
        assert m[11][7] == TERRAIN_BRICK
        assert m[12][5] == TERRAIN_BRICK
        assert m[12][7] == TERRAIN_BRICK
        assert m[10][5] == TERRAIN_BRICK
        assert m[10][6] == TERRAIN_BRICK
        assert m[10][7] == TERRAIN_BRICK

    def test_first_row_empty(self):
        """First row must be empty for enemy spawning."""
        generate_random_map()
        for x in range(MAP_W):
            assert main.map_data[0][x] == TERRAIN_EMPTY

    def test_spawn_points_clear(self):
        """Enemy spawn points at row 0 should be empty."""
        generate_random_map()
        for col in [0, 6, 12]:
            assert main.map_data[0][col] == TERRAIN_EMPTY

    def test_player_spawn_area_clear(self):
        """Player spawn area should be accessible."""
        generate_random_map()
        assert main.map_data[12][4] == TERRAIN_EMPTY
        assert main.map_data[12][6] == TERRAIN_EMPTY

    def test_only_valid_terrain(self):
        valid = {TERRAIN_EMPTY, TERRAIN_BRICK, TERRAIN_STEEL, TERRAIN_GRASS, TERRAIN_WATER}
        generate_random_map()
        for row in main.map_data:
            for tile in row:
                assert tile in valid

    def test_randomness_across_runs(self):
        """Two random maps should (very likely) differ."""
        generate_random_map()
        map1 = [row.copy() for row in main.map_data]
        generate_random_map()
        map2 = [row.copy() for row in main.map_data]
        # Extremely unlikely to be identical
        assert map1 != map2


class TestRespawnPlayer:
    def test_respawn_with_lives(self):
        main.lives = 2
        respawn_player()
        assert main.player is not None
        assert main.player.x == 4 * TILE
        assert main.player.y == 12 * TILE
        assert main.player.dir == DIR_UP
        assert main.player.is_player is True
        assert main.player.alive is True

    def test_no_respawn_without_lives(self):
        main.lives = 0
        old_player = main.player
        respawn_player()
        assert main.player == old_player  # unchanged (None)

    def test_respawn_position_in_bounds(self):
        main.lives = 1
        respawn_player()
        assert 0 <= main.player.x < main.SCREEN_W
        assert 0 <= main.player.y < main.SCREEN_H
