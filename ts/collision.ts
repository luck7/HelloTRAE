import {
    TILE, MAP_W, MAP_H, TERRAIN, TerrainType, BASE_COL, BASE_ROW
} from './constants.js';
import { Explosion } from './explosion.js';
import { Bullet } from './bullet.js';
import { Tank } from './tank.js';
import { game } from './gameState.js';
import { playExplosionSound, playTankExplosionSound } from './audio.js';
import { gameOver, updateUI, respawnPlayer } from './ui.js';

export function checkMapCollision(x: number, y: number, w: number, h: number): boolean {
    const left: number = Math.floor(x / TILE);
    const right: number = Math.floor((x + w - 1) / TILE);
    const top: number = Math.floor(y / TILE);
    const bottom: number = Math.floor((y + h - 1) / TILE);

    for (let ty: number = top; ty <= bottom; ty++) {
        for (let tx: number = left; tx <= right; tx++) {
            if (ty < 0 || ty >= MAP_H || tx < 0 || tx >= MAP_W) return false;
            const tile: TerrainType = game.map[ty][tx];
            if (tile === TERRAIN.BRICK || tile === TERRAIN.STEEL || tile === TERRAIN.WATER) {
                return false;
            }
        }
    }
    const baseX: number = BASE_COL * TILE;
    const baseY: number = BASE_ROW * TILE;
    if (x < baseX + TILE && x + w > baseX && y < baseY + TILE && y + h > baseY) {
        return false;
    }
    return true;
}

export function checkTankCollision(self: Tank, nx: number, ny: number): boolean {
    const sw: number = self.width, sh: number = self.height;
    if (game.player && game.player.alive && game.player !== self) {
        if (rectOverlap(nx, ny, sw, sh, game.player.x, game.player.y, game.player.width, game.player.height)) {
            return false;
        }
    }
    for (const e of game.enemies) {
        if (e.alive && e !== self) {
            if (rectOverlap(nx, ny, sw, sh, e.x, e.y, e.width, e.height)) {
                return false;
            }
        }
    }
    return true;
}

export function rectOverlap(x1: number, y1: number, w1: number, h1: number, x2: number, y2: number, w2: number, h2: number): boolean {
    return x1 < x2 + w2 && x1 + w1 > x2 && y1 < y2 + h2 && y1 + h1 > y2;
}

export function checkBulletMapCollision(bullet: Bullet): boolean {
    const left: number = Math.floor(bullet.x / TILE);
    const right: number = Math.floor((bullet.x + bullet.width - 1) / TILE);
    const top: number = Math.floor(bullet.y / TILE);
    const bottom: number = Math.floor((bullet.y + bullet.height - 1) / TILE);

    for (let cy: number = top; cy <= bottom; cy++) {
        for (let cx: number = left; cx <= right; cx++) {
            if (cy < 0 || cy >= MAP_H || cx < 0 || cx >= MAP_W) {
                bullet.alive = false;
                const ex: number = bullet.x + BULLET_SIZE / 2 - TILE / 2;
                const ey: number = bullet.y + BULLET_SIZE / 2 - TILE / 2;
                game.explosions.push(new Explosion(ex, ey, 'small'));
                playExplosionSound();
                return true;
            }
            const tile: TerrainType = game.map[cy][cx];
            if (tile === TERRAIN.BRICK) {
                game.map[cy][cx] = TERRAIN.EMPTY;
                bullet.alive = false;
                game.explosions.push(new Explosion(cx * TILE, cy * TILE, 'small'));
                playExplosionSound(false);
                return true;
            } else if (tile === TERRAIN.STEEL) {
                bullet.alive = false;
                game.explosions.push(new Explosion(cx * TILE, cy * TILE, 'small'));
                playExplosionSound(true);
                return true;
            }
        }
    }

    if (right >= BASE_COL && left <= BASE_COL && bottom >= BASE_ROW && top <= BASE_ROW) {
        bullet.alive = false;
        if (game.baseAlive) {
            game.baseAlive = false;
            game.gameOverDelay = 180;
        }
        return true;
    }

    return false;
}

export function checkBulletTankCollision(bullet: Bullet): void {
    if (bullet.isPlayer) {
        for (const e of game.enemies) {
            if (e.alive && rectOverlap(bullet.x, bullet.y, bullet.width, bullet.height,
                e.x, e.y, e.width, e.height)) {
                bullet.alive = false;
                e.alive = false;
                game.explosions.push(new Explosion(e.x, e.y, 'normal'));
                playTankExplosionSound();
                game.score += 100;
                updateUI();
                return;
            }
        }
    } else {
        if (game.player && game.player.alive && game.player.invincible <= 0 &&
            rectOverlap(bullet.x, bullet.y, bullet.width, bullet.height,
            game.player.x, game.player.y, game.player.width, game.player.height)) {
            bullet.alive = false;
            game.player.alive = false;
            game.explosions.push(new Explosion(game.player.x, game.player.y, 'big'));
            playTankExplosionSound();
            game.lives--;
            updateUI();
            if (game.lives <= 0) {
                gameOver('You were defeated!');
            } else {
                setTimeout(() => respawnPlayer(), 1500);
            }
        }
    }
}

export function checkBulletBulletCollision(): void {
    const playerBullets: Bullet[] = game.bullets.filter(b => b.alive && b.isPlayer);
    const enemyBullets: Bullet[] = game.bullets.filter(b => b.alive && !b.isPlayer);
    for (const pb of playerBullets) {
        for (const eb of enemyBullets) {
            if (rectOverlap(pb.x, pb.y, pb.width, pb.height, eb.x, eb.y, eb.width, eb.height)) {
                pb.alive = false;
                eb.alive = false;
                game.explosions.push(new Explosion(
                    (pb.x + eb.x) / 2,
                    (pb.y + eb.y) / 2,
                    'small'
                ));
            }
        }
    }
}
