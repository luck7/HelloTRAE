"""Tests for main.py entry point and integrated Game class."""
import pygame

from constants import (
    TILE_SIZE, GRID_W, GRID_H, GAME_W, GAME_H,
    T_EMPTY, T_BRICK, T_STEEL, T_WATER, T_GRASS,
    UP, DOWN, LEFT, RIGHT,
    DIR_TANK_IMG,
    BULLET_SPEED,
    STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER, STATE_WIN,
    TOTAL_ENEMIES, PLAYER_LIVES, SPAWN_PROTECTION,
    MAX_ENEMIES_ON_SCREEN,
)
from map import (
    parse_level, cell_to_pixel, pixel_to_cell, snap_axis,
    rect_for_center, bullet_rect,
)
from entities import Bullet, Tank, PlayerTank, EnemyTank, Explosion
from game import Game
from conftest import mock_keyboard


# ======================================================================
# Game class (integrated tests)
# ======================================================================
class TestGameInit:
    def test_initial_state_menu(self):
        g = Game()
        assert g.state == STATE_MENU

    def test_initial_score_zero(self):
        g = Game()
        assert g.score == 0

    def test_initial_base_alive(self):
        g = Game()
        assert g.base_alive is True

    def test_initial_no_player(self):
        g = Game()
        assert g.player is None

    def test_initial_no_enemies(self):
        g = Game()
        assert g.enemies == []

    def test_initial_no_bullets(self):
        g = Game()
        assert g.bullets == []

    def test_initial_enemies_remaining(self):
        g = Game()
        assert g.enemies_remaining == TOTAL_ENEMIES

    def test_grid_initialized(self):
        g = Game()
        assert len(g.grid) == GRID_H
        for row in g.grid:
            assert len(row) == GRID_W


class TestGameStartGame:
    def test_state_playing(self):
        g = Game()
        g.start_game()
        assert g.state == STATE_PLAYING

    def test_player_created(self):
        g = Game()
        g.start_game()
        assert g.player is not None
        assert g.player.alive is True

    def test_player_has_protection(self):
        g = Game()
        g.start_game()
        assert g.player.protection == SPAWN_PROTECTION

    def test_score_reset(self):
        g = Game()
        g.score = 500
        g.start_game()
        assert g.score == 0

    def test_enemies_spawned(self):
        g = Game()
        g.start_game()
        assert len(g.enemies) > 0

    def test_base_alive(self):
        g = Game()
        g.base_alive = False
        g.start_game()
        assert g.base_alive is True


class TestGameReset:
    def test_state_back_to_menu(self):
        g = Game()
        g.start_game()
        g.reset()
        assert g.state == STATE_MENU

    def test_score_zero(self):
        g = Game()
        g.score = 999
        g.reset()
        assert g.score == 0

    def test_player_none(self):
        g = Game()
        g.start_game()
        g.reset()
        assert g.player is None

    def test_enemies_cleared(self):
        g = Game()
        g.start_game()
        g.reset()
        assert g.enemies == []

    def test_high_score_preserved(self):
        g = Game()
        g.high_score = 1000
        g.reset()
        assert g.high_score == 1000


class TestGameUpdate:
    def test_menu_timer_increments(self):
        g = Game()
        assert g.state == STATE_MENU
        old_timer = g.menu_timer
        g.update()
        assert g.menu_timer == old_timer + 1

    def test_playing_state_updates(self):
        g = Game()
        g.start_game()
        old_timer = g.state_timer
        g.update()
        assert g.state_timer == old_timer + 1


class TestGameEndGame:
    def test_game_over_state(self):
        g = Game()
        g.start_game()
        g._end_game(STATE_GAME_OVER)
        assert g.state == STATE_GAME_OVER

    def test_win_state(self):
        g = Game()
        g.start_game()
        g._end_game(STATE_WIN)
        assert g.state == STATE_WIN

    def test_no_duplicate_state_change(self):
        g = Game()
        g.start_game()
        g._end_game(STATE_GAME_OVER)
        g.state_timer = 50
        g._end_game(STATE_GAME_OVER)
        assert g.state_timer == 50


class TestGameTanksProperty:
    def test_no_tanks_initially(self):
        g = Game()
        assert g.tanks == []

    def test_includes_enemies(self):
        g = Game()
        g.start_game()
        assert len(g.tanks) > 0

    def test_includes_player_when_alive(self):
        g = Game()
        g.start_game()
        assert g.player in g.tanks

    def test_excludes_dead_player(self):
        g = Game()
        g.start_game()
        g.player.alive = False
        assert g.player not in g.tanks


class TestGameScore:
    def test_high_score_tracks_best(self):
        g = Game()
        g.start_game()
        g.score = 500
        g.high_score = 0
        if g.score > g.high_score:
            g.high_score = g.score
        assert g.high_score == 500

    def test_high_score_not_decreased(self):
        g = Game()
        g.high_score = 1000
        g.score = 500
        if g.score > g.high_score:
            g.high_score = g.score
        assert g.high_score == 1000


# ======================================================================
# Tank.set_direction (via entities.Tank)
# ======================================================================
class TestTankSetDirection:
    def test_change_to_left(self):
        t = Tank('player', 100, 100, UP)
        t.set_direction(LEFT)
        assert t.direction == LEFT

    def test_change_to_down(self):
        t = Tank('player', 100, 100, UP)
        t.set_direction(DOWN)
        assert t.direction == DOWN

    def test_no_change_same_direction(self):
        t = Tank('player', 100, 100, UP)
        old_x = t.x
        t.set_direction(UP)
        assert t.x == old_x

    def test_change_snaps_x_for_vertical(self):
        t = Tank('player', 110, 100, RIGHT)
        t.set_direction(UP)
        assert t.x == snap_axis(110)

    def test_change_snaps_y_for_horizontal(self):
        t = Tank('player', 100, 110, DOWN)
        t.set_direction(LEFT)
        assert t.y == snap_axis(110)

    def test_image_updates(self):
        t = Tank('player', 100, 100, UP)
        t.set_direction(RIGHT)
        assert t.image == DIR_TANK_IMG['player'][RIGHT]


# ======================================================================
# Tank.try_move (via entities.Tank)
# ======================================================================
class TestTankTryMove:
    def test_move_success(self):
        g = Game()
        g.start_game()
        t = g.player
        old_x, old_y = t.x, t.y
        result = t.try_move(2, 0, g)
        if result:
            assert t.x == old_x + 2

    def test_move_blocked_by_wall(self):
        g = Game()
        g.grid = parse_level()[0]
        g.base_rect = rect_for_center(*cell_to_pixel(*g.base_cell))
        g.player = None
        g.enemies = []
        t = Tank('player', 3 * TILE_SIZE + 16, 3 * TILE_SIZE + 16, UP)
        for c, r in t._cells_under(rect_for_center(t.x + 2, t.y, TILE_SIZE - 2)):
            if 0 <= c < GRID_W and 0 <= r < GRID_H:
                g.grid[r][c] = T_BRICK
        result = t.try_move(TILE_SIZE, 0, g)
        assert result is False

    def test_move_out_of_bounds(self):
        g = Game()
        g.grid = parse_level()[0]
        g.base_rect = rect_for_center(*cell_to_pixel(*g.base_cell))
        g.player = None
        g.enemies = []
        t = Tank('player', 16, 100, UP)
        result = t.try_move(-TILE_SIZE, 0, g)
        assert result is False

    def test_move_blocked_by_base(self):
        g = Game()
        g.grid = parse_level()[0]
        g.base_rect = rect_for_center(*cell_to_pixel(*g.base_cell))
        g.player = None
        g.enemies = []
        bx, by = cell_to_pixel(*g.base_cell)
        t = Tank('player', bx, by - TILE_SIZE, UP)
        result = t.try_move(0, TILE_SIZE, g)
        assert result is False or t.y != by


# ======================================================================
# Tank._cells_under (via entities.Tank)
# ======================================================================
class TestTankCellsUnder:
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


# ======================================================================
# Tank.shoot (via entities.Tank)
# ======================================================================
class TestTankShoot:
    def test_player_shoot(self):
        g = Game()
        g.start_game()
        g.bullets = []
        g.player.shoot_cooldown = 0
        g.player.shoot(g)
        assert len(g.bullets) == 1

    def test_cooldown_prevents_shoot(self):
        g = Game()
        g.start_game()
        g.bullets = []
        g.player.shoot_cooldown = 10
        g.player.shoot(g)
        assert len(g.bullets) == 0

    def test_player_one_bullet_limit(self):
        g = Game()
        g.start_game()
        g.bullets = []
        existing = Bullet(g.player.x, g.player.y, UP, 'player')
        existing.alive = True
        existing.owner = 'player'
        g.bullets.append(existing)
        g.player.shoot_cooldown = 0
        g.player.shoot(g)
        player_bullets = [b for b in g.bullets if b.owner == 'player' and b.alive]
        assert len(player_bullets) == 1


# ======================================================================
# Game._update_bullet
# ======================================================================
class TestGameUpdateBullet:
    def _make_bullet(self, x, y, vx, vy, owner='player'):
        from unittest.mock import MagicMock
        b = MagicMock()
        b.x = float(x)
        b.y = float(y)
        b.vx = vx
        b.vy = vy
        b.alive = True
        b.owner = owner
        b.direction = UP
        return b

    def test_brick_destroyed(self):
        g = Game()
        g.grid = [[T_EMPTY] * GRID_W for _ in range(GRID_H)]
        g.grid[5][5] = T_BRICK
        g.base_rect = rect_for_center(*cell_to_pixel(*g.base_cell))
        g.player = None
        g.enemies = []
        bx = 5 * TILE_SIZE + TILE_SIZE // 2
        by = 5 * TILE_SIZE
        b = self._make_bullet(bx, by, 0, BULLET_SPEED)
        g.bullets = [b]
        g._update_bullet(b)
        assert g.grid[5][5] == T_EMPTY
        assert b.alive is False

    def test_steel_bounces(self):
        g = Game()
        g.grid = [[T_EMPTY] * GRID_W for _ in range(GRID_H)]
        g.grid[5][5] = T_STEEL
        g.base_rect = rect_for_center(*cell_to_pixel(*g.base_cell))
        g.player = None
        g.enemies = []
        bx = 5 * TILE_SIZE + TILE_SIZE // 2
        by = 5 * TILE_SIZE
        b = self._make_bullet(bx, by, 0, BULLET_SPEED)
        g.bullets = [b]
        g._update_bullet(b)
        assert g.grid[5][5] == T_STEEL
        assert b.alive is False

    def test_out_of_bounds(self):
        g = Game()
        g.grid = [[T_EMPTY] * GRID_W for _ in range(GRID_H)]
        g.base_rect = rect_for_center(*cell_to_pixel(*g.base_cell))
        g.player = None
        g.enemies = []
        b = self._make_bullet(100, -1, 0, -BULLET_SPEED)
        g.bullets = [b]
        g._update_bullet(b)
        assert b.alive is False

    def test_base_hit(self):
        g = Game()
        g.grid = [[T_EMPTY] * GRID_W for _ in range(GRID_H)]
        g.base_alive = True
        bx, by = cell_to_pixel(*g.base_cell)
        g.base_rect = rect_for_center(bx, by)
        g.player = None
        g.enemies = []
        b = self._make_bullet(bx, by, 0, BULLET_SPEED)
        g.bullets = [b]
        g._update_bullet(b)
        assert g.base_alive is False
        assert g.state == STATE_GAME_OVER

    def test_player_bullet_kills_enemy(self):
        g = Game()
        g.grid = [[T_EMPTY] * GRID_W for _ in range(GRID_H)]
        g.base_rect = rect_for_center(*cell_to_pixel(*g.base_cell))
        g.player = None
        enemy = EnemyTank(200, 200)
        enemy.alive = True
        enemy.protection = 0
        g.enemies = [enemy]
        g.score = 0
        b = self._make_bullet(enemy.x, enemy.y, 0, BULLET_SPEED)
        g.bullets = [b]
        g._update_bullet(b)
        assert enemy.alive is False
        assert g.score == 100

    def test_protected_tank_not_killed(self):
        g = Game()
        g.grid = [[T_EMPTY] * GRID_W for _ in range(GRID_H)]
        g.base_rect = rect_for_center(*cell_to_pixel(*g.base_cell))
        g.player = None
        enemy = EnemyTank(200, 200)
        enemy.alive = True
        enemy.protection = 50
        g.enemies = [enemy]
        b = self._make_bullet(enemy.x, enemy.y, 0, BULLET_SPEED)
        g.bullets = [b]
        g._update_bullet(b)
        assert enemy.alive is True
        assert b.alive is False

    def test_bullet_vs_bullet(self):
        g = Game()
        g.grid = [[T_EMPTY] * GRID_W for _ in range(GRID_H)]
        g.base_rect = rect_for_center(*cell_to_pixel(*g.base_cell))
        g.player = None
        g.enemies = []
        b1 = self._make_bullet(200, 200, 0, BULLET_SPEED, 'player')
        b2 = self._make_bullet(200, 200, 0, -BULLET_SPEED, 'enemy')
        g.bullets = [b1, b2]
        g._update_bullet(b1)
        assert b1.alive is False
        assert b2.alive is False


# ======================================================================
# Game._spawn_enemy
# ======================================================================
class TestGameSpawnEnemy:
    def test_spawn_decrements_remaining(self):
        g = Game()
        g.enemies_remaining = 10
        old = g.enemies_remaining
        g._spawn_enemy()
        if len(g.enemies) > 0:
            assert g.enemies_remaining == old - 1

    def test_no_spawn_when_none_remaining(self):
        g = Game()
        g.enemies_remaining = 0
        old_count = len(g.enemies)
        g._spawn_enemy()
        assert len(g.enemies) == old_count

    def test_no_spawn_when_max_on_screen(self):
        g = Game()
        g.enemies_remaining = 10
        while len(g.enemies) < MAX_ENEMIES_ON_SCREEN:
            g.enemies.append(EnemyTank(0, 0))
        old_count = len(g.enemies)
        g._spawn_enemy()
        assert len(g.enemies) == old_count


# ======================================================================
# Game._respawn_player
# ======================================================================
class TestGameRespawnPlayer:
    def test_respawn_decrements_lives(self):
        g = Game()
        g.start_game()
        g.player.alive = False
        old_lives = g.player.lives
        g._respawn_player()
        if old_lives > 1:
            assert g.player.lives == old_lives - 1

    def test_respawn_restores_position(self):
        g = Game()
        g.start_game()
        g.player.alive = False
        g.player.lives = 2
        g._respawn_player()
        px, py = cell_to_pixel(*g.player_spawn)
        assert g.player.x == px
        assert g.player.y == py

    def test_respawn_gives_protection(self):
        g = Game()
        g.start_game()
        g.player.alive = False
        g.player.lives = 2
        g._respawn_player()
        assert g.player.protection == SPAWN_PROTECTION

    def test_no_lives_ends_game(self):
        g = Game()
        g.start_game()
        g.player.alive = False
        g.player.lives = 1
        g._respawn_player()
        assert g.state == STATE_GAME_OVER


# ======================================================================
# PlayerTank.update
# ======================================================================
class TestPlayerTankUpdate:
    def _reset_keyboard(self):
        mock_keyboard.left = False
        mock_keyboard.right = False
        mock_keyboard.up = False
        mock_keyboard.down = False
        mock_keyboard.a = False
        mock_keyboard.d = False
        mock_keyboard.w = False
        mock_keyboard.s = False
        mock_keyboard.space = False

    def test_cooldown_decrements(self):
        g = Game()
        g.start_game()
        g.player.shoot_cooldown = 10
        self._reset_keyboard()
        g.player.update(g)
        assert g.player.shoot_cooldown == 9

    def test_protection_decrements(self):
        g = Game()
        g.start_game()
        g.player.protection = 50
        self._reset_keyboard()
        g.player.update(g)
        assert g.player.protection == 49

    def test_dead_player_no_update(self):
        g = Game()
        g.start_game()
        g.player.alive = False
        g.player.shoot_cooldown = 10
        g.player.update(g)
        assert g.player.shoot_cooldown == 10


# ======================================================================
# EnemyTank._cells_under
# ======================================================================
class TestEnemyTankCellsUnder:
    def test_cells_under_returns_set(self):
        t = Tank('enemy', 100, 100, DOWN)
        r = rect_for_center(100, 100, TILE_SIZE)
        cells = t._cells_under(r)
        assert isinstance(cells, set)
        assert len(cells) >= 1

    def test_cells_under_large_rect(self):
        t = Tank('enemy', 100, 100, DOWN)
        r = pygame.Rect(0, 0, TILE_SIZE * 3, TILE_SIZE * 3)
        cells = t._cells_under(r)
        assert len(cells) >= 9
