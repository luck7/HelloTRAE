"""Tests for game state management and collision handling functions."""
import main
from main import (
    game_over, reset_game, reset_stage, stage_complete, spawn_enemy,
    handle_bullet_map_collision, handle_bullet_tank_collision,
    handle_bullet_bullet_collision,
    Tank, Bullet, Explosion,
    TILE, MAP_W, MAP_H, TANK_SIZE, BULLET_SIZE,
    TERRAIN_EMPTY, TERRAIN_BRICK, TERRAIN_STEEL,
    BASE_COL, BASE_ROW,
    DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT,
)
from conftest import make_empty_map


# ======================================================================
# game_over
# ======================================================================
class TestGameOver:
    def test_sets_gameover_state(self):
        main.game_state = 'playing'
        game_over('test')
        assert main.game_state == 'gameover'

    def test_from_any_state(self):
        for state in ['menu', 'playing', 'stageTransition']:
            main.game_state = state
            game_over('test')
            assert main.game_state == 'gameover'


# ======================================================================
# reset_game
# ======================================================================
class TestResetGame:
    def test_resets_score(self):
        main.score = 500
        reset_game()
        assert main.score == 0

    def test_resets_lives(self):
        main.lives = 0
        reset_game()
        assert main.lives == 3

    def test_resets_stage(self):
        main.stage = 5
        reset_game()
        assert main.stage == 1

    def test_resets_gameover_delay(self):
        main.gameover_delay = 100
        reset_game()
        assert main.gameover_delay == 0

    def test_creates_player(self):
        main.player = None
        reset_game()
        assert main.player is not None
        assert main.player.is_player is True
        assert main.player.alive is True

    def test_clears_enemies(self):
        main.enemies = [Tank(0, 0, DIR_DOWN)]
        reset_game()
        assert main.enemies == []

    def test_clears_bullets(self):
        main.bullets = [Bullet(0, 0, DIR_UP, True)]
        reset_game()
        assert main.bullets == []

    def test_clears_explosions(self):
        main.explosions = ['fake']
        reset_game()
        assert main.explosions == []

    def test_resets_spawned_enemies(self):
        main.spawned_enemies = 10
        reset_game()
        assert main.spawned_enemies == 0

    def test_resets_base_alive(self):
        main.base_alive = False
        reset_game()
        assert main.base_alive is True

    def test_initializes_map(self):
        main.stage = 1
        reset_game()
        assert len(main.map_data) == MAP_H
        for y in range(MAP_H):
            assert main.map_data[y] == main.STAGE_MAP[y]

    def test_total_enemies_stage_1(self):
        reset_game()
        # total_enemies = 8 + stage * 2 = 8 + 1 * 2 = 10
        assert main.total_enemies == 10


# ======================================================================
# reset_stage
# ======================================================================
class TestResetStage:
    def test_creates_player(self):
        reset_stage()
        assert main.player is not None
        assert main.player.x == 4 * TILE
        assert main.player.y == 12 * TILE

    def test_clears_enemies(self):
        main.enemies = [Tank(0, 0, DIR_DOWN)]
        reset_stage()
        assert main.enemies == []

    def test_clears_bullets(self):
        main.bullets = [Bullet(0, 0, DIR_UP, True)]
        reset_stage()
        assert main.bullets == []

    def test_resets_base(self):
        main.base_alive = False
        reset_stage()
        assert main.base_alive is True

    def test_resets_spawned_enemies(self):
        main.spawned_enemies = 10
        reset_stage()
        assert main.spawned_enemies == 0

    def test_total_enemies_scales_with_stage(self):
        main.stage = 3
        reset_stage()
        assert main.total_enemies == 8 + 3 * 2  # 14


# ======================================================================
# stage_complete
# ======================================================================
class TestStageComplete:
    def test_sets_transition_state(self):
        main.game_state = 'playing'
        stage_complete()
        assert main.game_state == 'stageTransition'

    def test_increments_stage(self):
        main.stage = 1
        stage_complete()
        assert main.stage == 2

    def test_sets_transition_timer(self):
        stage_complete()
        assert main.stage_transition_timer == 120


# ======================================================================
# spawn_enemy
# ======================================================================
class TestSpawnEnemy:
    def test_spawn_increments_count(self):
        main.total_enemies = 20
        main.spawned_enemies = 0
        main.enemies = []
        spawn_enemy()
        assert main.spawned_enemies == 1

    def test_spawn_creates_tank(self):
        main.total_enemies = 20
        main.spawned_enemies = 0
        main.enemies = []
        spawn_enemy()
        assert len(main.enemies) == 1
        assert main.enemies[0].is_player is False

    def test_no_spawn_at_limit(self):
        main.total_enemies = 5
        main.spawned_enemies = 5
        old_count = len(main.enemies)
        spawn_enemy()
        assert main.spawned_enemies == 5
        assert len(main.enemies) == old_count

    def test_spawn_at_row_zero(self):
        main.total_enemies = 20
        main.spawned_enemies = 0
        main.enemies = []
        spawn_enemy()
        assert main.enemies[0].y == 0

    def test_multiple_spawns(self):
        main.total_enemies = 20
        main.spawned_enemies = 0
        main.enemies = []
        # Spawn points may be occupied, so spawn count <= 3
        for _ in range(5):
            spawn_enemy()
        assert main.spawned_enemies >= 1
        assert main.spawned_enemies <= 3


# ======================================================================
# handle_bullet_map_collision
# ======================================================================
class TestHandleBulletMapCollision:
    def test_brick_destroyed(self):
        main.map_data = make_empty_map()
        main.map_data[0][0] = TERRAIN_BRICK
        main.explosions = []
        b = Bullet(0, 0, DIR_DOWN, True)
        result = handle_bullet_map_collision(b)
        assert result is True
        assert main.map_data[0][0] == TERRAIN_EMPTY
        assert b.alive is False

    def test_steel_not_destroyed(self):
        main.map_data = make_empty_map()
        main.map_data[0][0] = TERRAIN_STEEL
        main.explosions = []
        b = Bullet(0, 0, DIR_DOWN, True)
        result = handle_bullet_map_collision(b)
        assert result is True
        assert main.map_data[0][0] == TERRAIN_STEEL  # unchanged
        assert b.alive is False

    def test_empty_map_no_collision(self):
        main.map_data = make_empty_map()
        main.explosions = []
        b = Bullet(5 * TILE + 8, 5 * TILE + 8, DIR_DOWN, True)
        result = handle_bullet_map_collision(b)
        assert result is False

    def test_base_hit(self):
        main.map_data = make_empty_map()
        main.explosions = []
        main.base_alive = True
        base_x = BASE_COL * TILE + 8
        base_y = BASE_ROW * TILE + 8
        b = Bullet(base_x, base_y, DIR_DOWN, True)
        result = handle_bullet_map_collision(b)
        assert result is True
        assert main.base_alive is False
        assert b.alive is False

    def test_base_already_destroyed_no_double_set(self):
        main.map_data = make_empty_map()
        main.explosions = []
        main.base_alive = False
        main.gameover_delay = 0
        base_x = BASE_COL * TILE + 8
        base_y = BASE_ROW * TILE + 8
        b = Bullet(base_x, base_y, DIR_DOWN, True)
        handle_bullet_map_collision(b)
        # gameover_delay should not be reset since base was already dead
        assert main.gameover_delay == 0

    def test_creates_explosion_on_brick(self):
        main.map_data = make_empty_map()
        main.map_data[0][0] = TERRAIN_BRICK
        main.explosions = []
        b = Bullet(0, 0, DIR_DOWN, True)
        handle_bullet_map_collision(b)
        assert len(main.explosions) > 0

    def test_creates_explosion_on_steel(self):
        main.map_data = make_empty_map()
        main.map_data[0][0] = TERRAIN_STEEL
        main.explosions = []
        b = Bullet(0, 0, DIR_DOWN, True)
        handle_bullet_map_collision(b)
        assert len(main.explosions) > 0


# ======================================================================
# handle_bullet_tank_collision
# ======================================================================
class TestHandleBulletTankCollision:
    def test_player_bullet_kills_enemy(self):
        main.explosions = []
        enemy = Tank(100, 100, DIR_DOWN, False)
        main.enemies = [enemy]
        main.player = None
        b = Bullet(100, 100, DIR_UP, True)
        b.width = BULLET_SIZE
        b.height = BULLET_SIZE
        handle_bullet_tank_collision(b)
        assert enemy.alive is False
        assert b.alive is False

    def test_player_bullet_awards_score(self):
        main.explosions = []
        main.score = 0
        enemy = Tank(100, 100, DIR_DOWN, False)
        main.enemies = [enemy]
        main.player = None
        b = Bullet(100, 100, DIR_UP, True)
        b.width = BULLET_SIZE
        b.height = BULLET_SIZE
        handle_bullet_tank_collision(b)
        assert main.score == 100

    def test_enemy_bullet_kills_player(self):
        main.explosions = []
        main.player = Tank(100, 100, DIR_UP, True)
        main.player.invincible = 0
        main.enemies = []
        b = Bullet(100, 100, DIR_DOWN, False)
        b.width = BULLET_SIZE
        b.height = BULLET_SIZE
        handle_bullet_tank_collision(b)
        assert main.player.alive is False
        assert b.alive is False

    def test_enemy_bullet_reduces_lives(self):
        main.explosions = []
        main.lives = 3
        main.player = Tank(100, 100, DIR_UP, True)
        main.player.invincible = 0
        main.enemies = []
        b = Bullet(100, 100, DIR_DOWN, False)
        b.width = BULLET_SIZE
        b.height = BULLET_SIZE
        handle_bullet_tank_collision(b)
        assert main.lives == 2

    def test_invincible_player_not_killed(self):
        main.explosions = []
        main.player = Tank(100, 100, DIR_UP, True)
        main.player.invincible = 100
        main.enemies = []
        b = Bullet(100, 100, DIR_DOWN, False)
        b.width = BULLET_SIZE
        b.height = BULLET_SIZE
        handle_bullet_tank_collision(b)
        assert main.player.alive is True

    def test_no_player_no_collision(self):
        main.player = None
        main.enemies = []
        b = Bullet(100, 100, DIR_DOWN, False)
        b.width = BULLET_SIZE
        b.height = BULLET_SIZE
        handle_bullet_tank_collision(b)
        # Should not crash


# ======================================================================
# handle_bullet_bullet_collision
# ======================================================================
class TestHandleBulletBulletCollision:
    def test_bullets_cancel_each_other(self):
        main.explosions = []
        pb = Bullet(100, 100, DIR_UP, True)
        eb = Bullet(100, 100, DIR_DOWN, False)
        main.bullets = [pb, eb]
        handle_bullet_bullet_collision()
        assert pb.alive is False
        assert eb.alive is False

    def test_same_direction_no_collision(self):
        main.explosions = []
        pb = Bullet(100, 100, DIR_UP, True)
        eb = Bullet(300, 300, DIR_UP, False)
        main.bullets = [pb, eb]
        handle_bullet_bullet_collision()
        assert pb.alive is True
        assert eb.alive is True

    def test_dead_bullets_ignored(self):
        main.explosions = []
        pb = Bullet(100, 100, DIR_UP, True)
        pb.alive = False
        eb = Bullet(100, 100, DIR_DOWN, False)
        main.bullets = [pb, eb]
        handle_bullet_bullet_collision()
        assert eb.alive is True  # not cancelled

    def test_creates_explosions(self):
        main.explosions = []
        pb = Bullet(100, 100, DIR_UP, True)
        eb = Bullet(100, 100, DIR_DOWN, False)
        main.bullets = [pb, eb]
        handle_bullet_bullet_collision()
        assert len(main.explosions) == 2

    def test_only_player_bullets_no_cancel(self):
        main.explosions = []
        pb1 = Bullet(100, 100, DIR_UP, True)
        pb2 = Bullet(100, 100, DIR_DOWN, True)
        main.bullets = [pb1, pb2]
        handle_bullet_bullet_collision()
        assert pb1.alive is True
        assert pb2.alive is True


# ======================================================================
# Steel explosion direction (handle_bullet_map_collision)
# ======================================================================
class TestSteelExplosionDirection:
    def test_steel_hit_from_up(self):
        main.map_data = make_empty_map()
        main.map_data[1][1] = TERRAIN_STEEL
        main.explosions = []
        # Bullet inside tile (1,1) moving down
        b = Bullet(1 * TILE + 8, 1 * TILE + 8, DIR_DOWN, True)
        handle_bullet_map_collision(b)
        assert len(main.explosions) > 0

    def test_steel_hit_from_down(self):
        main.map_data = make_empty_map()
        main.map_data[1][1] = TERRAIN_STEEL
        main.explosions = []
        b = Bullet(1 * TILE + 8, 2 * TILE - 1, DIR_UP, True)
        handle_bullet_map_collision(b)
        assert len(main.explosions) > 0

    def test_steel_hit_from_left(self):
        main.map_data = make_empty_map()
        main.map_data[1][1] = TERRAIN_STEEL
        main.explosions = []
        b = Bullet(2 * TILE - 1, 1 * TILE + 8, DIR_LEFT, True)
        handle_bullet_map_collision(b)
        assert len(main.explosions) > 0

    def test_steel_hit_from_right(self):
        main.map_data = make_empty_map()
        main.map_data[1][1] = TERRAIN_STEEL
        main.explosions = []
        b = Bullet(1 * TILE, 1 * TILE + 8, DIR_RIGHT, True)
        handle_bullet_map_collision(b)
        assert len(main.explosions) > 0


# ======================================================================
# on_key_down
# ======================================================================
class TestOnKeyDown:
    def test_pause_toggle_during_playing(self):
        from main import on_key_down
        main.game_state = 'playing'
        main.paused = False
        on_key_down(main.keys.P)
        assert main.paused is True
        on_key_down(main.keys.P)
        assert main.paused is False

    def test_no_pause_outside_playing(self):
        from main import on_key_down
        main.game_state = 'menu'
        main.paused = False
        on_key_down(main.keys.P)
        assert main.paused is False

    def test_space_starts_game_from_menu(self):
        from main import on_key_down
        main.game_state = 'menu'
        on_key_down(main.keys.SPACE)
        assert main.game_state == 'playing'
        assert main.score == 0
        assert main.lives == 3

    def test_space_restarts_from_gameover(self):
        from main import on_key_down
        main.game_state = 'gameover'
        main.score = 500
        on_key_down(main.keys.SPACE)
        assert main.game_state == 'playing'
        assert main.score == 0

    def test_space_no_effect_during_playing(self):
        from main import on_key_down
        main.game_state = 'playing'
        old_state = main.game_state
        on_key_down(main.keys.SPACE)
        assert main.game_state == old_state

    def test_other_keys_no_effect(self):
        from main import on_key_down
        main.game_state = 'playing'
        main.paused = False
        on_key_down(main.keys.W)
        assert main.paused is False


# ======================================================================
# update (main game loop)
# ======================================================================
class TestUpdate:
    def test_gameover_delay_decrements(self):
        from main import update
        main.gameover_delay = 10
        main.game_state = 'playing'
        update()
        assert main.gameover_delay == 9

    def test_gameover_delay_triggers_game_over(self):
        from main import update
        main.gameover_delay = 1
        main.game_state = 'playing'
        update()
        assert main.game_state == 'gameover'

    def test_gameover_delay_stops_player(self):
        from main import update
        main.gameover_delay = 10
        main.game_state = 'playing'
        main.player = Tank(100, 100, DIR_UP, True)
        main.player.moving = True
        update()
        assert main.player.moving is False

    def test_stage_transition_timer_decrements(self):
        from main import update
        main.game_state = 'stageTransition'
        main.stage_transition_timer = 50
        update()
        assert main.stage_transition_timer == 49

    def test_stage_transition_completes(self):
        from main import update
        main.game_state = 'stageTransition'
        main.stage_transition_timer = 1
        main.stage = 2
        update()
        assert main.game_state == 'playing'

    def test_no_update_when_paused(self):
        from main import update
        main.game_state = 'playing'
        main.paused = True
        main.player = None
        main.enemies = []
        main.bullets = []
        # Should not crash
        update()

    def test_no_update_in_menu(self):
        from main import update
        main.game_state = 'menu'
        main.player = None
        main.enemies = []
        # Should not crash
        update()

    def test_playing_update_clears_dead_bullets(self):
        from main import update
        main.game_state = 'playing'
        main.paused = False
        main.player = None
        main.enemies = []
        b = Bullet(100, 100, DIR_UP, True)
        b.alive = False
        main.bullets = [b]
        update()
        assert len(main.bullets) == 0

    def test_playing_update_clears_dead_explosions(self):
        from main import update
        main.game_state = 'playing'
        main.paused = False
        main.player = None
        main.enemies = []
        main.bullets = []
        ex = Explosion.__new__(Explosion)
        ex.alive = False
        ex.timer = 0
        ex.frame = 0
        ex.max_frame = 8
        main.explosions = [ex]
        update()
        assert len(main.explosions) == 0

    def test_spawn_timer_increments(self):
        from main import update
        main.game_state = 'playing'
        main.paused = False
        main.player = None
        main.enemies = []
        main.bullets = []
        old_timer = main.spawn_timer
        update()
        assert main.spawn_timer == old_timer + 1
