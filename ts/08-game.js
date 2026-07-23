"use strict";
/// <reference path="00-constants.ts" />
/// <reference path="01-images.ts" />
/// <reference path="03-explosion.ts" />
/// <reference path="04-bullet.ts" />
/// <reference path="05-tank.ts" />
/// <reference path="06-map.ts" />
/// <reference path="07-collision.ts" />
let canvas;
let ctx;
let gameState = 'menu';
let map = [];
let player = null;
let enemies = [];
let bullets = [];
let explosions = [];
let score = 0;
let lives = 3;
let stage = 1;
let totalEnemies = 20;
let spawnedEnemies = 0;
let spawnTimer = 0;
let keys = {};
let gameLoopId = null;
let baseAlive = true;
let paused = false;
let gameOverDelay = 0;
function respawnPlayer() {
    if (lives > 0) {
        player = new Tank(4 * TILE, 12 * TILE, DIR.UP, true);
    }
}
function spawnEnemy() {
    if (spawnedEnemies >= totalEnemies)
        return;
    const spawnPoints = [0, 6, 12];
    const sx = spawnPoints[Math.floor(Math.random() * spawnPoints.length)] * TILE;
    const sy = 0;
    let occupied = false;
    for (const e of enemies) {
        if (e.alive && Math.abs(e.x - sx) < TILE && Math.abs(e.y - sy) < TILE) {
            occupied = true;
            break;
        }
    }
    if (!occupied) {
        enemies.push(new Tank(sx, sy, DIR.DOWN, false));
        spawnedEnemies++;
        updateUI();
    }
}
function updateEnemies() {
    for (const e of enemies) {
        if (!e.alive)
            continue;
        e.moving = true;
        const oldDir = e.dir;
        if (e.turnCooldown <= 0) {
            if (Math.random() < 0.008) {
                const opposite = ((e.dir + 2) % 4);
                const choices = [0, 1, 2, 3].filter(d => d !== opposite);
                e.dir = choices[Math.floor(Math.random() * choices.length)];
            }
            if (player && player.alive && Math.random() < 0.06) {
                const dx = player.x - e.x;
                const dy = player.y - e.y;
                const opposite = ((e.dir + 2) % 4);
                let newDir = e.dir;
                if (Math.abs(dx) > Math.abs(dy)) {
                    newDir = dx > 0 ? DIR.RIGHT : DIR.LEFT;
                }
                else {
                    newDir = dy > 0 ? DIR.DOWN : DIR.UP;
                }
                if (newDir !== opposite)
                    e.dir = newDir;
            }
        }
        if (e.dir !== oldDir) {
            e.turnCooldown = 60;
            e.snapToGrid();
        }
        e.move();
        if (e.x === e._lastX && e.y === e._lastY) {
            if (e.turnCooldown <= 0) {
                const opposite = ((e.dir + 2) % 4);
                const choices = [0, 1, 2, 3].filter(d => d !== e.dir && d !== opposite);
                e.dir = choices[Math.floor(Math.random() * choices.length)];
                e.turnCooldown = 60;
            }
        }
        e._lastX = e.x;
        e._lastY = e.y;
        if (Math.random() < 0.012) {
            e.shoot();
        }
    }
}
function update() {
    if (gameOverDelay > 0) {
        gameOverDelay--;
        if (player)
            player.moving = false;
        if (gameOverDelay <= 0) {
            gameOver('Base destroyed!');
        }
        return;
    }
    if (gameState !== 'playing' || paused)
        return;
    spawnTimer++;
    if (spawnTimer > 200) {
        spawnTimer = 0;
        if (enemies.filter(e => e.alive).length < 3) {
            spawnEnemy();
        }
    }
    if (player && player.alive) {
        player.moving = false;
        if (keys['w'] || keys['arrowup']) {
            player.dir = DIR.UP;
            player.moving = true;
        }
        else if (keys['s'] || keys['arrowdown']) {
            player.dir = DIR.DOWN;
            player.moving = true;
        }
        else if (keys['a'] || keys['arrowleft']) {
            player.dir = DIR.LEFT;
            player.moving = true;
        }
        else if (keys['d'] || keys['arrowright']) {
            player.dir = DIR.RIGHT;
            player.moving = true;
        }
        if (player.moving) {
            player.move();
        }
        else {
            player.slideToGrid();
        }
        player.update();
    }
    if (keys[' '] && player && player.alive) {
        player.shoot();
    }
    updateEnemies();
    for (const e of enemies)
        e.update();
    for (const b of bullets)
        b.update();
    checkBulletBulletCollision();
    bullets = bullets.filter(b => b.alive);
    for (const ex of explosions)
        ex.update();
    explosions = explosions.filter(ex => ex.alive);
    enemies = enemies.filter(e => e.alive);
    if (spawnedEnemies >= totalEnemies && enemies.length === 0) {
        stageComplete();
    }
}
function draw() {
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);
    for (let y = 0; y < MAP_H; y++) {
        for (let x = 0; x < MAP_W; x++) {
            const tile = map[y][x];
            const tx = x * TILE, ty = y * TILE;
            if (tile === TERRAIN.BRICK && IMAGES.brick) {
                ctx.drawImage(IMAGES.brick, tx, ty, TILE, TILE);
            }
            else if (tile === TERRAIN.STEEL && IMAGES.steel) {
                ctx.drawImage(IMAGES.steel, tx, ty, TILE, TILE);
            }
            else if (tile === TERRAIN.WATER && IMAGES.water) {
                ctx.drawImage(IMAGES.water, tx, ty, TILE, TILE);
            }
        }
    }
    if (baseAlive) {
        if (IMAGES.base) {
            ctx.drawImage(IMAGES.base, BASE_COL * TILE, BASE_ROW * TILE, TILE, TILE);
        }
        else {
            ctx.fillStyle = '#ccc';
            ctx.fillRect(BASE_COL * TILE, BASE_ROW * TILE, TILE, TILE);
        }
    }
    else {
        if (IMAGES.baseDestroyed) {
            ctx.drawImage(IMAGES.baseDestroyed, BASE_COL * TILE, BASE_ROW * TILE, TILE, TILE);
        }
    }
    for (const e of enemies)
        e.draw(ctx);
    if (player)
        player.draw(ctx);
    for (const b of bullets)
        b.draw(ctx);
    for (const ex of explosions)
        ex.draw(ctx);
    for (let y = 0; y < MAP_H; y++) {
        for (let x = 0; x < MAP_W; x++) {
            if (map[y][x] === TERRAIN.GRASS && IMAGES.grass) {
                ctx.drawImage(IMAGES.grass, x * TILE, y * TILE, TILE, TILE);
            }
        }
    }
    if (paused) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
        ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 24px "Courier New", monospace';
        ctx.textAlign = 'center';
        ctx.fillText('PAUSED', CANVAS_W / 2, CANVAS_H / 2);
        ctx.font = '12px "Courier New", monospace';
        ctx.fillText('Press P to Continue', CANVAS_W / 2, CANVAS_H / 2 + 24);
    }
}
function gameLoop() {
    if (gameState === 'playing') {
        update();
        draw();
    }
    gameLoopId = requestAnimationFrame(gameLoop);
}
//# sourceMappingURL=08-game.js.map