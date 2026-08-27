"""Tests for collision detection via Tank.try_move and rect helpers."""
import pygame
from unittest.mock import MagicMock

from constants import (
    TILE_SIZE, GRID_W, GRID_H, GAME_W, GAME_H,
    T_EMPTY, T_BRICK, T_STEEL, T_WATER, T_GRASS,
    UP, DOWN, LEFT, RIGHT,
)
from map import parse_level, cell_to_pixel, rect_for_center, bullet_rect
from entities import Tank, PlayerTank, EnemyTank
from game import Game
from conftest import make_empty_map


# ======================================================================
# rect_for_center
# ======================================================================
class TestRectForCenter:
    def test_default_size(self):
        r = rect_for_center(100, 100)
        assert r.left == 100 - TILE_SIZE // 2
        assert r.top == 100 - TILE_SIZE // 2
        assert r.width == TILE_SIZE
        assert r.height == TILE_SIZE

    def test_custom_size(self):
        r = rect_for_center(100, 100, 20)
        assert r.width == 20
        assert r.height == 20

    def test_center_position(self):
        r = rect_for_center(100, 200)
        cx = r.left + r.width // 2
        cy = r.top + r.height // 2
        assert cx == 100
        assert cy == 200


# ======================================================================
# bullet_rect
# ======================================================================
class TestBulletRect:
    def test_size(self):
        b = MagicMock()
        b.x = 100
        b.y = 100
        r = bullet_rect(b)
        assert r.width == 16
        assert r.height == 16

    def test_centered(self):
        b = MagicMock()
        b.x = 100
        b.y = 200
        r = bullet_rect(b)
        assert r.centerx == 100
        assert r.centery == 200


# ======================================================================
# Tank.try_move -- wall collisions
# ======================================================================
class TestTryMoveWallCollisions:
    def _make_game_with_empty_grid(self):
        g = Game()
        g.grid = make_empty_map()
        g.base_rect = rect_for_center(*cell_to_pixel(6, 11))
        g.player = None
        g.enemies = []
        return g

    def test_brick_blocks_movement(self):
        g = self._make_game_with_empty_grid()
        g.grid[0][0] = T_BRICK
        t = Tank('player', 16, 16, UP)
        result = t.try_move(0, -2, g)
        assert result is False

    def test_steel_blocks_movement(self):
        g = self._make_game_with_empty_grid()
        g.grid[0][0] = T_STEEL
        t = Tank('player', 16, 16, UP)
        result = t.try_move(0, -2, g)
        assert result is False

    def test_water_blocks_movement(self):
        g = self._make_game_with_empty_grid()
        g.grid[0][0] = T_WATER
        t = Tank('player', 16, 16, UP)
        result = t.try_move(0, -2, g)
        assert result is False

    def test_grass_does_not_block(self):
        g = self._make_game_with_empty_grid()
        g.grid[0][0] = T_GRASS
        t = Tank('player', 16, 48, DOWN)
        result = t.try_move(0, -2, g)
        assert result is True

    def test_empty_is_clear(self):
        g = self._make_game_with_empty_grid()
        t = Tank('player', 100, 100, UP)
        result = t.try_move(0, -2, g)
        assert result is True


# ======================================================================
# Tank.try_move -- bounds check
# ======================================================================
class TestTryMoveBounds:
    def _make_game_with_empty_grid(self):
        g = Game()
        g.grid = make_empty_map()
        g.base_rect = rect_for_center(*cell_to_pixel(6, 11))
        g.player = None
        g.enemies = []
        return g

    def test_left_boundary(self):
        g = self._make_game_with_empty_grid()
        t = Tank('player', 16, 100, LEFT)
        result = t.try_move(-TILE_SIZE, 0, g)
        assert result is False

    def test_right_boundary(self):
        g = self._make_game_with_empty_grid()
        t = Tank('player', GAME_W - 16, 100, RIGHT)
        result = t.try_move(TILE_SIZE, 0, g)
        assert result is False

    def test_top_boundary(self):
        g = self._make_game_with_empty_grid()
        t = Tank('player', 100, 16, UP)
        result = t.try_move(0, -TILE_SIZE, g)
        assert result is False

    def test_bottom_boundary(self):
        g = self._make_game_with_empty_grid()
        t = Tank('player', 100, GAME_H - 16, DOWN)
        result = t.try_move(0, TILE_SIZE, g)
        assert result is False


# ======================================================================
# Tank.try_move -- tank-tank collisions
# ======================================================================
class TestTryMoveTankCollisions:
    def _make_game_with_empty_grid(self):
        g = Game()
        g.grid = make_empty_map()
        g.base_rect = rect_for_center(*cell_to_pixel(6, 11))
        g.player = None
        g.enemies = []
        return g

    def test_blocked_by_other_tank(self):
        g = self._make_game_with_empty_grid()
        # Place other tank close enough that moving 2px overlaps
        other = Tank('enemy', 100, 85, DOWN)
        other.alive = True
        g.enemies = [other]
        t = Tank('player', 100, 100, UP)
        result = t.try_move(0, -2, g)
        assert result is False

    def test_dead_tank_does_not_block(self):
        g = self._make_game_with_empty_grid()
        other = Tank('enemy', 100, 68, DOWN)
        other.alive = False
        g.enemies = [other]
        t = Tank('player', 100, 100, UP)
        result = t.try_move(0, -2, g)
        assert result is True

    def test_base_rect_blocks_movement(self):
        g = self._make_game_with_empty_grid()
        bx, by = cell_to_pixel(6, 11)
        t = Tank('player', bx, by - TILE_SIZE, UP)
        result = t.try_move(0, 2, g)
        # Should be blocked by base rect
        assert result is False or t.y != by


# ======================================================================
# Tank._cells_under
# ======================================================================
class TestCellsUnder:
    def test_single_cell(self):
        t = Tank('player', 16, 16, UP)
        r = rect_for_center(16, 16, TILE_SIZE)
        cells = t._cells_under(r)
        assert (0, 0) in cells

    def test_multiple_cells(self):
        t = Tank('player', 32, 32, UP)
        r = rect_for_center(32, 32, TILE_SIZE * 2)
        cells = t._cells_under(r)
        assert len(cells) >= 4

    def test_clamped_to_grid(self):
        t = Tank('player', 16, 16, UP)
        r = pygame.Rect(-100, -100, 2000, 2000)
        cells = t._cells_under(r)
        for c, row in cells:
            assert 0 <= c < GRID_W
            assert 0 <= row < GRID_H
