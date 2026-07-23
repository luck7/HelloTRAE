import { TILE, DIR } from './constants.js';
import { IMAGE_SRC } from './images.js';
import { Tank } from './tank.js';
import { initMap } from './map.js';
import { game } from './gameState.js';
import { gameLoop } from './game.js';

export function updateUI(): void {
    const scoreEl: HTMLElement | null = document.getElementById('scoreDisplay');
    if (scoreEl) scoreEl.textContent = String(game.score);
    const stageEl: HTMLElement | null = document.getElementById('stageDisplay');
    if (stageEl) stageEl.textContent = String(game.stage);

    const livesEl: HTMLElement | null = document.getElementById('livesDisplay');
    if (livesEl) {
        livesEl.innerHTML = '';
        for (let i: number = 0; i < game.lives; i++) {
            const img: HTMLImageElement = document.createElement('img');
            img.src = IMAGE_SRC.playerUp;
            img.className = 'life-icon';
            livesEl.appendChild(img);
        }
    }

    const enemyEl: HTMLElement | null = document.getElementById('enemyCount');
    if (enemyEl) {
        enemyEl.innerHTML = '';
        const remaining: number = game.totalEnemies - game.spawnedEnemies + game.enemies.filter(e => e.alive).length;
        for (let i: number = 0; i < remaining; i++) {
            const div: HTMLDivElement = document.createElement('div');
            div.className = 'enemy-icon';
            enemyEl.appendChild(div);
        }
    }
}

export function startGame(): void {
    const startScreen: HTMLElement | null = document.getElementById('startScreen');
    if (startScreen) startScreen.classList.add('hidden');
    game.gameState = 'playing';
    resetGame();
    gameLoop();
}

export function resetGame(): void {
    game.score = 0;
    game.lives = 3;
    game.stage = 1;
    game.gameOverDelay = 0;
    resetStage();
}

export function resetStage(): void {
    initMap();
    game.player = new Tank(4 * TILE, 12 * TILE, DIR.UP, true);
    game.enemies = [];
    game.bullets = [];
    game.explosions = [];
    game.spawnedEnemies = 0;
    game.spawnTimer = 0;
    game.baseAlive = true;
    game.totalEnemies = 8 + game.stage * 2;
    updateUI();
}

export function gameOver(reason: string): void {
    game.gameState = 'gameover';
    const endReasonEl: HTMLElement | null = document.getElementById('endReason');
    if (endReasonEl) endReasonEl.textContent = reason;
    const finalScoreEl: HTMLElement | null = document.getElementById('finalScore');
    if (finalScoreEl) finalScoreEl.textContent = String(game.score);
    const gameOverScreen: HTMLElement | null = document.getElementById('gameOverScreen');
    if (gameOverScreen) gameOverScreen.classList.remove('hidden');
}

export function restartGame(): void {
    const gameOverScreen: HTMLElement | null = document.getElementById('gameOverScreen');
    if (gameOverScreen) gameOverScreen.classList.add('hidden');
    game.gameState = 'playing';
    resetGame();
}

export function stageComplete(): void {
    game.gameState = 'stageTransition';
    game.stage++;
    const stageNumEl: HTMLElement | null = document.getElementById('stageNum');
    if (stageNumEl) stageNumEl.textContent = String(game.stage);
    const stageScreen: HTMLElement | null = document.getElementById('stageScreen');
    if (stageScreen) stageScreen.classList.remove('hidden');
    setTimeout(() => {
        const stageScreen2: HTMLElement | null = document.getElementById('stageScreen');
        if (stageScreen2) stageScreen2.classList.add('hidden');
        resetStage();
        game.gameState = 'playing';
    }, 2000);
}

export function respawnPlayer(): void {
    if (game.lives > 0) {
        game.player = new Tank(4 * TILE, 12 * TILE, DIR.UP, true);
    }
}
