import { MAP_W, MAP_H, TERRAIN, TerrainType, TILE } from './constants.js';
import { game } from './gameState.js';

export const STAGE_MAP: number[][] = [
    [0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0],
    [0, 1, 0, 2, 0, 1, 1, 1, 0, 2, 0, 1, 0],
    [0, 1, 0, 0, 3, 1, 1, 1, 3, 0, 0, 1, 0],
    [0, 1, 0, 0, 3, 0, 0, 0, 3, 0, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    [0, 3, 0, 1, 0, 1, 0, 1, 0, 1, 0, 3, 0],
    [2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 2],
    [0, 3, 0, 1, 0, 1, 0, 1, 0, 1, 0, 3, 0],
    [0, 3, 0, 1, 0, 1, 0, 1, 0, 1, 0, 3, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0]
];

export function initMap(): void {
    game.map = [];
    if (game.stage <= 1) {
        for (let y: number = 0; y < MAP_H; y++) {
            game.map[y] = [];
            for (let x: number = 0; x < MAP_W; x++) {
                game.map[y][x] = STAGE_MAP[y][x] as TerrainType;
            }
        }
    } else {
        generateRandomMap();
    }
}

export function generateRandomMap(): void {
    game.map = [];
    for (let y: number = 0; y < MAP_H; y++) {
        game.map[y] = [];
        for (let x: number = 0; x < MAP_W; x++) {
            game.map[y][x] = TERRAIN.EMPTY;
        }
    }

    for (let y: number = 1; y < MAP_H - 2; y++) {
        for (let x: number = 0; x < MAP_W; x++) {
            const r: number = Math.random();
            if (r < 0.18) game.map[y][x] = TERRAIN.BRICK;
            else if (r < 0.24) game.map[y][x] = TERRAIN.STEEL;
            else if (r < 0.32) game.map[y][x] = TERRAIN.GRASS;
            else if (r < 0.38) game.map[y][x] = TERRAIN.WATER;
        }
    }

    game.map[11][5] = TERRAIN.BRICK;
    game.map[11][6] = TERRAIN.BRICK;
    game.map[11][7] = TERRAIN.BRICK;
    game.map[12][5] = TERRAIN.BRICK;
    game.map[12][7] = TERRAIN.BRICK;
    game.map[10][5] = TERRAIN.BRICK;
    game.map[10][6] = TERRAIN.BRICK;
    game.map[10][7] = TERRAIN.BRICK;

    for (let x: number = 0; x < MAP_W; x++) {
        game.map[0][x] = TERRAIN.EMPTY;
    }
    game.map[12][4] = TERRAIN.EMPTY;
    game.map[12][6] = TERRAIN.EMPTY;

    game.map[1][0] = TERRAIN.EMPTY;
    game.map[1][6] = TERRAIN.EMPTY;
    game.map[1][12] = TERRAIN.EMPTY;
    game.map[11][4] = TERRAIN.EMPTY;
    game.map[12][3] = TERRAIN.EMPTY;
}
