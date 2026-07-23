import {
    TILE, CANVAS_W, CANVAS_H, MAP_W, MAP_H,
    TERRAIN, BASE_COL, BASE_ROW, DIR, Direction
} from './constants.js';
import { IMAGES } from './images.js';
import { Explosion } from './explosion.js';
import { Bullet } from './bullet.js';
import { Tank } from './tank.js';
import { game, canvas, ctx } from './gameState.js';
import { checkBulletBulletCollision } from './collision.js';
import { updateUI, stageComplete, gameOver } from './ui.js';

export function spawnEnemy(): void {
    if (game.spawnedEnemies >= game.totalEnemies) return;
    const spawnPoints: number[] = [0, 6, 12];
    const sx: number = spawnPoints[Math.floor(Math.random() * spawnPoints.length)] * TILE;
    const sy: number = 0;
    let occupied: boolean = false;
    for (const e of game.enemies) {
        if (e.alive && Math.abs(e.x - sx) < TILE && Math.abs(e.y - sy) < TILE) {
            occupied = true;
            break;
        }
    }
    if (!occupied) {
        game.enemies.push(new Tank(sx, sy, DIR.DOWN, false));
        game.spawnedEnemies++;
        updateUI();
    }
}

export function updateEnemies(): void {
    for (const e of game.enemies) {
        if (!e.alive) continue;
        e.moving = true;

        const oldDir: Direction = e.dir;
        if (e.turnCooldown <= 0) {
            if (Math.random() < 0.008) {
                const opposite: Direction = ((e.dir + 2) % 4) as Direction;
                const choices: Direction[] = [0, 1, 2, 3].filter(d => d !== opposite) as Direction[];
                e.dir = choices[Math.floor(Math.random() * choices.length)];
            }

            if (game.player && game.player.alive && Math.random() < 0.06) {
                const dx: number = game.player.x - e.x;
                const dy: number = game.player.y - e.y;
                const opposite: Direction = ((e.dir + 2) % 4) as Direction;
                let newDir: Direction = e.dir;
                if (Math.abs(dx) > Math.abs(dy)) {
                    newDir = dx > 0 ? DIR.RIGHT : DIR.LEFT;
                } else {
                    newDir = dy > 0 ? DIR.DOWN : DIR.UP;
                }
                if (newDir !== opposite) e.dir = newDir;
            }
        }

        // 转向时对齐垂直轴
        if (e.dir !== oldDir) {
            e.turnCooldown = 60;
            e.snapToGrid();
        }

        e.move();

        if (e.x === e._lastX && e.y === e._lastY) {
            if (e.turnCooldown <= 0) {
                const opposite: Direction = ((e.dir + 2) % 4) as Direction;
                const choices: Direction[] = [0, 1, 2, 3].filter(d => d !== e.dir && d !== opposite) as Direction[];
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

export function update(): void {
    if (game.gameOverDelay > 0) {
        game.gameOverDelay--;
        if (game.player) game.player.moving = false;
        if (game.gameOverDelay <= 0) {
            gameOver('Base destroyed!');
        }
        return;
    }
    if (game.gameState !== 'playing' || game.paused) return;

    game.spawnTimer++;
    if (game.spawnTimer > 200) {
        game.spawnTimer = 0;
        if (game.enemies.filter(e => e.alive).length < 3) {
            spawnEnemy();
        }
    }

    if (game.player && game.player.alive) {
        game.player.moving = false;
        if (game.keys['w'] || game.keys['arrowup']) { game.player.dir = DIR.UP; game.player.moving = true; }
        else if (game.keys['s'] || game.keys['arrowdown']) { game.player.dir = DIR.DOWN; game.player.moving = true; }
        else if (game.keys['a'] || game.keys['arrowleft']) { game.player.dir = DIR.LEFT; game.player.moving = true; }
        else if (game.keys['d'] || game.keys['arrowright']) { game.player.dir = DIR.RIGHT; game.player.moving = true; }

        if (game.player.moving) {
            game.player.move();
        } else {
            game.player.slideToGrid();
        }
        game.player.update();
    }

    if (game.keys[' '] && game.player && game.player.alive) {
        game.player.shoot();
    }

    updateEnemies();
    for (const e of game.enemies) e.update();

    for (const b of game.bullets) b.update();
    checkBulletBulletCollision();
    game.bullets = game.bullets.filter(b => b.alive);

    for (const ex of game.explosions) ex.update();
    game.explosions = game.explosions.filter(ex => ex.alive);

    game.enemies = game.enemies.filter(e => e.alive);

    if (game.spawnedEnemies >= game.totalEnemies && game.enemies.length === 0) {
        stageComplete();
    }
}

export function draw(): void {
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);

    for (let y: number = 0; y < MAP_H; y++) {
        for (let x: number = 0; x < MAP_W; x++) {
            const tile = game.map[y][x];
            const tx: number = x * TILE, ty: number = y * TILE;
            if (tile === TERRAIN.BRICK && IMAGES.brick) {
                ctx.drawImage(IMAGES.brick, tx, ty, TILE, TILE);
            } else if (tile === TERRAIN.STEEL && IMAGES.steel) {
                ctx.drawImage(IMAGES.steel, tx, ty, TILE, TILE);
            } else if (tile === TERRAIN.WATER && IMAGES.water) {
                ctx.drawImage(IMAGES.water, tx, ty, TILE, TILE);
            }
        }
    }

    if (game.baseAlive) {
        if (IMAGES.base) {
            ctx.drawImage(IMAGES.base, BASE_COL * TILE, BASE_ROW * TILE, TILE, TILE);
        } else {
            ctx.fillStyle = '#ccc';
            ctx.fillRect(BASE_COL * TILE, BASE_ROW * TILE, TILE, TILE);
        }
    } else {
        if (IMAGES.baseDestroyed) {
            ctx.drawImage(IMAGES.baseDestroyed, BASE_COL * TILE, BASE_ROW * TILE, TILE, TILE);
        }
    }

    for (const e of game.enemies) e.draw(ctx);
    if (game.player) game.player.draw(ctx);

    for (const b of game.bullets) b.draw(ctx);

    for (const ex of game.explosions) ex.draw(ctx);

    for (let y: number = 0; y < MAP_H; y++) {
        for (let x: number = 0; x < MAP_W; x++) {
            if (game.map[y][x] === TERRAIN.GRASS && IMAGES.grass) {
                ctx.drawImage(IMAGES.grass, x * TILE, y * TILE, TILE, TILE);
            }
        }
    }

    if (game.paused) {
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

export function gameLoop(): void {
    if (game.gameState === 'playing') {
        update();
        draw();
    }
    game.gameLoopId = requestAnimationFrame(gameLoop);
}
