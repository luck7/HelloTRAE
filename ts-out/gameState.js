export const game = {
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
    paused: false
};
export let canvas;
export let ctx;
export function setCanvas(c, c2) {
    canvas = c;
    ctx = c2;
}
//# sourceMappingURL=gameState.js.map