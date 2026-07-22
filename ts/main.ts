import { loadImages } from './images.js';
import { game, setCanvas } from './gameState.js';
import { startGame, restartGame } from './ui.js';

window.addEventListener('keydown', (e: KeyboardEvent) => {
    game.keys[e.key.toLowerCase()] = true;
    if (['arrowup', 'arrowdown', 'arrowleft', 'arrowright', ' '].includes(e.key.toLowerCase())) {
        e.preventDefault();
    }
    if (e.key.toLowerCase() === 'p' && game.gameState === 'playing') {
        game.paused = !game.paused;
    }
});

window.addEventListener('keyup', (e: KeyboardEvent) => {
    game.keys[e.key.toLowerCase()] = false;
});

(window as any).startGame = startGame;
(window as any).restartGame = restartGame;

window.onload = () => {
    const canvasEl: HTMLCanvasElement | null = document.getElementById('gameCanvas') as HTMLCanvasElement | null;
    if (canvasEl) {
        const ctxEl: CanvasRenderingContext2D | null = canvasEl.getContext('2d');
        if (ctxEl) {
            setCanvas(canvasEl, ctxEl);
            ctxEl.imageSmoothingEnabled = false;
        }
    }

    const startBtn: HTMLElement | null = document.getElementById('startBtn');
    if (startBtn) {
        startBtn.addEventListener('click', startGame);
    }

    const restartBtn: HTMLElement | null = document.getElementById('restartBtn');
    if (restartBtn) {
        restartBtn.addEventListener('click', restartGame);
    }

    loadImages().then(() => {
        console.log('Images loaded');
    });
};
