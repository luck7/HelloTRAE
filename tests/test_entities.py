"""Tests for entities.py: Bullet, Explosion, Tank, PlayerTank, EnemyTank."""
from unittest.mock import MagicMock

from constants import (
    TILE_SIZE, GRID_W, GRID_H, GAME_W, GAME_H,
    T_EMPTY, T_BRICK,
    UP, DOWN, LEFT, RIGHT,
    DIR_BULLET_IMG, DIR_TANK_IMG,
    BULLET_SPEED, TANK_SPEED,
    PLAYER_SHOOT_COOLDOWN, PLAYER_LIVES,
)
from map import rect_for_center, cell_to_pixel
from entities import Bullet, Explosion, Tank, PlayerTank, EnemyTank
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
# Bullet
# ======================================================================
class TestBulletInit:
    def test_position(self):
        b = Bullet(100, 200, UP, 'player')
        assert b.x == 100
        assert b.y == 200

    def test_direction(self):
        b = Bullet(0, 0, RIGHT, 'player')
        assert b.direction == RIGHT

    def test_owner(self):
        assert Bullet(0, 0, UP, 'player').owner == 'player'
        assert Bullet(0, 0, UP, 'enemy').owner == 'enemy'

    def test_velocity_up(self):
        b = Bullet(0, 0, UP, 'player')
        assert b.vy == -BULLET_SPEED
        assert b.vx == 0

    def test_velocity_down(self):
        b = Bullet(0, 0, DOWN, 'player')
        assert b.vy == BULLET_SPEED
        assert b.vx == 0

    def test_velocity_left(self):
        b = Bullet(0, 0, LEFT, 'player')
        assert b.vx == -BULLET_SPEED
        assert b.vy == 0

    def test_velocity_right(self):
        b = Bullet(0, 0, RIGHT, 'player')
        assert b.vx == BULLET_SPEED
        assert b.vy == 0

    def test_alive_on_creation(self):
        b = Bullet(0, 0, UP, 'player')
        assert b.alive is True

    def test_image_set(self):
        b = Bullet(0, 0, UP, 'player')
        assert b.image == DIR_BULLET_IMG[UP]


class TestBulletMovement:
    def test_move_up(self):
        b = Bullet(100, 100, UP, 'player')
        b.update()
        assert b.y == 100 - BULLET_SPEED

    def test_move_down(self):
        b = Bullet(100, 100, DOWN, 'player')
        b.update()
        assert b.y == 100 + BULLET_SPEED

    def test_move_left(self):
        b = Bullet(100, 100, LEFT, 'player')
        b.update()
        assert b.x == 100 - BULLET_SPEED

    def test_move_right(self):
        b = Bullet(100, 100, RIGHT, 'player')
        b.update()
        assert b.x == 100 + BULLET_SPEED


class TestBulletBounds:
    def test_out_of_bounds_top(self):
        b = Bullet(100, 0, UP, 'player')
        b.update()
        assert b.alive is False

    def test_out_of_bounds_left(self):
        b = Bullet(0, 100, LEFT, 'player')
        b.update()
        assert b.alive is False

    def test_out_of_bounds_right(self):
        b = Bullet(GAME_W, 100, RIGHT, 'player')
        b.update()
        assert b.alive is False

    def test_out_of_bounds_bottom(self):
        b = Bullet(100, GAME_H, DOWN, 'player')
        b.update()
        assert b.alive is False

    def test_in_bounds_stays_alive(self):
        b = Bullet(100, 100, UP, 'player')
        b.update()
        assert b.alive is True


# ======================================================================
# Explosion
# ======================================================================
class TestExplosion:
    def test_initial_timer(self):
        e = Explosion(100, 100)
        assert e.timer == 18

    def test_update_decrements_timer(self):
        e = Explosion(100, 100)
        e.update()
        assert e.timer == 17

    def test_position(self):
        e = Explosion(50, 75)
        assert e.x == 50
        assert e.y == 75


# ======================================================================
# Tank base class
# ======================================================================
class TestTankInit:
    def test_position(self):
        t = Tank('player', 100, 200, UP)
        assert t.x == 100
        assert t.y == 200

    def test_direction(self):
        t = Tank('player', 0, 0, RIGHT)
        assert t.direction == RIGHT

    def test_kind(self):
        t = Tank('enemy', 0, 0, UP)
        assert t.kind == 'enemy'

    def test_alive_on_creation(self):
        t = Tank('player', 0, 0, UP)
        assert t.alive is True

    def test_shoot_cooldown_zero(self):
        t = Tank('player', 0, 0, UP)
        assert t.shoot_cooldown == 0

    def test_protection_zero(self):
        t = Tank('player', 0, 0, UP)
        assert t.protection == 0

    def test_not_moving_initially(self):
        t = Tank('player', 0, 0, UP)
        assert t.moving is False

    def test_image_set(self):
        t = Tank('player', 0, 0, UP)
        assert t.image == DIR_TANK_IMG['player'][UP]

    def test_enemy_image(self):
        t = Tank('enemy', 0, 0, DOWN)
        assert t.image == DIR_TANK_IMG['enemy'][DOWN]


class TestTankSetDirection:
    def test_change_direction(self):
        t = Tank('player', 100, 100, UP)
        t.set_direction(LEFT)
        assert t.direction == LEFT

    def test_same_direction_no_change(self):
        t = Tank('player', 100, 100, UP)
        old_x = t.x
        t.set_direction(UP)
        assert t.x == old_x

    def test_snaps_x_for_vertical(self):
        t = Tank('player', 110, 100, RIGHT)
        t.set_direction(UP)
        # x should be snapped to nearest tile center
        from map import snap_axis
        assert t.x == snap_axis(110)

    def test_snaps_y_for_horizontal(self):
        t = Tank('player', 100, 110, DOWN)
        t.set_direction(LEFT)
        from map import snap_axis
        assert t.y == snap_axis(110)

    def test_image_updates(self):
        t = Tank('player', 100, 100, UP)
        t.set_direction(RIGHT)
        assert t.image == DIR_TANK_IMG['player'][RIGHT]


class TestTankShoot:
    def test_shoot_creates_bullet(self):
        g = _make_game_with_empty_grid()
        g.start_game()
        g.bullets = []
        g.player.shoot_cooldown = 0
        g.player.shoot(g)
        assert len(g.bullets) == 1

    def test_cooldown_prevents_shoot(self):
        g = _make_game_with_empty_grid()
        g.start_game()
        g.bullets = []
        g.player.shoot_cooldown = 10
        g.player.shoot(g)
        assert len(g.bullets) == 0

    def test_player_one_bullet_limit(self):
        g = _make_game_with_empty_grid()
        g.start_game()
        g.bullets = []
        # Add an existing alive player bullet
        existing = Bullet(g.player.x, g.player.y, UP, 'player')
        existing.alive = True
        g.bullets.append(existing)
        g.player.shoot_cooldown = 0
        g.player.shoot(g)
        player_bullets = [b for b in g.bullets if b.owner == 'player' and b.alive]
        assert len(player_bullets) == 1

    def test_enemy_one_bullet_limit(self):
        """Enemy can only have one alive bullet on screen at a time."""
        g = _make_game_with_empty_grid()
        e = EnemyTank(200, 200)
        g.enemies = [e]
        g.bullets = []
        e.shoot_cooldown = 0
        e.shoot(g)
        assert len(g.bullets) == 1
        e.shoot_cooldown = 0
        e.shoot(g)
        # Second shoot blocked because first bullet still alive
        assert len(g.bullets) == 1


# ======================================================================
# PlayerTank
# ======================================================================
class TestPlayerTank:
    def test_initial_lives(self):
        p = PlayerTank(100, 100)
        assert p.lives == PLAYER_LIVES

    def test_kind_is_player(self):
        p = PlayerTank(100, 100)
        assert p.kind == 'player'

    def test_direction_is_up(self):
        p = PlayerTank(100, 100)
        assert p.direction == UP


# ======================================================================
# EnemyTank
# ======================================================================
class TestEnemyTank:
    def test_kind_is_enemy(self):
        e = EnemyTank(100, 100)
        assert e.kind == 'enemy'

    def test_direction_is_down(self):
        e = EnemyTank(100, 100)
        assert e.direction == DOWN

    def test_has_dir_timer(self):
        e = EnemyTank(100, 100)
        assert e.dir_timer > 0

    def test_initial_protection(self):
        e = EnemyTank(100, 100)
        assert e.protection == 30
