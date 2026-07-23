import { TerrainType, GameState, KeyState } from './constants.js';
import { Tank } from './tank.js';
import { Bullet } from './bullet.js';
import { Explosion } from './explosion.js';

export interface GameStateData {
    gameState: GameState;
    map: TerrainType[][];
    player: Tank | null;
    enemies: Tank[];
    bullets: Bullet[];
    explosions: Explosion[];
    score: number;
    lives: number;
    stage: number;
    totalEnemies: number;
    spawnedEnemies: number;
    spawnTimer: number;
    keys: KeyState;
    gameLoopId: number | null;
    baseAlive: boolean;
    paused: boolean;
    gameOverDelay: number;
}

export const game: GameStateData = {
    gameState: 'menu',
    map: [],
    player: null,
    enemies: [],
    bullets: [],
    explosions: [],
    score: 0,
    lives: 3,
    stage: 1,
    totalEnemies: 20,
    spawnedEnemies: 0,
    spawnTimer: 0,
    keys: {},
    gameLoopId: null,
    baseAlive: true,
    paused: false,
    gameOverDelay: 0
};

export let canvas: HTMLCanvasElement;
export let ctx: CanvasRenderingContext2D;

export function setCanvas(c: HTMLCanvasElement, c2: CanvasRenderingContext2D): void {
    canvas = c;
    ctx = c2;
}
