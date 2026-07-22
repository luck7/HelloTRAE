import {
    TILE, BULLET_SIZE, CANVAS_W, CANVAS_H,
    DIR, Direction
} from './constants.js';
import { IMAGES } from './images.js';
import { Explosion } from './explosion.js';
import { playExplosionSound } from './audio.js';
import { game } from './gameState.js';
import { checkBulletMapCollision, checkBulletTankCollision } from './collision.js';
import { Tank } from './tank.js';

export class Bullet {
    x: number;
    y: number;
    dir: Direction;
    isPlayer: boolean;
    speed: number;
    width: number;
    height: number;
    alive: boolean;
    owner: Tank | null;

    constructor(x: number, y: number, dir: Direction, isPlayer: boolean) {
        this.x = x;
        this.y = y;
        this.dir = dir;
        this.isPlayer = isPlayer;
        this.speed = 4;
        this.width = BULLET_SIZE;
        this.height = BULLET_SIZE;
        this.alive = true;
        this.owner = null;
    }

    update(): void {
        if (!this.alive) return;
        if (this.dir === DIR.UP) this.y -= this.speed;
        else if (this.dir === DIR.RIGHT) this.x += this.speed;
        else if (this.dir === DIR.DOWN) this.y += this.speed;
        else if (this.dir === DIR.LEFT) this.x -= this.speed;

        if (this.x < 0 || this.y < 0 || this.x + this.width > CANVAS_W || this.y + this.height > CANVAS_H) {
            this.alive = false;
            game.explosions.push(new Explosion(this.x, this.y, 'small'));
            playExplosionSound();
            return;
        }

        if (checkBulletMapCollision(this)) return;

        checkBulletTankCollision(this);
    }

    getImage(): HTMLImageElement | null {
        const dirStr: string = ['Up', 'Right', 'Down', 'Left'][this.dir];
        return IMAGES['bullet' + dirStr] || null;
    }

    draw(ctx: CanvasRenderingContext2D): void {
        if (!this.alive) return;
        const img: HTMLImageElement | null = this.getImage();
        if (img) {
            ctx.drawImage(img, Math.floor(this.x), Math.floor(this.y), BULLET_SIZE, BULLET_SIZE);
        } else {
            ctx.fillStyle = '#fff';
            ctx.fillRect(Math.floor(this.x), Math.floor(this.y), this.width, this.height);
        }
    }
}
