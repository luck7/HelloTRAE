// ==================== 游戏状态 ====================
let canvas, ctx;
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

// ==================== 游戏逻辑 ====================
function respawnPlayer() {
    if (lives > 0) {
        // 玩家出生在左下角
        player = new Tank(4 * TILE, 12 * TILE, DIR.UP, true);
    }
}

function spawnEnemy() {
    if (spawnedEnemies >= totalEnemies) return;
    // 三个出生点：左上、中上、右上
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
        if (!e.alive) continue;
        e.moving = true;
        const oldDir = e.dir;

        if (e.turnCooldown <= 0) {
            // 低概率随机转向，且不会直接掉头（除非被堵住）
            if (Math.random() < 0.008) {
                const opposite = (e.dir + 2) % 4;
                const choices = [0, 1, 2, 3].filter(d => d !== opposite);
                e.dir = choices[Math.floor(Math.random() * choices.length)];
            }

            // 追踪玩家概率降低，且避免掉头
            if (player && player.alive && Math.random() < 0.06) {
                const dx = player.x - e.x;
                const dy = player.y - e.y;
                const opposite = (e.dir + 2) % 4;
                let newDir = e.dir;
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

        // 撞墙时换方向（避免卡住）
        if (e.x === e._lastX && e.y === e._lastY) {
            if (e.turnCooldown <= 0) {
                const opposite = (e.dir + 2) % 4;
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
        if (player) player.moving = false;
        if (gameOverDelay <= 0) {
            gameOver('Base destroyed!');
        }
        return;
    }
    if (gameState !== 'playing' || paused) return;

    spawnTimer++;
    if (spawnTimer > 200) {
        spawnTimer = 0;
        if (enemies.filter(e => e.alive).length < 3) {
            spawnEnemy();
        }
    }

    if (player && player.alive) {
        player.moving = false;
        if (keys['w'] || keys['arrowup']) { player.dir = DIR.UP; player.moving = true; }
        else if (keys['s'] || keys['arrowdown']) { player.dir = DIR.DOWN; player.moving = true; }
        else if (keys['a'] || keys['arrowleft']) { player.dir = DIR.LEFT; player.moving = true; }
        else if (keys['d'] || keys['arrowright']) { player.dir = DIR.RIGHT; player.moving = true; }

        if (player.moving) {
            player.move();
        } else {
            player.slideToGrid();
        }
        player.update();
    }

    if (keys[' '] && player && player.alive) {
        player.shoot();
    }

    updateEnemies();
    for (const e of enemies) e.update();

    for (const b of bullets) b.update();
    checkBulletBulletCollision();
    bullets = bullets.filter(b => b.alive);

    for (const ex of explosions) ex.update();
    explosions = explosions.filter(ex => ex.alive);

    enemies = enemies.filter(e => e.alive);

    if (spawnedEnemies >= totalEnemies && enemies.length === 0) {
        stageComplete();
    }
}

function draw() {
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);

    // 绘制地图底层（砖、钢、水）
    for (let y = 0; y < MAP_H; y++) {
        for (let x = 0; x < MAP_W; x++) {
            const tile = map[y][x];
            const tx = x * TILE, ty = y * TILE;
            if (tile === TERRAIN.BRICK && IMAGES.brick) {
                ctx.drawImage(IMAGES.brick, tx, ty, TILE, TILE);
            } else if (tile === TERRAIN.STEEL && IMAGES.steel) {
                ctx.drawImage(IMAGES.steel, tx, ty, TILE, TILE);
            } else if (tile === TERRAIN.WATER && IMAGES.water) {
                ctx.drawImage(IMAGES.water, tx, ty, TILE, TILE);
            }
        }
    }

    // 绘制基地（单个32x32图片）
    if (baseAlive) {
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

    // 绘制坦克
    for (const e of enemies) e.draw(ctx);
    if (player) player.draw(ctx);

    // 绘制子弹
    for (const b of bullets) b.draw(ctx);

    // 绘制爆炸
    for (const ex of explosions) ex.draw(ctx);

    // 绘制草地（上层，遮挡坦克）
    for (let y = 0; y < MAP_H; y++) {
        for (let x = 0; x < MAP_W; x++) {
            if (map[y][x] === TERRAIN.GRASS && IMAGES.grass) {
                ctx.drawImage(IMAGES.grass, x * TILE, y * TILE, TILE, TILE);
            }
        }
    }

    // 暂停提示
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
