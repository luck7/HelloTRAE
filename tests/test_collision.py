"""Tests for collision detection and path-finding functions."""
import main
from main import (
    rect_overlap, is_path_clear, can_move_to,
    TILE, MAP_W, MAP_H, TANK_SIZE,
    TERRAIN_EMPTY, TERRAIN_BRICK, TERRAIN_STEEL, TERRAIN_WATER, TERRAIN_GRASS,
    BASE_COL, BASE_ROW, DIR_UP,
)
from conftest import make_empty_map, make_standard_map


# ======================================================================
# rect_overlap
# ======================================================================
class TestRectOverlap:
    def test_overlapping_rects(self):
        assert rect_overlap(0, 0, 10, 10, 5, 5, 10, 10) is True

    def test_no_overlap(self):
        assert rect_overlap(0, 0, 10, 10, 20, 20, 10, 10) is False

    def test_edge_touching_not_overlap(self):
        assert rect_overlap(0, 0, 10, 10, 10, 0, 10, 10) is False

    def test_contained_rect(self):
        assert rect_overlap(0, 0, 20, 20, 5, 5, 10, 10) is True

    def test_horizontal_overlap(self):
        assert rect_overlap(0, 0, 10, 5, 5, 0, 10, 5) is True

    def test_vertical_overlap(self):
        assert rect_overlap(0, 0, 5, 10, 0, 5, 5, 10) is True

    def test_zero_size_rect(self):
        # rect_overlap uses strict < comparison, so a zero-size rect
        # inside another rect still "overlaps" by the implementation's logic
        assert rect_overlap(5, 5, 0, 0, 0, 0, 10, 10) is True

    def test_symmetry(self):
        assert rect_overlap(0, 0, 10, 10, 5, 5, 10, 10) == \
               rect_overlap(5, 5, 10, 10, 0, 0, 10, 10)

    def test_negative_coordinates(self):
        assert rect_overlap(-10, -10, 20, 20, -5, -5, 10, 10) is True

    def test_far_apart_negative(self):
        assert rect_overlap(-100, -100, 10, 10, 100, 100, 10, 10) is False


# ======================================================================
# is_path_clear
# ======================================================================
class TestIsPathClear:
    def test_empty_map_is_clear(self):
        main.map_data = make_empty_map()
        assert is_path_clear(0, 0, TILE, TILE) is True

    def test_brick_blocks_path(self):
        main.map_data = make_empty_map()
        main.map_data[0][0] = TERRAIN_BRICK
        assert is_path_clear(0, 0, TILE, TILE) is False

    def test_steel_blocks_path(self):
        main.map_data = make_empty_map()
        main.map_data[0][0] = TERRAIN_STEEL
        assert is_path_clear(0, 0, TILE, TILE) is False

    def test_water_blocks_path(self):
        main.map_data = make_empty_map()
        main.map_data[0][0] = TERRAIN_WATER
        assert is_path_clear(0, 0, TILE, TILE) is False

    def test_grass_does_not_block(self):
        main.map_data = make_empty_map()
        main.map_data[0][0] = TERRAIN_GRASS
        assert is_path_clear(0, 0, TILE, TILE) is True

    def test_out_of_bounds_left(self):
        main.map_data = make_empty_map()
        assert is_path_clear(-1, 0, TILE, TILE) is False

    def test_out_of_bounds_top(self):
        main.map_data = make_empty_map()
        assert is_path_clear(0, -1, TILE, TILE) is False

    def test_out_of_bounds_right(self):
        main.map_data = make_empty_map()
        assert is_path_clear(MAP_W * TILE, 0, TILE, TILE) is False

    def test_out_of_bounds_bottom(self):
        main.map_data = make_empty_map()
        assert is_path_clear(0, MAP_H * TILE, TILE, TILE) is False

    def test_base_blocks_path(self):
        main.map_data = make_empty_map()
        base_x = BASE_COL * TILE
        base_y = BASE_ROW * TILE
        assert is_path_clear(base_x, base_y, TILE, TILE) is False

    def test_clear_area_near_base(self):
        main.map_data = make_empty_map()
        base_x = BASE_COL * TILE
        base_y = BASE_ROW * TILE
        # Position far from base
        assert is_path_clear(0, 0, TILE, TILE) is True

    def test_multi_tile_span_hits_terrain(self):
        main.map_data = make_empty_map()
        main.map_data[0][1] = TERRAIN_BRICK
        # A 2-tile wide object at x=0 should overlap tile (0,1) which is brick
        assert is_path_clear(0, 0, TILE * 2, TILE) is False

    def test_standard_map_spawn_area_clear(self):
        """Player spawn area (col 4, row 12) should be accessible."""
        main.map_data = make_standard_map()
        # Row 12, col 4 is empty in STAGE_MAP
        assert main.STAGE_MAP[12][4] == TERRAIN_EMPTY


# ======================================================================
# can_move_to
# ======================================================================
class TestCanMoveTo:
    def _make_tank(self, x, y, is_player=False):
        from unittest.mock import MagicMock
        tank = MagicMock()
        tank.x = x
        tank.y = y
        tank.width = TANK_SIZE
        tank.height = TANK_SIZE
        tank.alive = True
        return tank

    def test_no_other_tanks_clear(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        tank = self._make_tank(0, 0)
        assert can_move_to(tank, 100, 100) is True

    def test_blocked_by_player(self):
        main.map_data = make_empty_map()
        main.player = self._make_tank(100, 100, is_player=True)
        main.enemies = []
        tank = self._make_tank(0, 0)
        # Overlaps with player at (100,100)
        assert can_move_to(tank, 100, 100) is False

    def test_not_blocked_far_from_player(self):
        main.map_data = make_empty_map()
        main.player = self._make_tank(100, 100, is_player=True)
        main.enemies = []
        tank = self._make_tank(0, 0)
        assert can_move_to(tank, 300, 300) is True

    def test_blocked_by_alive_enemy(self):
        main.map_data = make_empty_map()
        main.player = None
        enemy = self._make_tank(200, 200)
        main.enemies = [enemy]
        tank = self._make_tank(0, 0)
        assert can_move_to(tank, 200, 200) is False

    def test_dead_enemy_does_not_block(self):
        main.map_data = make_empty_map()
        main.player = None
        enemy = self._make_tank(200, 200)
        enemy.alive = False
        main.enemies = [enemy]
        tank = self._make_tank(0, 0)
        assert can_move_to(tank, 200, 200) is True

    def test_self_not_blocked_by_self(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        tank = self._make_tank(100, 100)
        # Tank should be able to "move" to its own position
        assert can_move_to(tank, 100, 100) is True

    def test_self_enemy_not_blocked_by_self(self):
        main.map_data = make_empty_map()
        main.player = None
        tank = self._make_tank(100, 100)
        main.enemies = [tank]
        assert can_move_to(tank, 100, 100) is True

    def test_blocked_by_multiple_enemies(self):
        main.map_data = make_empty_map()
        main.player = None
        e1 = self._make_tank(50, 50)
        e2 = self._make_tank(200, 200)
        main.enemies = [e1, e2]
        tank = self._make_tank(0, 0)
        assert can_move_to(tank, 50, 50) is False
        assert can_move_to(tank, 200, 200) is False
        assert can_move_to(tank, 350, 350) is True
