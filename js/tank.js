// ==================== 坦克类 ====================
class Tank {
    constructor(x, y, dir, isPlayer = false) {
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
        this.turnCooldown = 0;
    }

    getImage() {
        const prefix = this.isPlayer ? 'player' : 'enemy';
        const dirStr = ['Up', 'Right', 'Down', 'Left'][this.dir];
        return IMAGES[prefix + dirStr] || null;
    }

    update() {
        if (!this.alive) return;
        if (this.shootCooldown > 0) this.shootCooldown--;
        if (this.turnCooldown > 0) this.turnCooldown--;
        if (this.invincible > 0) {
            this.invincible--;
            this.blinkTimer++;
        }
    }

    snapToGrid() {
        // 转向时只对齐垂直于移动方向的轴，避免斜向跳动
        if (this.dir === DIR.UP || this.dir === DIR.DOWN) {
            const sx = Math.round(this.x / GRID) * GRID;
            if (checkMapCollision(sx, this.y, this.width, this.height) &&
                checkTankCollision(this, sx, this.y)) {
                this.x = sx;
            }
        } else {
            const sy = Math.round(this.y / GRID) * GRID;
            if (checkMapCollision(this.x, sy, this.width, this.height) &&
                checkTankCollision(this, this.x, sy)) {
                this.y = sy;
            }
        }
    }

    slideToGrid() {
        // 只沿移动方向单轴滑动，始终向前（不后退），避免反向跳动
        if (this.dir === DIR.UP) {
            const ty = Math.floor(this.y / GRID) * GRID;
            if (this.y !== ty) {
                const newY = this.y - this.speed;
                const fy = Math.max(newY, ty);
                if (checkMapCollision(this.x, fy, this.width, this.height) &&
                    checkTankCollision(this, this.x, fy)) {
                    this.y = fy;
                }
            }
        } else if (this.dir === DIR.DOWN) {
            const ty = Math.ceil(this.y / GRID) * GRID;
            if (this.y !== ty) {
                const newY = this.y + this.speed;
                const fy = Math.min(newY, ty);
                if (checkMapCollision(this.x, fy, this.width, this.height) &&
                    checkTankCollision(this, this.x, fy)) {
                    this.y = fy;
                }
            }
        } else if (this.dir === DIR.LEFT) {
            const tx = Math.floor(this.x / GRID) * GRID;
            if (this.x !== tx) {
                const newX = this.x - this.speed;
                const fx = Math.max(newX, tx);
                if (checkMapCollision(fx, this.y, this.width, this.height) &&
                    checkTankCollision(this, fx, this.y)) {
                    this.x = fx;
                }
            }
        } else if (this.dir === DIR.RIGHT) {
            const tx = Math.ceil(this.x / GRID) * GRID;
            if (this.x !== tx) {
                const newX = this.x + this.speed;
                const fx = Math.min(newX, tx);
                if (checkMapCollision(fx, this.y, this.width, this.height) &&
                    checkTankCollision(this, fx, this.y)) {
                    this.x = fx;
                }
            }
        }
    }

    move() {
        if (!this.alive || !this.moving) return;
        let nx = this.x, ny = this.y;
        const step = this.speed;
        if (this.dir === DIR.UP) ny -= step;
        else if (this.dir === DIR.RIGHT) nx += step;
        else if (this.dir === DIR.DOWN) ny += step;
        else if (this.dir === DIR.LEFT) nx -= step;

        // 边界检测 - 坦克必须完全在画布内
        if (nx < 0 || ny < 0 || nx + this.width > CANVAS_W || ny + this.height > CANVAS_H) return;

        // 地图碰撞检测
        if (!checkMapCollision(nx, ny, this.width, this.height)) return;

        // 坦克间碰撞检测
        if (!checkTankCollision(this, nx, ny)) return;

        this.x = nx;
        this.y = ny;
    }

    shoot() {
        if (!this.alive || this.shootCooldown > 0) return;
        const activeBullets = bullets.filter(b => b.alive && b.owner === this).length;
        if (activeBullets >= 2) return;
        this.shootCooldown = this.isPlayer ? 15 : 45;
        let bx, by;
        const halfBullet = BULLET_SIZE / 2;
        const halfTank = TANK_SIZE / 2;
        if (this.dir === DIR.UP) {
            bx = this.x + halfTank - halfBullet;
            by = this.y - BULLET_SIZE;
        } else if (this.dir === DIR.RIGHT) {
            bx = this.x + this.width;
            by = this.y + halfTank - halfBullet;
        } else if (this.dir === DIR.DOWN) {
            bx = this.x + halfTank - halfBullet;
            by = this.y + this.height;
        } else if (this.dir === DIR.LEFT) {
            bx = this.x - BULLET_SIZE;
            by = this.y + halfTank - halfBullet;
        }
        const bullet = new Bullet(bx, by, this.dir, this.isPlayer);
        bullet.owner = this;
        bullets.push(bullet);
    }

    draw(ctx) {
        if (!this.alive) return;
        if (this.invincible > 0 && this.blinkTimer % 8 < 4) return;

        const img = this.getImage();
        if (img) {
            ctx.drawImage(img, Math.floor(this.x), Math.floor(this.y), TANK_SIZE, TANK_SIZE);
        } else {
            ctx.fillStyle = this.isPlayer ? '#fc6' : '#c44';
            ctx.fillRect(Math.floor(this.x), Math.floor(this.y), this.width, this.height);
        }
    }
}
