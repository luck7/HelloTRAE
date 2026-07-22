// ==================== 常量配置 ====================
// 所有图片都是 32x32（子弹是16x16），所以 TILE=32
const TILE = 32;
const MAP_W = 13;
const MAP_H = 13;
const CANVAS_W = MAP_W * TILE;  // 416
const CANVAS_H = MAP_H * TILE;  // 416
const TANK_SIZE = 32;
const BULLET_SIZE = 16;
const GRID = 16;

const DIR = { UP: 0, RIGHT: 1, DOWN: 2, LEFT: 3 };
const TERRAIN = { EMPTY: 0, BRICK: 1, STEEL: 2, GRASS: 3, WATER: 4 };

// 基地位置（13x13网格中的列,行）
const BASE_COL = 6;
const BASE_ROW = 12;
