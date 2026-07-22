import {
    TILE, TANK_SIZE, BULLET_SIZE, GRID, CANVAS_W, CANVAS_H,
    DIR, Direction
} from './constants.js';
import { IMAGES } from './images.js';
import { Bullet } from './bullet.js';
import { checkMapCollision, checkTankCollision } from './collision.js';
import { game } from './gameState.js';

export class Tank {
    x: number;
    y: number;
    dir: Direction;
    isPlayer: boolean;
    width: number;
    height: number;
    speed: number;
    moving: boolean;
    alive: boolean;
    shootCooldown: number;
    invincible: number;
    blinkTimer: number;
    _lastX: number;
    _lastY: number;

    constructor(x: number, y: number, dir: Direction, isPlayer: boolean = false) {
        this.x = x;
        this.y = y;
        this.dir = dir;
        this.isPlayer = isPlayer;
        this.width = TANK_SIZE;
        this.height = TANK_SIZE;
        this.speed = isPlayer ? 1 : 1;
        this.moving = false;
        this.alive = true;
        this.shootCooldown = 0;
        this.invincible = isPlayer ? 180 : 0;
        this.blinkTimer = 0;
        this._lastX = x;
        this._lastY = y;
    }

    getImage(): HTMLImageElement | null {
        const prefix: string = this.isPlayer ? 'player' : 'enemy';
        const dirStr: string = ['Up', 'Right', 'Down', 'Left'][this.dir];
        return IMAGES[prefix + dirStr] || null;
    }

    update(): void {
        if (!this.alive) return;
        if (this.shootCooldown > 0) this.shootCooldown--;
        if (this.invincible > 0) {
            this.invincible--;
            this.blinkTimer++;
        }
    }

    snapToGrid(): void {
        const snap = (val: number): number => Math.round(val / GRID) * GRID;
        const sx: number = snap(this.x);
        const sy: number = snap(this.y);
        if (checkMapCollision(sx, this.y, this.width, this.height) &&
            checkTankCollision(this, sx, this.y)) {
            this.x = sx;
        }
        if (checkMapCollision(this.x, sy, this.width, this.height) &&
            checkTankCollision(this, this.x, sy)) {
            this.y = sy;
        }
    }

    move(): void {
        if (!this.alive || !this.moving) return;
        let nx: number = this.x, ny: number = this.y;
        const step: number = this.speed;
        if (this.dir === DIR.UP) ny -= step;
        else if (this.dir === DIR.RIGHT) nx += step;
        else if (this.dir === DIR.DOWN) ny += step;
        else if (this.dir === DIR.LEFT) nx -= step;

        if (nx < 0 || ny < 0 || nx + this.width > CANVAS_W || ny + this.height > CANVAS_H) return;

        if (!checkMapCollision(nx, ny, this.width, this.height)) return;

        if (!checkTankCollision(this, nx, ny)) return;

        this.x = nx;
        this.y = ny;
    }

    shoot(): void {
        if (!this.alive || this.shootCooldown > 0) return;
        const activeBullets: number = game.bullets.filter(b => b.alive && b.owner === this).length;
        if (activeBullets >= 2) return;
        this.shootCooldown = this.isPlayer ? 15 : 45;
        let bx: number, by: number;
        const halfBullet: number = BULLET_SIZE / 2;
        const halfTank: number = TANK_SIZE / 2;
        if (this.dir === DIR.UP) {
            bx = this.x + halfTank - halfBullet;
            by = this.y - BULLET_SIZE;
        } else if (this.dir === DIR.RIGHT) {
            bx = this.x + this.width;
            by = this.y + halfTank - halfBullet;
        } else if (this.dir === DIR.DOWN) {
            bx = this.x + halfTank - halfBullet;
            by = this.y + this.height;
        } else {
            bx = this.x - BULLET_SIZE;
            by = this.y + halfTank - halfBullet;
        }
        const bullet: Bullet = new Bullet(bx, by, this.dir, this.isPlayer);
        bullet.owner = this;
        game.bullets.push(bullet);
    }

    draw(ctx: CanvasRenderingContext2D): void {
        if (!this.alive) return;
        if (this.invincible > 0 && this.blinkTimer % 8 < 4) return;

        const img: HTMLImageElement | null = this.getImage();
        if (img) {
            ctx.drawImage(img, Math.floor(this.x), Math.floor(this.y), TANK_SIZE, TANK_SIZE);
        } else {
            ctx.fillStyle = this.isPlayer ? '#fc6' : '#c44';
            ctx.fillRect(Math.floor(this.x), Math.floor(this.y), this.width, this.height);
        }
    }
}
