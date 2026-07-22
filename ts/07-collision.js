"use strict";
/// <reference path="00-constants.ts" />
/// <reference path="02-audio.ts" />
/// <reference path="03-explosion.ts" />
/// <reference path="04-bullet.ts" />
/// <reference path="05-tank.ts" />
/// <reference path="06-map.ts" />
function checkMapCollision(x, y, w, h) {
    const left = Math.floor(x / TILE);
    const right = Math.floor((x + w - 1) / TILE);
    const top = Math.floor(y / TILE);
    const bottom = Math.floor((y + h - 1) / TILE);
    for (let ty = top; ty <= bottom; ty++) {
        for (let tx = left; tx <= right; tx++) {
            if (ty < 0 || ty >= MAP_H || tx < 0 || tx >= MAP_W)
                return false;
            const tile = map[ty][tx];
            if (tile === TERRAIN.BRICK || tile === TERRAIN.STEEL || tile === TERRAIN.WATER) {
                return false;
            }
        }
    }
    const baseX = BASE_COL * TILE;
    const baseY = BASE_ROW * TILE;
    if (x < baseX + TILE && x + w > baseX && y < baseY + TILE && y + h > baseY) {
        return false;
    }
    return true;
}
function checkTankCollision(self, nx, ny) {
    const sw = self.width, sh = self.height;
    if (player && player.alive && player !== self) {
        if (rectOverlap(nx, ny, sw, sh, player.x, player.y, player.width, player.height)) {
            return false;
        }
    }
    for (const e of enemies) {
        if (e.alive && e !== self) {
            if (rectOverlap(nx, ny, sw, sh, e.x, e.y, e.width, e.height)) {
                return false;
            }
        }
    }
    return true;
}
function rectOverlap(x1, y1, w1, h1, x2, y2, w2, h2) {
    return x1 < x2 + w2 && x1 + w1 > x2 && y1 < y2 + h2 && y1 + h1 > y2;
}
function checkBulletMapCollision(bullet) {
    const left = Math.floor(bullet.x / TILE);
    const right = Math.floor((bullet.x + bullet.width - 1) / TILE);
    const top = Math.floor(bullet.y / TILE);
    const bottom = Math.floor((bullet.y + bullet.height - 1) / TILE);
    for (let cy = top; cy <= bottom; cy++) {
        for (let cx = left; cx <= right; cx++) {
            if (cy < 0 || cy >= MAP_H || cx < 0 || cx >= MAP_W) {
                bullet.alive = false;
                explosions.push(new Explosion(bullet.x, bullet.y, 'small'));
                playExplosionSound();
                return true;
            }
            const tile = map[cy][cx];
            if (tile === TERRAIN.BRICK) {
                map[cy][cx] = TERRAIN.EMPTY;
                bullet.alive = false;
                explosions.push(new Explosion(cx * TILE, cy * TILE, 'small'));
                playExplosionSound(false);
                return true;
            }
            else if (tile === TERRAIN.STEEL) {
                bullet.alive = false;
                explosions.push(new Explosion(cx * TILE, cy * TILE, 'small'));
                playExplosionSound(true);
                return true;
            }
        }
    }
    if (right >= BASE_COL && left <= BASE_COL && bottom >= BASE_ROW && top <= BASE_ROW) {
        bullet.alive = false;
        if (baseAlive) {
            baseAlive = false;
            explosions.push(new Explosion(BASE_COL * TILE, BASE_ROW * TILE, 'big'));
            gameOver('Base destroyed!');
        }
        return true;
    }
    return false;
}
function checkBulletTankCollision(bullet) {
    if (bullet.isPlayer) {
        for (const e of enemies) {
            if (e.alive && rectOverlap(bullet.x, bullet.y, bullet.width, bullet.height, e.x, e.y, e.width, e.height)) {
                bullet.alive = false;
                e.alive = false;
                explosions.push(new Explosion(e.x, e.y, 'normal'));
                playTankExplosionSound();
                score += 100;
                updateUI();
                return;
            }
        }
    }
    else {
        if (player && player.alive && player.invincible <= 0 &&
            rectOverlap(bullet.x, bullet.y, bullet.width, bullet.height, player.x, player.y, player.width, player.height)) {
            bullet.alive = false;
            player.alive = false;
            explosions.push(new Explosion(player.x, player.y, 'big'));
            playTankExplosionSound();
            lives--;
            updateUI();
            if (lives <= 0) {
                gameOver('You were defeated!');
            }
            else {
                setTimeout(() => respawnPlayer(), 1500);
            }
        }
    }
}
function checkBulletBulletCollision() {
    const playerBullets = bullets.filter(b => b.alive && b.isPlayer);
    const enemyBullets = bullets.filter(b => b.alive && !b.isPlayer);
    for (const pb of playerBullets) {
        for (const eb of enemyBullets) {
            if (rectOverlap(pb.x, pb.y, pb.width, pb.height, eb.x, eb.y, eb.width, eb.height)) {
                pb.alive = false;
                eb.alive = false;
                explosions.push(new Explosion((pb.x + eb.x) / 2, (pb.y + eb.y) / 2, 'small'));
            }
        }
    }
}
//# sourceMappingURL=07-collision.js.map