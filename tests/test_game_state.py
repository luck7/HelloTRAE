"""Tests for game.py: Game class state management, spawning, and bullet updates."""
from unittest.mock import MagicMock

from constants import (
    TILE_SIZE, GRID_W, GRID_H, GAME_W, GAME_H,
    T_EMPTY, T_BRICK, T_STEEL,
    UP, DOWN, LEFT, RIGHT,
    STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER, STATE_WIN,
    TOTAL_ENEMIES, SPAWN_PROTECTION, PLAYER_SHOOT_COOLDOWN,
    BULLET_SPEED, MAX_ENEMIES_ON_SCREEN,
)
from map import parse_level, cell_to_pixel, rect_for_center, bullet_rect
from entities import Bullet, Tank, PlayerTank, EnemyTank, Explosion
from game import Game
from conftest import make_empty_map


def _make_game_with_empty_grid():
    g = Game()
    g.grid = make_empty_map()
    g.base_rect = rect_for_center(*cell_to_pixel(6, 11))
    g.player = None
    g.enemies = []
    return g


# ======================================================================
# Game state transitions
# ======================================================================
class TestGameOverState:
    def test_game_over_from_playing(self):
        g = Game()
        g.start_game()
        g._end_game(STATE_GAME_OVER)
        assert g.state == STATE_GAME_OVER

    def test_game_over_from_any_state(self):
        for state in [STATE_MENU, STATE_PLAYING, STATE_PAUSED]:
            g = Game()
            g.state = state
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


# ======================================================================
# Game.reset
# ======================================================================
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

    def test_bullets_cleared(self):
        g = Game()
        g.start_game()
        g.reset()
        assert g.bullets == []

    def test_explosions_cleared(self):
        g = Game()
        g.start_game()
        g.reset()
        assert g.explosions == []

    def test_high_score_preserved(self):
        g = Game()
        g.high_score = 1000
        g.reset()
        assert g.high_score == 1000

    def test_base_alive_restored(self):
        g = Game()
        g.start_game()
        g.base_alive = False
        g.reset()
        assert g.base_alive is True


# ======================================================================
# Game.start_game
# ======================================================================
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

    def test_enemies_remaining_reset(self):
        g = Game()
        g.enemies_remaining = 5
        g.start_game()
        # start_game spawns 2 enemies, so remaining = TOTAL - 2
        assert g.enemies_remaining == TOTAL_ENEMIES - 2


# ======================================================================
# Game._spawn_enemy
# ======================================================================
class TestSpawnEnemy:
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
class TestRespawnPlayer:
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

    def test_respawn_restores_direction(self):
        g = Game()
        g.start_game()
        g.player.alive = False
        g.player.lives = 2
        g.player.direction = DOWN
        g._respawn_player()
        assert g.player.direction == UP


# ======================================================================
# Game._update_bullet
# ======================================================================
class TestUpdateBullet:
    def _make_bullet(self, x, y, vx, vy, owner='player'):
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
        g = _make_game_with_empty_grid()
        g.grid[5][5] = T_BRICK
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
        g = _make_game_with_empty_grid()
        g.grid[5][5] = T_STEEL
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
        g = _make_game_with_empty_grid()
        g.player = None
        g.enemies = []
        b = self._make_bullet(100, -1, 0, -BULLET_SPEED)
        g.bullets = [b]
        g._update_bullet(b)
        assert b.alive is False

    def test_base_hit(self):
        g = _make_game_with_empty_grid()
        g.base_alive = True
        bx, by = cell_to_pixel(6, 11)
        g.base_rect = rect_for_center(bx, by)
        g.player = None
        g.enemies = []
        b = self._make_bullet(bx, by, 0, BULLET_SPEED)
        g.bullets = [b]
        g._update_bullet(b)
        assert g.base_alive is False
        assert g.state == STATE_GAME_OVER

    def test_player_bullet_kills_enemy(self):
        g = _make_game_with_empty_grid()
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
        g = _make_game_with_empty_grid()
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
        g = _make_game_with_empty_grid()
        g.player = None
        g.enemies = []
        b1 = self._make_bullet(200, 200, 0, BULLET_SPEED, 'player')
        b2 = self._make_bullet(200, 200, 0, -BULLET_SPEED, 'enemy')
        g.bullets = [b1, b2]
        g._update_bullet(b1)
        assert b1.alive is False
        assert b2.alive is False


# ======================================================================
# Game.update
# ======================================================================
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

    def test_game_over_state_timer_increments(self):
        g = Game()
        g.start_game()
        g._end_game(STATE_GAME_OVER)
        old_timer = g.state_timer
        g.update()
        assert g.state_timer == old_timer + 1


# ======================================================================
# Game.tanks property
# ======================================================================
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
