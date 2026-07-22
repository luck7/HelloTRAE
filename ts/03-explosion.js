"use strict";
/// <reference path="00-constants.ts" />
/// <reference path="01-images.ts" />
class Explosion {
    constructor(x, y, size = 'normal') {
        this.x = x;
        this.y = y;
        this.size = size;
        this.frame = 0;
        this.maxFrame = 8;
        this.alive = true;
        this.timer = 0;
    }
    update() {
        this.timer++;
        if (this.timer > 4) {
            this.timer = 0;
            this.frame++;
            if (this.frame >= this.maxFrame)
                this.alive = false;
        }
    }
    draw(ctx) {
        if (!this.alive)
            return;
        const img = IMAGES.explosion;
        const scale = this.size === 'big' ? 2 : (this.size === 'small' ? 0.6 : 1);
        const progress = this.frame / this.maxFrame;
        const alpha = 1 - progress;
        const drawSize = TILE * scale;
        if (img && this.frame < 3) {
            ctx.globalAlpha = alpha;
            ctx.drawImage(img, this.x - (scale - 1) * TILE / 2, this.y - (scale - 1) * TILE / 2, drawSize, drawSize);
            ctx.globalAlpha = 1;
        }
        else {
            const cx = this.x + TILE / 2;
            const cy = this.y + TILE / 2;
            const radius = (8 + this.frame * 4) * scale;
            ctx.fillStyle = `rgba(255, ${120 + this.frame * 15}, 0, ${alpha})`;
            ctx.beginPath();
            ctx.arc(cx, cy, radius, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = `rgba(255, 200, 0, ${alpha * 0.5})`;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(cx, cy, radius + 4, 0, Math.PI * 2);
            ctx.stroke();
        }
    }
}
//# sourceMappingURL=03-explosion.js.map