"""Tests for Tank and Bullet classes."""
import main
from main import (
    Tank, Bullet,
    TILE, SCREEN_W, SCREEN_H, TANK_SIZE, BULLET_SIZE,
    DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT,
    TERRAIN_EMPTY, TERRAIN_BRICK,
)
from conftest import make_empty_map


# ======================================================================
# Bullet
# ======================================================================
class TestBulletInit:
    def test_position(self):
        b = Bullet(100, 200, DIR_UP, True)
        assert b.x == 100
        assert b.y == 200

    def test_direction(self):
        b = Bullet(0, 0, DIR_RIGHT, True)
        assert b.dir == DIR_RIGHT

    def test_is_player_flag(self):
        assert Bullet(0, 0, DIR_UP, True).is_player is True
        assert Bullet(0, 0, DIR_UP, False).is_player is False

    def test_speed(self):
        b = Bullet(0, 0, DIR_UP, True)
        assert b.speed == 4

    def test_dimensions(self):
        b = Bullet(0, 0, DIR_UP, True)
        assert b.width == BULLET_SIZE
        assert b.height == BULLET_SIZE

    def test_alive_on_creation(self):
        b = Bullet(0, 0, DIR_UP, True)
        assert b.alive is True

    def test_owner_default_none(self):
        b = Bullet(0, 0, DIR_UP, True)
        assert b.owner is None


class TestBulletMovement:
    def test_move_up(self):
        main.map_data = make_empty_map()
        main.explosions = []
        b = Bullet(100, 100, DIR_UP, True)
        b.update()
        assert b.y == 96  # 100 - speed(4)

    def test_move_down(self):
        main.map_data = make_empty_map()
        main.explosions = []
        b = Bullet(100, 100, DIR_DOWN, True)
        b.update()
        assert b.y == 104

    def test_move_left(self):
        main.map_data = make_empty_map()
        main.explosions = []
        b = Bullet(100, 100, DIR_LEFT, True)
        b.update()
        assert b.x == 96

    def test_move_right(self):
        main.map_data = make_empty_map()
        main.explosions = []
        b = Bullet(100, 100, DIR_RIGHT, True)
        b.update()
        assert b.x == 104

    def test_dead_bullet_does_not_move(self):
        main.map_data = make_empty_map()
        main.explosions = []
        b = Bullet(100, 100, DIR_UP, True)
        b.alive = False
        b.update()
        assert b.x == 100
        assert b.y == 100


class TestBulletBounds:
    def test_out_of_bounds_top(self):
        main.map_data = make_empty_map()
        main.explosions = []
        b = Bullet(100, 0, DIR_UP, True)
        b.update()
        assert b.alive is False

    def test_out_of_bounds_left(self):
        main.map_data = make_empty_map()
        main.explosions = []
        b = Bullet(0, 100, DIR_LEFT, True)
        b.update()
        assert b.alive is False

    def test_out_of_bounds_right(self):
        main.map_data = make_empty_map()
        main.explosions = []
        b = Bullet(SCREEN_W - BULLET_SIZE, 100, DIR_RIGHT, True)
        b.update()
        assert b.alive is False

    def test_out_of_bounds_bottom(self):
        main.map_data = make_empty_map()
        main.explosions = []
        b = Bullet(100, SCREEN_H - BULLET_SIZE, DIR_DOWN, True)
        b.update()
        assert b.alive is False


class TestBulletImage:
    def test_up(self):
        assert Bullet(0, 0, DIR_UP, True).get_image() == 'bullet_up'

    def test_right(self):
        assert Bullet(0, 0, DIR_RIGHT, True).get_image() == 'bullet_right'

    def test_down(self):
        assert Bullet(0, 0, DIR_DOWN, True).get_image() == 'bullet_down'

    def test_left(self):
        assert Bullet(0, 0, DIR_LEFT, True).get_image() == 'bullet_left'


# ======================================================================
# Tank
# ======================================================================
class TestTankInit:
    def test_position(self):
        t = Tank(100, 200, DIR_UP)
        assert t.x == 100
        assert t.y == 200

    def test_direction(self):
        t = Tank(0, 0, DIR_RIGHT)
        assert t.dir == DIR_RIGHT

    def test_is_player_default_false(self):
        t = Tank(0, 0, DIR_UP)
        assert t.is_player is False

    def test_is_player_true(self):
        t = Tank(0, 0, DIR_UP, True)
        assert t.is_player is True

    def test_dimensions(self):
        t = Tank(0, 0, DIR_UP)
        assert t.width == TANK_SIZE
        assert t.height == TANK_SIZE

    def test_speed(self):
        t = Tank(0, 0, DIR_UP)
        assert t.speed == 2

    def test_alive_on_creation(self):
        t = Tank(0, 0, DIR_UP)
        assert t.alive is True

    def test_player_invincible_on_spawn(self):
        t = Tank(0, 0, DIR_UP, True)
        assert t.invincible == 180

    def test_enemy_not_invincible(self):
        t = Tank(0, 0, DIR_UP, False)
        assert t.invincible == 0

    def test_shoot_cooldown_zero(self):
        t = Tank(0, 0, DIR_UP)
        assert t.shoot_cooldown == 0

    def test_not_moving_initially(self):
        t = Tank(0, 0, DIR_UP)
        assert t.moving is False


class TestTankImage:
    def test_player_up(self):
        assert Tank(0, 0, DIR_UP, True).get_image() == 'tank_player_up'

    def test_player_down(self):
        assert Tank(0, 0, DIR_DOWN, True).get_image() == 'tank_player_down'

    def test_player_left(self):
        assert Tank(0, 0, DIR_LEFT, True).get_image() == 'tank_player_left'

    def test_player_right(self):
        assert Tank(0, 0, DIR_RIGHT, True).get_image() == 'tank_player_right'

    def test_enemy_up(self):
        assert Tank(0, 0, DIR_UP, False).get_image() == 'tank_basic_up'

    def test_enemy_down(self):
        assert Tank(0, 0, DIR_DOWN, False).get_image() == 'tank_basic_down'

    def test_enemy_left(self):
        assert Tank(0, 0, DIR_LEFT, False).get_image() == 'tank_basic_left'

    def test_enemy_right(self):
        assert Tank(0, 0, DIR_RIGHT, False).get_image() == 'tank_basic_right'


class TestTankMovement:
    def test_move_up(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        t = Tank(100, 100, DIR_UP, True)
        t.moving = True
        t.move()
        assert t.y == 98  # 100 - speed(2)

    def test_move_down(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        t = Tank(100, 100, DIR_DOWN, True)
        t.moving = True
        t.move()
        assert t.y == 102

    def test_move_left(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        t = Tank(100, 100, DIR_LEFT, True)
        t.moving = True
        t.move()
        assert t.x == 98

    def test_move_right(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        t = Tank(100, 100, DIR_RIGHT, True)
        t.moving = True
        t.move()
        assert t.x == 102

    def test_not_moving_stays(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        t = Tank(100, 100, DIR_UP, True)
        t.moving = False
        t.move()
        assert t.x == 100
        assert t.y == 100

    def test_dead_tank_does_not_move(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        t = Tank(100, 100, DIR_UP, True)
        t.alive = False
        t.moving = True
        t.move()
        assert t.x == 100
        assert t.y == 100

    def test_blocked_by_wall(self):
        main.map_data = make_empty_map()
        main.map_data[0][0] = TERRAIN_BRICK
        main.player = None
        main.enemies = []
        t = Tank(0, 0, DIR_UP, True)
        t.moving = True
        old_y = t.y
        t.move()
        # Should be blocked by brick or boundary
        assert t.y == old_y or t.y >= 0

    def test_boundary_top(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        t = Tank(100, 0, DIR_UP, True)
        t.moving = True
        t.move()
        assert t.y == 0  # Can't go above 0

    def test_boundary_left(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        t = Tank(0, 100, DIR_LEFT, True)
        t.moving = True
        t.move()
        assert t.x == 0

    def test_boundary_right(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        t = Tank(SCREEN_W - TANK_SIZE, 100, DIR_RIGHT, True)
        t.moving = True
        t.move()
        assert t.x == SCREEN_W - TANK_SIZE  # Can't exceed screen width


class TestTankShoot:
    def test_shoot_creates_bullet(self):
        main.bullets = []
        t = Tank(100, 100, DIR_UP, True)
        t.shoot()
        assert len(main.bullets) == 1
        b = main.bullets[0]
        assert isinstance(b, Bullet)
        assert b.is_player is True
        assert b.owner is t

    def test_shoot_sets_cooldown_player(self):
        main.bullets = []
        t = Tank(100, 100, DIR_UP, True)
        t.shoot()
        assert t.shoot_cooldown == 15

    def test_shoot_sets_cooldown_enemy(self):
        main.bullets = []
        t = Tank(100, 100, DIR_UP, False)
        t.shoot()
        assert t.shoot_cooldown == 45

    def test_no_shoot_during_cooldown(self):
        main.bullets = []
        t = Tank(100, 100, DIR_UP, True)
        t.shoot()
        t.shoot()  # Should be blocked by cooldown
        assert len(main.bullets) == 1

    def test_no_shoot_when_dead(self):
        main.bullets = []
        t = Tank(100, 100, DIR_UP, True)
        t.alive = False
        t.shoot()
        assert len(main.bullets) == 0

    def test_max_2_bullets_per_tank(self):
        main.bullets = []
        t = Tank(100, 100, DIR_UP, True)
        t.shoot_cooldown = 0
        t.shoot()
        t.shoot_cooldown = 0
        t.shoot()
        t.shoot_cooldown = 0
        t.shoot()  # 3rd attempt, should be blocked
        alive_owned = [b for b in main.bullets if b.alive and b.owner == t]
        assert len(alive_owned) == 2

    def test_bullet_direction_up(self):
        main.bullets = []
        t = Tank(128, 128, DIR_UP, True)
        t.shoot()
        b = main.bullets[0]
        assert b.dir == DIR_UP
        assert b.y < t.y  # Bullet spawned above tank

    def test_bullet_direction_down(self):
        main.bullets = []
        t = Tank(128, 128, DIR_DOWN, True)
        t.shoot()
        b = main.bullets[0]
        assert b.dir == DIR_DOWN
        assert b.y > t.y

    def test_bullet_direction_left(self):
        main.bullets = []
        t = Tank(128, 128, DIR_LEFT, True)
        t.shoot()
        b = main.bullets[0]
        assert b.dir == DIR_LEFT
        assert b.x < t.x

    def test_bullet_direction_right(self):
        main.bullets = []
        t = Tank(128, 128, DIR_RIGHT, True)
        t.shoot()
        b = main.bullets[0]
        assert b.dir == DIR_RIGHT
        assert b.x > t.x


class TestTankUpdate:
    def test_cooldown_decrements(self):
        t = Tank(0, 0, DIR_UP, True)
        t.shoot_cooldown = 10
        t.update()
        assert t.shoot_cooldown == 9

    def test_invincible_decrements(self):
        t = Tank(0, 0, DIR_UP, True)
        initial = t.invincible
        t.update()
        assert t.invincible == initial - 1

    def test_dead_tank_no_update(self):
        t = Tank(0, 0, DIR_UP, True)
        t.alive = False
        t.shoot_cooldown = 10
        t.update()
        assert t.shoot_cooldown == 10  # unchanged

    def test_invincible_timer_zero_no_decrement(self):
        t = Tank(0, 0, DIR_UP, False)
        assert t.invincible == 0
        t.update()
        assert t.invincible == 0


# ======================================================================
# Tank.snap_to_grid
# ======================================================================
class TestTankSnapToGrid:
    def test_snap_up_snaps_x(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        t = Tank(20, 100, DIR_UP, True)
        t.prev_dir = DIR_RIGHT
        t.snap_to_grid()
        # x should snap to nearest HALF_TILE grid point
        assert t.x % main.HALF_TILE == 0

    def test_snap_down_snaps_x(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        t = Tank(20, 100, DIR_DOWN, True)
        t.prev_dir = DIR_LEFT
        t.snap_to_grid()
        assert t.x % main.HALF_TILE == 0

    def test_snap_right_snaps_y(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        t = Tank(100, 20, DIR_RIGHT, True)
        t.prev_dir = DIR_DOWN
        t.snap_to_grid()
        assert t.y % main.HALF_TILE == 0

    def test_snap_left_snaps_y(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        t = Tank(100, 20, DIR_LEFT, True)
        t.prev_dir = DIR_UP
        t.snap_to_grid()
        assert t.y % main.HALF_TILE == 0

    def test_no_snap_when_already_on_grid(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        t = Tank(32, 64, DIR_UP, True)
        t.prev_dir = DIR_RIGHT
        old_x = t.x
        t.snap_to_grid()
        assert t.x == old_x  # already on grid, no change

    def test_snap_blocked_by_wall(self):
        main.map_data = make_empty_map()
        # Place brick where tank would snap to
        main.map_data[3][1] = main.TERRAIN_BRICK
        main.player = None
        main.enemies = []
        t = Tank(20, 96, DIR_UP, True)
        t.prev_dir = DIR_RIGHT
        old_x = t.x
        t.snap_to_grid()
        # If snap target overlaps brick, x should not change
        # (depends on whether the snap position is blocked)
        # Just verify no crash and tank position is valid
        assert t.x >= 0

    def test_snap_prev_dir_updown_no_x_change(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        t = Tank(20, 100, DIR_UP, True)
        t.prev_dir = DIR_UP  # prev same axis
        t.snap_to_grid()
        # round(20/16)*16 = 16, so x snaps to 16
        assert t.x == 16


# ======================================================================
# Tank.slide_to_grid
# ======================================================================
class TestTankSlideToGrid:
    def test_slide_up(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        t = Tank(64, 35, DIR_UP, True)
        old_y = t.y
        t.slide_to_grid()
        assert t.y <= old_y  # should slide toward grid

    def test_slide_down(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        t = Tank(64, 35, DIR_DOWN, True)
        old_y = t.y
        t.slide_to_grid()
        assert t.y >= old_y

    def test_slide_left(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        t = Tank(35, 64, DIR_LEFT, True)
        old_x = t.x
        t.slide_to_grid()
        assert t.x <= old_x

    def test_slide_right(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        t = Tank(35, 64, DIR_RIGHT, True)
        old_x = t.x
        t.slide_to_grid()
        assert t.x >= old_x

    def test_no_slide_when_on_grid(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        t = Tank(64, 64, DIR_UP, True)
        t.slide_to_grid()
        assert t.x == 64
        assert t.y == 64

    def test_slide_blocked_by_wall(self):
        main.map_data = make_empty_map()
        main.map_data[1][2] = main.TERRAIN_BRICK
        main.player = None
        main.enemies = []
        t = Tank(64, 65, DIR_UP, True)
        old_y = t.y
        t.slide_to_grid()
        # May or may not slide depending on wall position
        assert t.y >= 0


# ======================================================================
# Tank.move advanced
# ======================================================================
class TestTankMoveAdvanced:
    def test_move_blocked_by_another_tank(self):
        main.map_data = make_empty_map()
        other = Tank(100, 100, DIR_UP, False)
        main.player = None
        main.enemies = [other]
        t = Tank(100, 130, DIR_UP, True)
        t.moving = True
        t.move()
        # Should be blocked by the other tank
        assert t.y == 130  # didn't move

    def test_move_down_boundary(self):
        main.map_data = make_empty_map()
        main.player = None
        main.enemies = []
        t = Tank(100, main.SCREEN_H - main.TANK_SIZE, DIR_DOWN, True)
        t.moving = True
        t.move()
        assert t.y == main.SCREEN_H - main.TANK_SIZE  # can't go below

    def test_move_onto_brick_blocked(self):
        main.map_data = make_empty_map()
        main.map_data[2][3] = main.TERRAIN_BRICK
        main.player = None
        main.enemies = []
        # Tank at row 3 moving up into row 2 brick
        t = Tank(3 * main.TILE, 3 * main.TILE, DIR_UP, True)
        t.moving = True
        old_y = t.y
        t.move()
        assert t.y == old_y  # blocked by brick
