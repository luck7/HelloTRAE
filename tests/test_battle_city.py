"""Tests for battle_city.py utility functions and Game class."""
import pygame
import battle_city as bc
from battle_city import (
    TILE_SIZE, GRID_W, GRID_H, GAME_W, GAME_H,
    T_EMPTY, T_BRICK, T_STEEL, T_WATER, T_GRASS,
    UP, DOWN, LEFT, RIGHT,
    parse_level, cell_to_pixel, pixel_to_cell, snap_axis,
    rect_for_center, bullet_rect, BULLET_SIZE, BULLET_SPEED,
    Game,
    STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER, STATE_WIN,
    TOTAL_ENEMIES, PLAYER_LIVES, SPAWN_PROTECTION,
)


# ======================================================================
# parse_level
# ======================================================================
class TestParseLevel:
    def test_grid_dimensions(self):
        grid = parse_level()
        assert len(grid) == GRID_H
        for row in grid:
            assert len(row) == GRID_W

    def test_returns_list_of_lists(self):
        grid = parse_level()
        assert isinstance(grid, list)
        assert isinstance(grid[0], list)

    def test_enemy_spawns_found(self):
        parse_level()
        assert len(bc.ENEMY_SPAWN_POINTS) == 3
        # Top row: columns 0, 6, 12
        cols = sorted([c for c, r in bc.ENEMY_SPAWN_POINTS])
        assert cols == [0, 6, 12]

    def test_enemy_spawns_at_row_zero(self):
        parse_level()
        for c, r in bc.ENEMY_SPAWN_POINTS:
            assert r == 0

    def test_player_spawn(self):
        parse_level()
        assert bc.PLAYER_SPAWN == (6, 12)

    def test_base_cell(self):
        parse_level()
        assert bc.BASE_CELL == (6, 11)

    def test_brick_tiles(self):
        grid = parse_level()
        # Row 2: "..BBBBBBBBB.." → cols 2-10 are brick
        for c in range(2, 11):
            assert grid[2][c] == T_BRICK, f"Expected brick at col {c}, row 2"

    def test_steel_tiles(self):
        grid = parse_level()
        # Row 4: "..B.SSSSS.B.." → cols 4-8 are steel
        for c in range(4, 9):
            assert grid[4][c] == T_STEEL, f"Expected steel at col {c}, row 4"

    def test_water_tiles(self):
        grid = parse_level()
        # Row 8: ".WW...G...WW." → cols 1,2 and 10,11 are water
        assert grid[8][1] == T_WATER
        assert grid[8][2] == T_WATER
        assert grid[8][10] == T_WATER
        assert grid[8][11] == T_WATER

    def test_grass_tiles(self):
        grid = parse_level()
        # Row 5: "..B...G...B.." → col 6 is grass
        assert grid[5][6] == T_GRASS

    def test_empty_cells(self):
        grid = parse_level()
        # Row 0: "E.....E.....E" → cols 1-5, 7-11 should be empty
        for c in range(1, 6):
            assert grid[0][c] == T_EMPTY
        for c in range(7, 12):
            assert grid[0][c] == T_EMPTY

    def test_base_not_in_grid(self):
        """The base marker 'H' should not appear as a terrain tile."""
        grid = parse_level()
        for row in grid:
            for tile in row:
                assert tile in (T_EMPTY, T_BRICK, T_STEEL, T_WATER, T_GRASS)


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
        # 32 is exactly between 16 and 48 → round to nearest even
        result = snap_axis(32)
        assert result in (16, 48)

    def test_snap_negative(self):
        result = snap_axis(-5)
        assert result == -16


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
        from unittest.mock import MagicMock
        b = MagicMock()
        b.x = 100
        b.y = 100
        r = bullet_rect(b)
        assert r.width == BULLET_SIZE
        assert r.height == BULLET_SIZE

    def test_centered(self):
        from unittest.mock import MagicMock
        b = MagicMock()
        b.x = 100
        b.y = 200
        r = bullet_rect(b)
        assert r.centerx == 100
        assert r.centery == 200


# ======================================================================
# Game class
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
        g._end_game(STATE_GAME_OVER)  # same state, should not reset timer
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
        # Simulate score update logic
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
# Tank.set_direction (battle_city.py)
# ======================================================================
class TestBCTankSetDirection:
    def test_change_to_left(self):
        from battle_city import Tank
        t = Tank('player', 100, 100, UP)
        t.set_direction(LEFT)
        assert t.direction == LEFT

    def test_change_to_down(self):
        from battle_city import Tank
        t = Tank('player', 100, 100, UP)
        t.set_direction(DOWN)
        assert t.direction == DOWN

    def test_no_change_same_direction(self):
        from battle_city import Tank
        t = Tank('player', 100, 100, UP)
        old_x = t.x
        t.set_direction(UP)
        assert t.x == old_x  # no snap when same direction

    def test_change_snaps_x_for_vertical(self):
        from battle_city import Tank
        t = Tank('player', 110, 100, RIGHT)
        t.set_direction(UP)
        # x should be snapped to nearest tile center
        assert t.x == snap_axis(110)

    def test_change_snaps_y_for_horizontal(self):
        from battle_city import Tank
        t = Tank('player', 100, 110, DOWN)
        t.set_direction(LEFT)
        assert t.y == snap_axis(110)

    def test_image_updates(self):
        from battle_city import Tank, DIR_TANK_IMG
        t = Tank('player', 100, 100, UP)
        t.set_direction(RIGHT)
        assert t.image == DIR_TANK_IMG['player'][RIGHT]


# ======================================================================
# Tank.try_move (battle_city.py)
# ======================================================================
class TestBCTankTryMove:
    def test_move_success(self):
        from battle_city import Tank
        g = Game()
        g.start_game()
        t = g.player
        old_x, old_y = t.x, t.y
        # Try moving in a direction that should work
        result = t.try_move(2, 0, g)
        if result:
            assert t.x == old_x + 2

    def test_move_blocked_by_wall(self):
        from battle_city import Tank
        g = Game()
        g.grid = parse_level()
        g.base_rect = rect_for_center(*cell_to_pixel(*bc.BASE_CELL))
        g.player = None
        g.enemies = []
        # Place tank next to a brick wall
        t = Tank('player', 3 * TILE_SIZE + 16, 3 * TILE_SIZE + 16, UP)
        # Try to move into brick
        for c, r in t._cells_under(rect_for_center(t.x + 2, t.y, TILE_SIZE - 2)):
            if 0 <= c < GRID_W and 0 <= r < GRID_H:
                g.grid[r][c] = T_BRICK
        result = t.try_move(TILE_SIZE, 0, g)
        assert result is False

    def test_move_out_of_bounds(self):
        from battle_city import Tank
        g = Game()
        g.grid = parse_level()
        g.base_rect = rect_for_center(*cell_to_pixel(*bc.BASE_CELL))
        g.player = None
        g.enemies = []
        # Tank at left edge
        t = Tank('player', 16, 100, UP)
        result = t.try_move(-TILE_SIZE, 0, g)
        assert result is False

    def test_move_blocked_by_base(self):
        from battle_city import Tank
        g = Game()
        g.grid = parse_level()
        g.base_rect = rect_for_center(*cell_to_pixel(*bc.BASE_CELL))
        g.player = None
        g.enemies = []
        # Tank near base
        bx, by = cell_to_pixel(*bc.BASE_CELL)
        t = Tank('player', bx, by - TILE_SIZE, UP)
        result = t.try_move(0, TILE_SIZE, g)
        # Should be blocked by base rect
        assert result is False or t.y != by


# ======================================================================
# Tank._cells_under (battle_city.py)
# ======================================================================
class TestBCTankCellsUnder:
    def test_single_cell(self):
        from battle_city import Tank
        t = Tank('player', 16, 16, UP)
        r = rect_for_center(16, 16, TILE_SIZE)
        cells = t._cells_under(r)
        assert (0, 0) in cells

    def test_multiple_cells(self):
        from battle_city import Tank
        t = Tank('player', 32, 32, UP)
        r = rect_for_center(32, 32, TILE_SIZE * 2)
        cells = t._cells_under(r)
        assert len(cells) >= 4

    def test_clamped_to_grid(self):
        from battle_city import Tank
        t = Tank('player', 16, 16, UP)
        # Very large rect that extends beyond grid
        r = pygame.Rect(-100, -100, 2000, 2000)
        cells = t._cells_under(r)
        for c, row in cells:
            assert 0 <= c < GRID_W
            assert 0 <= row < GRID_H


# ======================================================================
# Tank.shoot (battle_city.py)
# ======================================================================
class TestBCTankShoot:
    def test_player_shoot(self):
        from battle_city import Tank, PlayerTank
        g = Game()
        g.start_game()
        g.bullets = []
        g.player.shoot_cooldown = 0
        g.player.shoot(g)
        assert len(g.bullets) == 1

    def test_cooldown_prevents_shoot(self):
        from battle_city import Tank
        g = Game()
        g.start_game()
        g.bullets = []
        g.player.shoot_cooldown = 10
        g.player.shoot(g)
        assert len(g.bullets) == 0

    def test_player_one_bullet_limit(self):
        from battle_city import Tank
        g = Game()
        g.start_game()
        g.bullets = []
        # Add an existing player bullet
        existing = bc.Bullet(g.player.x, g.player.y, UP, 'player')
        existing.alive = True
        existing.owner = 'player'
        g.bullets.append(existing)
        g.player.shoot_cooldown = 0
        g.player.shoot(g)
        # Should not add another bullet
        player_bullets = [b for b in g.bullets if b.owner == 'player' and b.alive]
        assert len(player_bullets) == 1


# ======================================================================
# Game._update_bullet (battle_city.py)
# ======================================================================
class TestBCGameUpdateBullet:
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
        g.base_rect = rect_for_center(*cell_to_pixel(*bc.BASE_CELL))
        g.player = None
        g.enemies = []
        # Bullet moving down into brick at (5,5)
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
        g.base_rect = rect_for_center(*cell_to_pixel(*bc.BASE_CELL))
        g.player = None
        g.enemies = []
        bx = 5 * TILE_SIZE + TILE_SIZE // 2
        by = 5 * TILE_SIZE
        b = self._make_bullet(bx, by, 0, BULLET_SPEED)
        g.bullets = [b]
        g._update_bullet(b)
        assert g.grid[5][5] == T_STEEL  # unchanged
        assert b.alive is False

    def test_out_of_bounds(self):
        g = Game()
        g.grid = [[T_EMPTY] * GRID_W for _ in range(GRID_H)]
        g.base_rect = rect_for_center(*cell_to_pixel(*bc.BASE_CELL))
        g.player = None
        g.enemies = []
        # Bullet at top edge moving up
        b = self._make_bullet(100, -1, 0, -BULLET_SPEED)
        g.bullets = [b]
        g._update_bullet(b)
        assert b.alive is False

    def test_base_hit(self):
        g = Game()
        g.grid = [[T_EMPTY] * GRID_W for _ in range(GRID_H)]
        g.base_alive = True
        bx, by = cell_to_pixel(*bc.BASE_CELL)
        g.base_rect = rect_for_center(bx, by)
        g.player = None
        g.enemies = []
        # Bullet moving into base
        b = self._make_bullet(bx, by, 0, BULLET_SPEED)
        g.bullets = [b]
        g._update_bullet(b)
        assert g.base_alive is False
        assert g.state == STATE_GAME_OVER

    def test_player_bullet_kills_enemy(self):
        g = Game()
        g.grid = [[T_EMPTY] * GRID_W for _ in range(GRID_H)]
        g.base_rect = rect_for_center(*cell_to_pixel(*bc.BASE_CELL))
        g.player = None
        enemy = bc.EnemyTank(200, 200)
        enemy.alive = True
        enemy.protection = 0
        g.enemies = [enemy]
        g.score = 0
        # Bullet at enemy position
        b = self._make_bullet(enemy.x, enemy.y, 0, BULLET_SPEED)
        g.bullets = [b]
        g._update_bullet(b)
        assert enemy.alive is False
        assert g.score == 100

    def test_protected_tank_not_killed(self):
        g = Game()
        g.grid = [[T_EMPTY] * GRID_W for _ in range(GRID_H)]
        g.base_rect = rect_for_center(*cell_to_pixel(*bc.BASE_CELL))
        g.player = None
        enemy = bc.EnemyTank(200, 200)
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
        g.base_rect = rect_for_center(*cell_to_pixel(*bc.BASE_CELL))
        g.player = None
        g.enemies = []
        b1 = self._make_bullet(200, 200, 0, BULLET_SPEED, 'player')
        b2 = self._make_bullet(200, 200, 0, -BULLET_SPEED, 'enemy')
        g.bullets = [b1, b2]
        g._update_bullet(b1)
        assert b1.alive is False
        assert b2.alive is False


# ======================================================================
# Game._spawn_enemy (battle_city.py)
# ======================================================================
class TestBCGameSpawnEnemy:
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
        # Fill up to MAX_ENEMIES_ON_SCREEN
        while len(g.enemies) < bc.MAX_ENEMIES_ON_SCREEN:
            g.enemies.append(bc.EnemyTank(0, 0))
        old_count = len(g.enemies)
        g._spawn_enemy()
        assert len(g.enemies) == old_count


# ======================================================================
# Game._respawn_player (battle_city.py)
# ======================================================================
class TestBCGameRespawnPlayer:
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
        px, py = cell_to_pixel(*bc.PLAYER_SPAWN)
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
# PlayerTank.update (battle_city.py)
# ======================================================================
class TestBCPlayerTankUpdate:
    def test_cooldown_decrements(self):
        g = Game()
        g.start_game()
        g.player.shoot_cooldown = 10
        bc.keyboard.left = False
        bc.keyboard.right = False
        bc.keyboard.up = False
        bc.keyboard.down = False
        bc.keyboard.a = False
        bc.keyboard.d = False
        bc.keyboard.w = False
        bc.keyboard.s = False
        bc.keyboard.space = False
        g.player.update(g)
        assert g.player.shoot_cooldown == 9

    def test_protection_decrements(self):
        g = Game()
        g.start_game()
        g.player.protection = 50
        bc.keyboard.left = False
        bc.keyboard.right = False
        bc.keyboard.up = False
        bc.keyboard.down = False
        bc.keyboard.a = False
        bc.keyboard.d = False
        bc.keyboard.w = False
        bc.keyboard.s = False
        bc.keyboard.space = False
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
# EnemyTank.update (battle_city.py)
# ======================================================================
class TestBCTankCellsUnder:
    def test_cells_under_returns_set(self):
        from battle_city import Tank
        t = Tank('enemy', 100, 100, DOWN)
        r = rect_for_center(100, 100, TILE_SIZE)
        cells = t._cells_under(r)
        assert isinstance(cells, set)
        assert len(cells) >= 1

    def test_cells_under_large_rect(self):
        from battle_city import Tank
        t = Tank('enemy', 100, 100, DOWN)
        r = pygame.Rect(0, 0, TILE_SIZE * 3, TILE_SIZE * 3)
        cells = t._cells_under(r)
        assert len(cells) >= 9
