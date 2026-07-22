export const TILE: number = 32;
export const MAP_W: number = 13;
export const MAP_H: number = 13;
export const CANVAS_W: number = MAP_W * TILE;
export const CANVAS_H: number = MAP_H * TILE;
export const TANK_SIZE: number = 32;
export const BULLET_SIZE: number = 16;
export const GRID: number = 16;

export const DIR = { UP: 0, RIGHT: 1, DOWN: 2, LEFT: 3 } as const;
export type Direction = typeof DIR[keyof typeof DIR];

export const TERRAIN = { EMPTY: 0, BRICK: 1, STEEL: 2, GRASS: 3, WATER: 4 } as const;
export type TerrainType = typeof TERRAIN[keyof typeof TERRAIN];

export const BASE_COL: number = 6;
export const BASE_ROW: number = 12;

export type GameState = 'menu' | 'playing' | 'gameover' | 'stageTransition';
export type ExplosionSize = 'small' | 'normal' | 'big';

export interface ImageDictionary {
    [key: string]: HTMLImageElement;
}

export interface ImageSourceDictionary {
    playerUp: string;
    playerDown: string;
    playerLeft: string;
    playerRight: string;
    enemyUp: string;
    enemyDown: string;
    enemyLeft: string;
    enemyRight: string;
    bulletUp: string;
    bulletDown: string;
    bulletLeft: string;
    bulletRight: string;
    brick: string;
    steel: string;
    grass: string;
    water: string;
    base: string;
    baseDestroyed: string;
    explosion: string;
    [key: string]: string;
}

export interface KeyState {
    [key: string]: boolean;
}
