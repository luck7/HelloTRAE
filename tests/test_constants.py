"""Tests for constants defined in constants.py."""
import constants as c


class TestTileConstants:
    def test_tile_size(self):
        assert c.TILE_SIZE == 32

    def test_map_dimensions(self):
        assert c.GRID_W == 13
        assert c.GRID_H == 13

    def test_game_dimensions(self):
        assert c.GAME_W == c.GRID_W * c.TILE_SIZE  # 416
        assert c.GAME_H == c.GRID_H * c.TILE_SIZE  # 416

    def test_hud_width(self):
        assert c.HUD_W == 96

    def test_bullet_size(self):
        assert c.BULLET_SIZE == 16

    def test_fps(self):
        assert c.FPS == 60


class TestDirectionConstants:
    def test_direction_values(self):
        assert c.UP == 'up'
        assert c.DOWN == 'down'
        assert c.LEFT == 'left'
        assert c.RIGHT == 'right'

    def test_directions_are_unique(self):
        dirs = [c.UP, c.DOWN, c.LEFT, c.RIGHT]
        assert len(set(dirs)) == 4

    def test_dir_vec_has_all_directions(self):
        for d in (c.UP, c.DOWN, c.LEFT, c.RIGHT):
            assert d in c.DIR_VEC

    def test_dir_bullet_img_has_all_directions(self):
        for d in (c.UP, c.DOWN, c.LEFT, c.RIGHT):
            assert d in c.DIR_BULLET_IMG

    def test_dir_tank_img_has_both_kinds(self):
        assert 'player' in c.DIR_TANK_IMG
        assert 'enemy' in c.DIR_TANK_IMG
        for d in (c.UP, c.DOWN, c.LEFT, c.RIGHT):
            assert d in c.DIR_TANK_IMG['player']
            assert d in c.DIR_TANK_IMG['enemy']


class TestTerrainConstants:
    def test_terrain_values(self):
        assert c.T_EMPTY == 0
        assert c.T_BRICK == 1
        assert c.T_STEEL == 2
        assert c.T_WATER == 3
        assert c.T_GRASS == 4

    def test_terrains_are_unique(self):
        terrains = [c.T_EMPTY, c.T_BRICK, c.T_STEEL, c.T_GRASS, c.T_WATER]
        assert len(set(terrains)) == 5


class TestGameStateConstants:
    def test_state_values(self):
        assert c.STATE_MENU == 'menu'
        assert c.STATE_PLAYING == 'playing'
        assert c.STATE_PAUSED == 'paused'
        assert c.STATE_GAME_OVER == 'game_over'
        assert c.STATE_WIN == 'win'


class TestWindowDimensions:
    def test_width(self):
        assert c.WIDTH == c.GAME_W + c.HUD_W  # 512

    def test_height(self):
        assert c.HEIGHT == c.GAME_H  # 416


class TestTuningConstants:
    def test_tank_speed(self):
        assert c.TANK_SPEED == 2

    def test_bullet_speed(self):
        assert c.BULLET_SPEED == 4

    def test_player_lives(self):
        assert c.PLAYER_LIVES == 3

    def test_max_enemies_on_screen(self):
        assert c.MAX_ENEMIES_ON_SCREEN == 4

    def test_total_enemies(self):
        assert c.TOTAL_ENEMIES == 20

    def test_spawn_protection(self):
        assert c.SPAWN_PROTECTION == 120

    def test_spawn_interval(self):
        assert c.SPAWN_INTERVAL == 180
