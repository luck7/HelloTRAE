import { loadImages } from './images.js';
import { game, setCanvas } from './gameState.js';
import { startGame, restartGame } from './ui.js';
window.addEventListener('keydown', (e) => {
    game.keys[e.key.toLowerCase()] = true;
    if (['arrowup', 'arrowdown', 'arrowleft', 'arrowright', ' '].includes(e.key.toLowerCase())) {
        e.preventDefault();
    }
    if (e.key.toLowerCase() === 'p' && game.gameState === 'playing') {
        game.paused = !game.paused;
    }
});
window.addEventListener('keyup', (e) => {
    game.keys[e.key.toLowerCase()] = false;
});
window.startGame = startGame;
window.restartGame = restartGame;
window.onload = () => {
    const canvasEl = document.getElementById('gameCanvas');
    if (canvasEl) {
        const ctxEl = canvasEl.getContext('2d');
        if (ctxEl) {
            setCanvas(canvasEl, ctxEl);
            ctxEl.imageSmoothingEnabled = false;
        }
    }
    const startBtn = document.getElementById('startBtn');
    if (startBtn) {
        startBtn.addEventListener('click', startGame);
    }
    const restartBtn = document.getElementById('restartBtn');
    if (restartBtn) {
        restartBtn.addEventListener('click', restartGame);
    }
    loadImages().then(() => {
        console.log('Images loaded');
    });
};
//# sourceMappingURL=main.js.map