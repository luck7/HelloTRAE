"use strict";
/// <reference path="00-constants.ts" />
const STAGE_MAP = [
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
function initMap() {
    map = [];
    if (stage <= 1) {
        for (let y = 0; y < MAP_H; y++) {
            map[y] = [];
            for (let x = 0; x < MAP_W; x++) {
                map[y][x] = STAGE_MAP[y][x];
            }
        }
    }
    else {
        generateRandomMap();
    }
}
function generateRandomMap() {
    map = [];
    for (let y = 0; y < MAP_H; y++) {
        map[y] = [];
        for (let x = 0; x < MAP_W; x++) {
            map[y][x] = TERRAIN.EMPTY;
        }
    }
    for (let y = 1; y < MAP_H - 2; y++) {
        for (let x = 0; x < MAP_W; x++) {
            const r = Math.random();
            if (r < 0.18)
                map[y][x] = TERRAIN.BRICK;
            else if (r < 0.24)
                map[y][x] = TERRAIN.STEEL;
            else if (r < 0.32)
                map[y][x] = TERRAIN.GRASS;
            else if (r < 0.38)
                map[y][x] = TERRAIN.WATER;
        }
    }
    map[11][5] = TERRAIN.BRICK;
    map[11][6] = TERRAIN.BRICK;
    map[11][7] = TERRAIN.BRICK;
    map[12][5] = TERRAIN.BRICK;
    map[12][7] = TERRAIN.BRICK;
    map[10][5] = TERRAIN.BRICK;
    map[10][6] = TERRAIN.BRICK;
    map[10][7] = TERRAIN.BRICK;
    for (let x = 0; x < MAP_W; x++) {
        map[0][x] = TERRAIN.EMPTY;
    }
    map[12][4] = TERRAIN.EMPTY;
    map[12][6] = TERRAIN.EMPTY;
    map[1][0] = TERRAIN.EMPTY;
    map[1][6] = TERRAIN.EMPTY;
    map[1][12] = TERRAIN.EMPTY;
    map[11][4] = TERRAIN.EMPTY;
    map[12][3] = TERRAIN.EMPTY;
}
//# sourceMappingURL=06-map.js.map