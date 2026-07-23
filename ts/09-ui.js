"use strict";
/// <reference path="00-constants.ts" />
/// <reference path="01-images.ts" />
/// <reference path="05-tank.ts" />
/// <reference path="06-map.ts" />
/// <reference path="08-game.ts" />
function updateUI() {
    const scoreEl = document.getElementById('scoreDisplay');
    if (scoreEl)
        scoreEl.textContent = String(score);
    const stageEl = document.getElementById('stageDisplay');
    if (stageEl)
        stageEl.textContent = String(stage);
    const livesEl = document.getElementById('livesDisplay');
    if (livesEl) {
        livesEl.innerHTML = '';
        for (let i = 0; i < lives; i++) {
            const img = document.createElement('img');
            img.src = IMAGE_SRC.playerUp;
            img.className = 'life-icon';
            livesEl.appendChild(img);
        }
    }
    const enemyEl = document.getElementById('enemyCount');
    if (enemyEl) {
        enemyEl.innerHTML = '';
        const remaining = totalEnemies - spawnedEnemies + enemies.filter(e => e.alive).length;
        for (let i = 0; i < remaining; i++) {
            const div = document.createElement('div');
            div.className = 'enemy-icon';
            enemyEl.appendChild(div);
        }
    }
}
function startGame() {
    const startScreen = document.getElementById('startScreen');
    if (startScreen)
        startScreen.classList.add('hidden');
    gameState = 'playing';
    resetGame();
    gameLoop();
}
function resetGame() {
    score = 0;
    lives = 3;
    stage = 1;
    gameOverDelay = 0;
    resetStage();
}
function resetStage() {
    initMap();
    player = new Tank(4 * TILE, 12 * TILE, DIR.UP, true);
    enemies = [];
    bullets = [];
    explosions = [];
    spawnedEnemies = 0;
    spawnTimer = 0;
    baseAlive = true;
    totalEnemies = 8 + stage * 2;
    updateUI();
}
function gameOver(reason) {
    gameState = 'gameover';
    const endReasonEl = document.getElementById('endReason');
    if (endReasonEl)
        endReasonEl.textContent = reason;
    const finalScoreEl = document.getElementById('finalScore');
    if (finalScoreEl)
        finalScoreEl.textContent = String(score);
    const gameOverScreen = document.getElementById('gameOverScreen');
    if (gameOverScreen)
        gameOverScreen.classList.remove('hidden');
}
function restartGame() {
    const gameOverScreen = document.getElementById('gameOverScreen');
    if (gameOverScreen)
        gameOverScreen.classList.add('hidden');
    gameState = 'playing';
    resetGame();
}
function stageComplete() {
    gameState = 'stageTransition';
    stage++;
    const stageNumEl = document.getElementById('stageNum');
    if (stageNumEl)
        stageNumEl.textContent = String(stage);
    const stageScreen = document.getElementById('stageScreen');
    if (stageScreen)
        stageScreen.classList.remove('hidden');
    setTimeout(() => {
        const stageScreen2 = document.getElementById('stageScreen');
        if (stageScreen2)
            stageScreen2.classList.add('hidden');
        resetStage();
        gameState = 'playing';
    }, 2000);
}
//# sourceMappingURL=09-ui.js.map