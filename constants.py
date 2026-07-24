import math

TILE = 32
MAP_W = 13
MAP_H = 13
SCREEN_W = MAP_W * TILE
SCREEN_H = MAP_H * TILE
TANK_SIZE = 32
BULLET_SIZE = 16
GRID = 16
HALF_TILE = TILE // 2

DIR_UP = 0
DIR_RIGHT = 1
DIR_DOWN = 2
DIR_LEFT = 3

TERRAIN_EMPTY = 0
TERRAIN_BRICK = 1
TERRAIN_STEEL = 2
TERRAIN_GRASS = 3
TERRAIN_WATER = 4

BASE_COL = 6
BASE_ROW = 12

STAGE_MAP = [
    [0,0,0,2,0,0,0,0,0,2,0,0,0],
    [0,1,0,2,0,1,1,1,0,2,0,1,0],
    [0,1,0,0,3,1,1,1,3,0,0,1,0],
    [0,1,0,0,3,0,0,0,3,0,0,1,0],
    [0,1,0,1,0,1,0,1,0,1,0,1,0],
    [0,3,0,1,0,1,0,1,0,1,0,3,0],
    [2,3,0,0,0,0,0,0,0,0,0,3,2],
    [0,3,0,1,0,1,0,1,0,1,0,3,0],
    [0,3,0,1,0,1,0,1,0,1,0,3,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,1,0,0,0,1,1,1,0,0,0,1,0],
    [0,0,0,0,0,1,1,1,0,0,0,0,0],
    [0,0,0,0,0,1,0,1,0,0,0,0,0]
]
