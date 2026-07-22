"use strict";
/// <reference path="00-constants.ts" />
/// <reference path="01-images.ts" />
/// <reference path="02-audio.ts" />
/// <reference path="03-explosion.ts" />
class Bullet {
    constructor(x, y, dir, isPlayer) {
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
    update() {
        if (!this.alive)
            return;
        if (this.dir === DIR.UP)
            this.y -= this.speed;
        else if (this.dir === DIR.RIGHT)
            this.x += this.speed;
        else if (this.dir === DIR.DOWN)
            this.y += this.speed;
        else if (this.dir === DIR.LEFT)
            this.x -= this.speed;
        if (this.x < 0 || this.y < 0 || this.x + this.width > CANVAS_W || this.y + this.height > CANVAS_H) {
            this.alive = false;
            explosions.push(new Explosion(this.x, this.y, 'small'));
            playExplosionSound();
            return;
        }
        if (checkBulletMapCollision(this))
            return;
        checkBulletTankCollision(this);
    }
    getImage() {
        const dirStr = ['Up', 'Right', 'Down', 'Left'][this.dir];
        return IMAGES['bullet' + dirStr] || null;
    }
    draw(ctx) {
        if (!this.alive)
            return;
        const img = this.getImage();
        if (img) {
            ctx.drawImage(img, Math.floor(this.x), Math.floor(this.y), BULLET_SIZE, BULLET_SIZE);
        }
        else {
            ctx.fillStyle = '#fff';
            ctx.fillRect(Math.floor(this.x), Math.floor(this.y), this.width, this.height);
        }
    }
}
//# sourceMappingURL=04-bullet.js.map