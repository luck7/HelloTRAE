"""
Battle City - Game constants.

All tuning parameters, tile types, directions, colors, and window dimensions
used across the project are defined here.
"""

# ----------------------------------------------------------------------
# Window / grid dimensions
# ----------------------------------------------------------------------
TILE_SIZE = 32
GRID_W = 13
GRID_H = 13
GAME_W = GRID_W * TILE_SIZE   # 416
GAME_H = GRID_H * TILE_SIZE   # 416
HUD_W = 96
WIDTH = GAME_W + HUD_W        # 512
HEIGHT = GAME_H               # 416
FPS = 60

# ----------------------------------------------------------------------
# Tile types
# ----------------------------------------------------------------------
T_EMPTY = 0
T_BRICK = 1
T_STEEL = 2
T_WATER = 3
T_GRASS = 4

# ----------------------------------------------------------------------
# Directions
# ----------------------------------------------------------------------
UP, DOWN, LEFT, RIGHT = 'up', 'down', 'left', 'right'

DIR_VEC = {
    UP: (0, -1),
    DOWN: (0, 1),
    LEFT: (-1, 0),
    RIGHT: (1, 0),
}

DIR_BULLET_IMG = {
    UP: 'bullet_up',
    DOWN: 'bullet_down',
    LEFT: 'bullet_left',
    RIGHT: 'bullet_right',
}

DIR_TANK_IMG = {
    'player': {
        UP: 'tank_player_up',
        DOWN: 'tank_player_down',
        LEFT: 'tank_player_left',
        RIGHT: 'tank_player_right',
    },
    'enemy': {
        UP: 'tank_basic_up',
        DOWN: 'tank_basic_down',
        LEFT: 'tank_basic_left',
        RIGHT: 'tank_basic_right',
    },
}

# ----------------------------------------------------------------------
# Game states
# ----------------------------------------------------------------------
STATE_MENU = 'menu'
STATE_PLAYING = 'playing'
STATE_PAUSED = 'paused'
STATE_GAME_OVER = 'game_over'
STATE_WIN = 'win'

# ----------------------------------------------------------------------
# Colors
# ----------------------------------------------------------------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (60, 60, 60)
GRAY = (110, 110, 110)
LIGHT_GRAY = (180, 180, 180)
HUD_BG = (24, 24, 24)
HUD_BORDER = (90, 90, 90)
RED = (210, 60, 60)
YELLOW = (230, 200, 60)
GREEN = (70, 200, 70)
ORANGE = (220, 130, 40)
BROWN = (140, 90, 50)

# ----------------------------------------------------------------------
# Tuning
# ----------------------------------------------------------------------
TANK_SPEED = 2
BULLET_SPEED = 4
BULLET_SIZE = 16  # bullet sprites are 16x16

PLAYER_LIVES = 3
PLAYER_SHOOT_COOLDOWN = 18      # frames

MAX_ENEMIES_ON_SCREEN = 4
TOTAL_ENEMIES = 20
ENEMY_SHOOT_COOLDOWN_MIN = 50
ENEMY_SHOOT_COOLDOWN_MAX = 150
ENEMY_DIR_CHANGE_MIN = 40
ENEMY_DIR_CHANGE_MAX = 180

SPAWN_INTERVAL = 180             # frames between enemy spawns
SPAWN_PROTECTION = 120           # frames of invulnerability after spawn
