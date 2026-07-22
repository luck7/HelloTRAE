"use strict";
/// <reference path="00-constants.ts" />
/// <reference path="01-images.ts" />
/// <reference path="08-game.ts" />
window.addEventListener('keydown', (e) => {
    keys[e.key.toLowerCase()] = true;
    if (['arrowup', 'arrowdown', 'arrowleft', 'arrowright', ' '].includes(e.key.toLowerCase())) {
        e.preventDefault();
    }
    if (e.key.toLowerCase() === 'p' && gameState === 'playing') {
        paused = !paused;
    }
});
window.addEventListener('keyup', (e) => {
    keys[e.key.toLowerCase()] = false;
});
window.onload = () => {
    const canvasEl = document.getElementById('gameCanvas');
    if (canvasEl) {
        canvas = canvasEl;
        const ctxEl = canvas.getContext('2d');
        if (ctxEl) {
            ctx = ctxEl;
            ctx.imageSmoothingEnabled = false;
        }
    }
    loadImages().then(() => {
        console.log('Images loaded');
    });
};
//# sourceMappingURL=10-main.js.map