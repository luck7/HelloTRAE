// ==================== UI 控制 ====================
function updateUI() {
    document.getElementById('scoreDisplay').textContent = score;
    document.getElementById('stageDisplay').textContent = stage;

    const livesEl = document.getElementById('livesDisplay');
    livesEl.innerHTML = '';
    for (let i = 0; i < lives; i++) {
        const img = document.createElement('img');
        img.src = IMAGE_SRC.playerUp;
        img.className = 'life-icon';
        livesEl.appendChild(img);
    }

    const enemyEl = document.getElementById('enemyCount');
    enemyEl.innerHTML = '';
    const remaining = totalEnemies - spawnedEnemies + enemies.filter(e => e.alive).length;
    for (let i = 0; i < remaining; i++) {
        const div = document.createElement('div');
        div.className = 'enemy-icon';
        enemyEl.appendChild(div);
    }
}

function startGame() {
    document.getElementById('startScreen').classList.add('hidden');
    gameState = 'playing';
    resetGame();
    gameLoop();
}

function resetGame() {
    score = 0;
    lives = 3;
    stage = 1;
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
    document.getElementById('endReason').textContent = reason;
    document.getElementById('finalScore').textContent = score;
    document.getElementById('gameOverScreen').classList.remove('hidden');
}

function restartGame() {
    document.getElementById('gameOverScreen').classList.add('hidden');
    gameState = 'playing';
    resetGame();
}

function stageComplete() {
    gameState = 'stageTransition';
    stage++;
    document.getElementById('stageNum').textContent = stage;
    document.getElementById('stageScreen').classList.remove('hidden');
    setTimeout(() => {
        document.getElementById('stageScreen').classList.add('hidden');
        resetStage();
        gameState = 'playing';
    }, 2000);
}
